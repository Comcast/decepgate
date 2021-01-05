
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <sys/wait.h>
#include <sys/socket.h>
#include <signal.h>
#include <ctype.h>          
#include <arpa/inet.h>
#include <netdb.h>
#include <unistd.h>  
#include <fcntl.h>
#include <sys/time.h>
#include <sys/stat.h>

#define PORT 8082
#define BACKLOG 5
#define LENGTH 8192


/*
---------------------------------------------------------------------
TCP based file streaming,used to receive files transferred remotely
---------------------------------------------------------------------
*/

//File reciever with timeout
int receive_timeout(int s ,FILE *fr, int timeout)
{
        int size_recv , total_size= 0;
        struct timeval begin , now;
        char chunk[LENGTH];
        double timediff;

        //make socket non blocking
        fcntl(s, F_SETFL, O_NONBLOCK);

        //beginning time
        gettimeofday(&begin , NULL);

        while(1)
        {
                gettimeofday(&now , NULL);

                //time elapsed in seconds
                timediff = (now.tv_sec - begin.tv_sec) + 1e-6 * (now.tv_usec - begin.tv_usec);

                //if you got some data, then break after timeout
                if( total_size > 0 && timediff > timeout )
                {
                        break;
                }

                //if you got no data at all, wait a little longer, twice the timeout
                else if( timediff > timeout*2)
                {
                        break;
                }

                memset(chunk ,0 , LENGTH);      //clear the variable
                if((size_recv =  recv(s , chunk , LENGTH , 0) ) < 0)
                {
                        //if nothing was received then we want to wait a little before trying again, 0.1 seconds
                        usleep(100000);

                }
		else
                {
                        total_size += size_recv;
                        int write_sz = fwrite(chunk, sizeof(char),size_recv, fr);
                        if(write_sz < size_recv)
                        {
                                perror("File write failed on server.\n");
                        }

                        //reset beginning time
                        gettimeofday(&begin , NULL);
                }
        }

        return total_size;
}


void error(const char *msg)
{
	perror(msg);
	exit(1);
}

int main (int argc, char **argv)
{
	/* Defining Variables */
	int sockfd; 
	int nsockfd; 
	int sin_size; 
	struct sockaddr_in addr_local; /* client addr */
	struct sockaddr_in addr_remote; /* server addr */
	int opt=1;
	int port=PORT;

	while ((opt = getopt (argc, argv, "p:")) != -1)
	{
		switch (opt)
		{
			case 'p':
				printf("port, -p %s:", optarg);
				port = atoi(optarg);
				break;
			default:
				printf("Unkown argument:%s", optarg);
		}
	}
	char config_suffix[] = "/tmp/honeyd_tmp";
        char *full_path = malloc(strlen(config_suffix) + 1);
        strcpy(full_path, config_suffix);

	if(mkdir(full_path, S_IRWXU|S_IRWXO) != 0)
        {
                if(errno != EEXIST)
                {
                        perror("Error: Could not create /tmp/honeyd_tmp/");
                }
        }

	/* Get the Socket file descriptor */
	if((sockfd = socket(AF_INET, SOCK_STREAM, 0)) == -1 )
	{
		fprintf(stderr, "ERROR: Failed to obtain Socket Descriptor. (errno = %d)\n", errno);
		exit(1);
	}
	else 
		printf("[Server] Obtaining socket descriptor successfully.\n");

	/* Fill the client socket address struct */
	addr_local.sin_family = AF_INET; // Protocol Family
	addr_local.sin_port = htons(port); // Port number
	addr_local.sin_addr.s_addr = INADDR_ANY; // AutoFill local address
	bzero(&(addr_local.sin_zero), 8); // Flush the rest of struct

	/* Bind a special Port */
	if( bind(sockfd, (struct sockaddr*)&addr_local, sizeof(struct sockaddr)) == -1 )
	{
		fprintf(stderr, "ERROR: Failed to bind Port. (errno = %d)\n", errno);
		exit(1);
	}
	else 
		printf("[Server] Binded tcp port %d in addr 127.0.0.1 sucessfully.\n",port);

	/* Listen remote connect/calling */
	if(listen(sockfd,BACKLOG) == -1)
	{
		fprintf(stderr, "ERROR: Failed to listen Port. (errno = %d)\n", errno);
		exit(1);
	}
	else
		printf ("[Server] Listening the port %d successfully.\n", port);

	int success = 1;
	while(success)
	{
		sin_size = sizeof(struct sockaddr_in);

		/* Wait a connection, and obtain a new socket file despriptor for single connection */
		if ((nsockfd = accept(sockfd, (struct sockaddr *)&addr_remote,  (socklen_t *) &sin_size)) == -1) 
		{
			fprintf(stderr, "ERROR: Obtaining new Socket Despcritor. (errno = %d)\n", errno);
			exit(1);
		}
		else 
			printf("[Server] Server has got connected from %s.\n", inet_ntoa(addr_remote.sin_addr));


		/*Receive File from Client */
		char* fr_name = "/tmp/honeyd_tmp/demo.conf";
		FILE *fr = fopen(fr_name, "w");
		if(fr == NULL)
			printf("File %s Cannot be opened file on server.\n", fr_name);
		else
		{
			int total_recv = receive_timeout(nsockfd,fr,4);
                        printf("Total file size %d\n",total_recv);

			if(total_recv < 0)
			{
				if (errno == EAGAIN)
				{
					printf("recv() timed out.\n");
				}
				else
				{
					fprintf(stderr, "recv() failed due to errno = %d\n", errno);
					exit(1);
				}
			}
			printf("Ok received from client!\n");
			fclose(fr); 
		}


		success = 1;
		close(nsockfd); //close the socket
		printf("[Server] Connection with Client closed. Server will wait now...\n");
		while(waitpid(-1, NULL, WNOHANG) > 0);
	}
}

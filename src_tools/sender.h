#include <stdio.h>
#include <sys/socket.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/types.h>
#include <stdarg.h>



/* 
------------------------------------------------------------
UDP BASED REMOTE LOG STREAMING MACROS WITH THREE LEVELS
	*H_LOG_ERROR - to log error messages
	*H_LOG_WARN  - to log warning messages
	*H_LOG_INFO  - to log ncessary info
-----------------------------------------------------------
			
*/
char msg[1024];

//H_LOG_ERROR -  to log error messages
#define H_LOG_ERROR(format,...) {\
snprintf(msg,sizeof(msg),"HONEYD [ERROR] " format, ##__VA_ARGS__);\
struct sockaddr_in clientAddr;\
int sockfd, clientLen;\
if((sockfd=socket(AF_INET, SOCK_DGRAM, 0)) == -1)\
        {\
                perror("socket failed:");\
                return;\
        }\
memset((char *)&clientAddr, 0, sizeof(clientAddr));\
clientAddr.sin_family           = AF_INET;\
clientAddr.sin_port                 = htons(DEFAULT_LISTEN_PORT);\
clientAddr.sin_addr.s_addr      = inet_addr(DEFAULT_LISTEN_IP);\
clientLen = sizeof(clientAddr);\
if (connect(sockfd, (struct sockaddr *)&clientAddr,clientLen) < 0) \
    { \
        perror("\nConnection Failed \n"); \
        return;\
    } \
  send(sockfd ,msg , strlen(msg) , 0 ); \
 close(sockfd);\
}
//H_LOG_WARN  - to log warning messages
#define H_LOG_WARN(format,...) {\
sprintf(msg,"HONEYD [WARN] " format, ##__VA_ARGS__);\
struct sockaddr_in clientAddr;\
int sockfd, clientLen;\
if((sockfd=socket(AF_INET, SOCK_DGRAM, 0)) == -1)\
        {\
                perror("socket failed:");\
                return;\
        }\
memset((char *)&clientAddr, 0, sizeof(clientAddr));\
clientAddr.sin_family           = AF_INET;\
clientAddr.sin_port                 = htons(DEFAULT_LISTEN_PORT);\
clientAddr.sin_addr.s_addr      = inet_addr(DEFAULT_LISTEN_IP);\
clientLen = sizeof(clientAddr);\
if (connect(sockfd, (struct sockaddr *)&clientAddr,clientLen) < 0) \
    { \
        perror("\nConnection Failed \n"); \
        return;\
    } \
send(sockfd ,msg , strlen(msg) , 0 ); \
close(sockfd);\
}

//H_LOG_INFO  - to log ncessary info
#define H_LOG_INFO(format,...) {\
sprintf(msg,"HONEYD [INFO] " format, ##__VA_ARGS__);\
struct sockaddr_in clientAddr;\
int sockfd, clientLen;\
if((sockfd=socket(AF_INET, SOCK_DGRAM, 0)) == -1)\
        {\
                perror("socket failed:");\
                return;\
        }\
memset((char *)&clientAddr, 0, sizeof(clientAddr));\
clientAddr.sin_family           = AF_INET;\
clientAddr.sin_port                 = htons(DEFAULT_LISTEN_PORT);\
clientAddr.sin_addr.s_addr      = inet_addr(DEFAULT_LISTEN_IP);\
clientLen = sizeof(clientAddr);\
if (connect(sockfd, (struct sockaddr *)&clientAddr,clientLen) < 0) \
    { \
        perror("\nConnection Failed \n"); \
	return;\
    } \
  send(sockfd ,msg , strlen(msg) , 0 ); \
 close(sockfd);\
}


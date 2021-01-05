HEADERS = sender.h

default: conf_recv

conf_recv.o: conf_recv.c   $(HEADERS)
	gcc -c conf_recv.c -o conf_recv.o

conf_recv: conf_recv.o
	gcc conf_recv.o -o conf_recv


clean:
	-rm -f conf_recv.o
	-rm -f conf_recv

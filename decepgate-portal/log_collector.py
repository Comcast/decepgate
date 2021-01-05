'''Log collector for Decepgate'''
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys
import argparse

file_name=' '

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        ''' WatchDog event Handler for monitoring the logs collected and clean the content for GUI'''

        feed=""
        filePath=dir_path+'/'+file_name

        with open(filePath,'r') as f:
            lines = f.readlines()
        feed=lines[-1].split()
        f.close()

        buf = "%s,%s,%s,%s,%s,%s" % (feed[5],feed[6],feed[8],feed[10],feed[9],feed[11])

        '''Read the file name to write the parsed data '''
        with open("config.txt",'r+') as ft:
            ft.seek(0)
            i_data=ft.read()
        ft.close()

        '''Write the Parsed Data for GUI '''
        with open(i_data,'a+') as fp:
             fp.write(buf)
             fp.write("\n")
        fp.close()

if __name__ == '__main__':
    ''' Map the command line arguments '''
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file_name",
                        nargs='?',help="Specify the name of a log file ")
    parser.add_argument("-d", "--dir_path",
                        nargs='?',
                        help="Specify the directory to watch")

    args = parser.parse_args()

    if not args.file_name:
        printf("Filename missing")
        exit()
    else:
        file_name=args.file_name
    if not args.dir_path:
        printf("Specify directory path to watch")
        exit()
    else:
        dir_path=args.dir_path
    
    '''Read the file name to write the header '''
    with open("config.txt",'r+') as ft:
        ft.seek(0)
        i_data=ft.read().strip()
    ft.close()
 
    ''' Map the header for writing parsed data '''
    fp = open(i_data,"a+")
    fp.seek(0)
    i_data=fp.read()
    if len(i_data) == 0:
         fp.write("TimeStamp,Protocol,Src_Ip,Dest_Ip,Src_Port,Dest_Port\n")
    fp.close()

    event_handler = MyHandler()
    observer = Observer()
    ''' Initiate the watchdog handler '''
    observer.schedule(event_handler, path=dir_path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

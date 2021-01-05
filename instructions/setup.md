DECEPGATE SETUP
============

### Building the honeyd for RDK platform,
- Please refer modifications.md for upgrading honeyd to run on embedded devices
- Using the decepgate.bb yocto recipe , build the image and flash into the RDK devices
- After flashing the image all required services to run honeyd will be ready

### prerequisite for dashboard setup
- pip3 install dash (0.37.0) ,dash-core-components (0.43.1), Flask (1.1.2), dash-html-components (0.13.5),plotly (4.3.0),matplotlib (2.1.1),pandas (0.24.2),watchdog (0.9.0)

### Remote Server
- Used syslog to collect logs remotely.
- In syslog config  enabled udp protocol with port 514 to receive logs across.
		`module(load="imudp"),input(type="imudp" port="514")`
- On remote server run `log_collector.py` for listening to logs through syslog and clean it for GUI.
```python3 log_collector.py --dir_path " directory to watch "--file_name "log_file"```

  This will prompt you for two inputs:
  1. --dir_path
    	* Directory path to listen for logs received.
  2. --file-name
    	* File name of the logs  collected.
- For dashboard hosted using flask run  decepgate_ui.py
` python3 decepgate_ui.py --ip host ip"--port "listening port"`

  Two optional inputs,
  1. --ip
        * IP where dashboard is hosted.
  2. --port
        * Listening port of the dashboard.
- Required files for dashboard is  config.txt & config_pre.txt for fault_tolerance.

 	These two files usage
	 1. config.txt,
 		- To get file name of the parsed log which is gui input.
	 2. config_pre.txt,
 		- To preserve the file name of parsed log, inorder to maintaina state of each config file.


---
### Gateway
- To receive file from remote server to gateway, run
` conf_recv -p 8083 `


	* -p is listening port for for file reciver
- Used inotify library and created a package to listen for file received in a directory in gateway and did swapping and starting services with config files.
	```./inotify_decepgate  /tmp/honeyd_tmp /tmp/script.sh 1  *.conf```
	
  Usage,
  	1. ./tmp/honeyd_tmp
       	    - directory where inotify listening
   	2. ./tmp/script.sh
            - to switch config files when new file received and starting honeyd with new configuration.
	3. .conf
       	    - listen for .conf extension files
  
- For streaming logs need to integrate the log macros used in `sender.h` in required places.

##### NOTE: 
	- For injecting honeyd config files to gateway, use dashboard to broadcast.
	- We referred inotify sample codes and customized according to our need. So please refer open source inotify packages to use this services


### Files Description
| File Name | Description |
| --- | --- |
| src_tools/conf_recv.c |  To receive file from remote server to gateway  |
| src_tools/sender.h | For sending logs to remote server |
| src_tools/Makefile | Sample Makefile(For testing compilation locally,but for actual use need to add these modules to honeyd |
| decepgate-portal/log_collector.py | Used for cleaning logs collected in remote server and feed that into GUI |
| decepgate-portal/decepgate_ui.py  | Live dashboard for uploading and broadcasting config iles to gateway and also to see the live traffic from gateway |
| decepgate-portal/config.txt | To store the filename of honeyd traffic based on config filename(used for fault tolerence mechanism |
| decepgate-portal/config_pre.txt | Used to switch traffic based on config file name (fault tolenrence mechanism) |
| yocto-recipe/honeyd.bb | Yocto recipe used for building honeyd in RDK platform  |
| service-scripts/config_receiver.service | systemd service for file reciever |
| service-scripts/inotify-decepgate.service | systemd service for directory notifier |
| service-scripts/start-honeyd.service | systemd service for honeyd application |
| service-scripts/start-honeyd.timer | Service boot timer |
| service-scripts/script.sh | Script used by inotify to perform actions to swap config files and started honeyd services |
| service-scripts/start_honeyd.sh | small script to start honeyd service |


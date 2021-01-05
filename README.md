# DecepGate
DecepGate helps building Honeypots and Honeynets on devices with limited resources such as gateways and embedded devices. DecepGate also gives the abaility to manage decoys through a full fledge portal. The portal helps to create profiles, deploy decoys, collect logs and visualize them, and reconfigure the decoys. Below, we provide details on the architecture of the DecepGate and its components.

# Overall End-to-End Architecture of DecepGate
<p align="center">
<img src="/images/o_arch.png" width="70%">
</p>

The main elements of DecepGate are as follows:
### User
The user will create config files,design and also do deployments 
### Control Device
The device that the user can access the portal through and manage decoys.
### Portal
A full fledge portal enabling users to manage decoys and reconfigure them
### Host Device
The device that is hosting decoys.

# Internal Architecture of DecepGate
<p align="center">
<img src="/images/i_arch.png" width="60%">
</p>

### About Honeyd 
[Honeyd](http://www.honeyd.org/) is a small daemon that creates virtual hosts on a network and will be running on an Embedded box. The hosts can be configured to run arbitrary services, and their TCP personality can be adapted so that they appear to be running certain
versions of operating systems.  Honeyd enables a single host to claim multiple addresses.

Scanners would be able to interact with the virtual hosts such as pinging the virtual machines, or to traceroute them.
Any type of service on the virtual machine can be simulated according to a simple configuration file. 

### Portal [/decepgate-portal]:
Using this portal, we are able to upload config files in dashboard and inject them into the embedded devices. Once a config file is uploaded, the portal shows the network topology of our honeynet. Then we can broadcast the file to any device where honeyd running. Also whenever someone hit the virtual networks, will start to display Logs,Graphs,Charts in live dashboard.
We are using syslog to collect logs and watchdogs to parse and feed live data from logs received.

### In Device [/service-scripts]:
Whenever config file is injected from the portal remotely, we have config receiver developed running on gateway devices to receive the config file. Once the file received, we use a service named inotify-decepgate developed using intoify watch to listen for a file and start the decepgate using the config file received. Whenever new config file receives, our application will swap the config and start the service with new network topology.

### Changes contributed:
#### Honeyd:
Modified Honeyd Toolchain to build images for Embedded devices. By default they are developed to build on native environment. Enhanced the toolchain to support cross compilation. In some of the embedded boxes, the DecepGate application was not able to capture packets due to the compatibility issue. To resolve this issue, we changed the application interface components, with different event triggering option. Also application callbacks changed to timer.
The config access modified. Removed file based logging and replaced with TCP stream.

#### File Receiver:
TCP-based file receiver developed to receive config file in the box.

#### Inotify-Decepgate:
To listen for config file in the box, used open-close flag. This was used for notifying file change events happening in a directory, based on which appropriate actions will be taken using the scripts to swap config files and start & stop service-scripts.

#### Service-scripts:
Created  multiple systemd services to start applications and dependencies, swap config file, on boot behavior etc.

### Portal hosted remotely:
Here portal developed in Python using Flask and Dash. Using this Portal we can Broadcast a configuration file of DecepGate to the Remote Devices. Used Syslog to receive logs and watchdog package in python to clean the data and send to live dashboard.


# Files Description
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

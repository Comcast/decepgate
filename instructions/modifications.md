### Honeyd for embedded devices

### Changes Required:

#### Changes added for cross compilation in toolchain:
> In Honeyd the build tools are supporting native compilation, basically we need to run on respective platforms to build the package, but to cross compile for different platforms currently the toolchain is getting exited due to code snippet execution, which was supposed to be executed only on native platform.

##### For supporting cross compilation ,to build for different platforms ,need to do change the toolchain,
Under configure.in ,If the target is for cross compilation then,
- Modify the library and header paths ,by default its picking `/usr/ path`
- Corrected `INC and LIB path`, if withval option included.
- Also should skip the sample code execution of each library in toolchain, so modified those to support while running cross compilation.
`HAVEMETHOD needs to be changed for skipping snippet execution wherever exit has been added.`

##### NOTE : 
>Earlier it will execute the small program for each library, which is applicable for only native compilation
Also there is redefinition error in particular arm versions due to the structure user which was part of system headers defined in honeyd application ,so renamed the structure.

#### CHANGES DONE ON SOURCE CODE:
- Replaced new version of fingerprint(removed three finger prints which caused parse issue)
	- Replaced the latest fingerprint version from,
		`<DB Link>` https://svn.nmap.org/nmap/nmap-os-db
- Most of embedded  devices will have  only read access for home directory  ,so in our source code changed the path referring home to /tmp.
```EG:
	char config_suffix[] = "/.config"; 
	char config_suffix[] = "/tmp/.config";
```
- Also application is not able to read most of the  packets ,due to that huge packet drops happening. Reason is due to pcap version compatibilty in embedded devices.
	 -  To fix this compatibilty issue following changes made,
	 		Changed packet reading polling mechanism from  `EV_READ`  to `EV_PERSIST ` (polling mechanism in frequent interval) 
			Reason is our event handler using EV_READ based on packet capture file descriptor, where pcap dispatch used, so in the device the events are not triggering due to packet capture issue in pcap ,so used pcap loop as an alternative to read entire buffer(will do read for entire size),it will behave similar to event persist.
```
        Old Prototype -> pcap_dispatch(inter->if_pcap, -1, if_recv_cb, (u_char *)inter)
        New Prototype-> pcap_loop(inter->if_pcap, -1, if_recv_cb, (u_char *)inter)
```

- Inorder to use new event polling , need to change ,
>Removed libevent timer(evtimer_new) and just used,honeyd_delay_callback with timeout by default -> `honeyd_delay_callback(-1, EV_TIMEOUT,delay)`

- Remove file logging ,as we moved to UDP based remote streaming.
		Use macros in sender .h for remote streaming
		Macros available are,
				H_LOG_ERROR - To log error messages
				H_LOG_WARN - To log warning messages
				H_LOG_INFO   - To log necessary info






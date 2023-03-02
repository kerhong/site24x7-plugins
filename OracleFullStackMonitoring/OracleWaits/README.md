# Oracle Waits Monitoring


                                                                                              
## Prerequisites

- Download and install the latest version of the [Site24x7 Linux agent](https://www.site24x7.com/app/client#/admin/inventory/add-monitor) in the server where you plan to run the plugin. 

- Install cx_Oracle module for python
```
  pip3 install cx_Oracle
```
---


### Plugin Installation  

- Create a directory named "OracleWaits" under the Site24x7 Linux Agent plugin directory: 

		Linux             ->   /opt/site24x7/monagent/plugins/OracleWaits
      
- Download all the files in the "OracleWaits" folder and place it under the "OracleWaits" directory.

		wget https://raw.githubusercontent.com/site24x7/plugins/master/OracleFullStackMonitoring/OracleWaits/OracleWaits.py
		wget https://raw.githubusercontent.com/site24x7/plugins/master/OracleFullStackMonitoring/OracleWaits/OracleWaits.cfg

- Execute the following command in your server to install OracleWaits: 

		pip3 install cx_Oracle

- Execute the below command with appropriate arguments to check for the valid json output:
```
 python3 OracleWaits.py --hostname=<name of the host> --port=<port> --sid=<SID> --username=<USERNAME> --password=<PASSWORD> --oracle_home=<ORACLE_HOME> --tablespace_name=<TABLESPACE_NAME>
 ```

---

### Configurations

- Provide your OracleWaits configurations in OracleWaits.cfg file.
```
    [ORCL]
    hostname=localhost
    port=1521
    sid=<SID>
    username=<USERNAME>
    password=<PASSWORD>
    logs_enabled="False"
    log_type_name =None
    log_file_path=None
    oracle_home=None

```	

The agent will automatically execute the plugin within five minutes and send performance data to the Site24x7 data center.



## Supported Metrics
The following metrics are captured in the OracleWaits Plugin:

- **Free Buffer Waits**

- **Buffer Busy Waits**

- **Latch Free**

- **Library Cache Pin**

- **Library Cache Load Lock**

- **Log Buffer Space**

- **Library Object Reloads Count**

- **Enqueue Waits**

- **DB File Parallel Read**

- **DB File Parallel Write**

- **Control File Sequential Read**

- **Control File Parallel Write**

- **Write Complete Waits**

- **Log File Sync**

- **Sort Segment Request**

- **Direct Path Read**

- **Direct Path Write**

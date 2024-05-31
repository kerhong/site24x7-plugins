#! /usr/bin/python3
import os
import subprocess
import json
import warnings
import urllib.parse
import urllib.request
import shutil
import configparser

warnings.filterwarnings("ignore")
class colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m' 


def multi_config(read_file, write_file):
    try:
        with open(read_file, "r") as f:
            config_details=f.read()
            with open(write_file, "a") as f:
                f.write("\n")
                f.write(config_details)
        return True
    except Exception as e:
        print("    "+str(e))
        return False

def delete_folder(folder_name):
    try:
        shutil.rmtree(folder_name)
        return True
    except Exception as e:
        print("    "+str(e))
        return False

def move_folder(source, destination):
    try:
        os.rename(source, destination)
    except Exception as e:
        print(colors.RED +"    "+str(e)+colors.RESET)
        return False
    return True


def remove_section_from_config(config_file, section_name):
    config = configparser.ConfigParser()
    config.read(config_file)

    if config.has_section(section_name):
        config.remove_section(section_name)
        with open(config_file, 'w') as configfile:
            config.write(configfile)

def check_parse(plugin_name, plugin_dir, plugin_temp_path):

    file_path=plugin_dir+plugin_name+".cfg"
    temp_file_path=plugin_temp_path+plugin_name+"/"+plugin_name+".cfg"
    config = configparser.ConfigParser()
    config.read(file_path)
    sections = config.sections()

    config_temp = configparser.ConfigParser()
    config_temp.read(temp_file_path)
    section_name = config_temp.sections()[0]
    if section_name in sections:
        remove_section_from_config(file_path, section_name)


def move_plugin(plugin_name, plugins_temp_path, agent_plugin_path):
    try:
        if not check_directory(agent_plugin_path):
            print(f"    {agent_plugin_path} Agent Plugins Directory not Present")
            return False
        plugin_dir=agent_plugin_path+plugin_name+"/"
        if not check_directory(plugin_dir):

            if not move_folder(plugins_temp_path+plugin_name, plugin_dir): 
                return False
        else:
            check_parse(plugin_name, plugin_dir, plugins_temp_path)

            if not multi_config(plugins_temp_path+plugin_name+"/"+plugin_name+".cfg",plugin_dir+plugin_name+".cfg"):
                 return False

    except Exception as e:
        print(colors.RED +"    "+str(e)+colors.RESET)
        return False
    return True

def plugin_config_setter(plugin_name, plugins_temp_path, arguments, display_name):
    try:
        full_path=plugins_temp_path+plugin_name+"/"
        config_file_path=full_path+plugin_name+".cfg"

        arguments='\n'.join(arguments.replace("--","").split())
        with open(config_file_path, "w") as f:
            f.write(f"[{display_name}]\n"+arguments)


    except Exception as e:
        print(colors.RED +"    "+str(e)+colors.RESET)
        return False
    return True

def plugin_validator(output):
    try:
        result=json.loads(output.decode())
        if "status" in result:
            if result['status']==0:
                print("    Plugin execution encountered a error")
                if "msg" in result:
                    print(result['msg'])
            return False

    except Exception as e:
        print(colors.RED +"    "+str(e)+colors.RESET)
        return False
    
    return True



def download_file(url, path):
    filename=url.split("/")[-1]
    full_path=path+filename
    urllib.request.urlretrieve(url, full_path)
    response=urllib.request.urlopen(url)
    if response.getcode() == 200 :
        print(colors.GREEN +f"      {filename} Downloaded"+ colors.RESET)
    else:
        print(colors.RED +f"      {filename} Download Failed with response code {str(response.status_code)}"+ colors.RESET)
        return False
    return True

def down_move(plugin_name, plugin_url, plugins_temp_path):
    temp_plugin_path=os.path.join(plugins_temp_path,plugin_name+"/")
    if not check_directory(temp_plugin_path):
        if not make_directory(temp_plugin_path):return False

    py_file_url=plugin_url+"/"+plugin_name+".py"
    cfg_file_url=plugin_url+"/"+plugin_name+".cfg"
    if not download_file(py_file_url, temp_plugin_path):return False
    if not download_file(cfg_file_url, temp_plugin_path):return False
    return True


def execute_command(cmd, need_out=False):
    try:
        if not isinstance(cmd, list):
            cmd=cmd.split()
        
        result=subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print(f"    {cmd} execution failed with return code {result.returncode}")
            print(f"    {str(result.stderr)}")
            return False
        if need_out:
            return result.stdout
        return True
    except Exception as e:
        print(colors.RED +"    "+str(e)+colors.RESET)
        return False


def make_directory(path):
    if not check_directory(path):
        try:
            os.mkdir(path)
            print(f"    {path} directory created.")
        
        except Exception as e:
            print(f"    Unable to create {path} Directory  : {str(e)}")
            return False
    return True


def check_directory(path):
    return os.path.isdir(path)



def input_validate(msg, default=None, custom_msg=None):

    input_check=False
    while not input_check:
        if custom_msg:
                    option = input(f"{custom_msg}")
        else:
                    option = input(f"\n    Enter the {msg} of the Kafka instance : ")
        if not option :
            print(f"    No {msg} entered.")
            if default:
                continue_option=input(f"    Do you want to use the default value \"{default}\"? (y/n):")
                if continue_option =="Y" or continue_option=="y":
                    option=default
                    input_check=True
                    return option
            continue_option=input(f"    A {msg} is required to get metrics. Do you want to enter a {msg} (y/n) : ")

            if continue_option=="Y" or continue_option=="y":
                input_check=False
            else:
                input_check=True
                return False
        else:
            input_check=True
        
    return option



def initiate(plugin_name, plugin_url):

    args={}
    agent_path="/opt/site24x7/monagent/"
    agent_temp_path=agent_path+"temp/"
    agent_plugin_path=agent_path+"plugins/"

    print()
    print(colors.GREEN +"------------------------   Installing the plugin ----------------------------"+ colors.RESET)
    print()
    print(colors.BLUE +"""    Hostname/IP Address, JMX port, Server port, Kafka topic name, Kafka home and Kafka group name of the Kafka instance is required to get metrics. These details will be configured in the plugin configuration file.
          """+ colors.RESET)
    
    kafka_host=input_validate("hostname", default="localhost")
    if not kafka_host:
        print()
        print(colors.RED + "------------------------------ Error occured. Hostname is required to install the plugin. Process exited.  ------------------------------" + colors.RESET)
        return
    
    kafka_jmx_port=input_validate("jmx port", default="9999")
    if not kafka_jmx_port:
        print()
        print(colors.RED + "------------------------------ Error occured. Kafka JMX Port is required to install the plugin. Process exited.  ------------------------------" + colors.RESET)
        return
    
    kafka_server_port=input_validate("kafka server port", default="9092")
    if not kafka_server_port:
        print()
        print(colors.RED + "------------------------------ Error occured. Kafka server port is required to install the plugin. Process exited.  ------------------------------" + colors.RESET)
        return
    
    kafka_topic_name=input_validate("kafka topic")
    if not kafka_topic_name:
        print()
        print(colors.RED + "------------------------------ Error occured. Kafka Topics is required to install the plugin. Process exited.  ------------------------------" + colors.RESET)
        return
    
    kafka_home=input_validate("Kafka Home path")
    if not kafka_home:
        print()
        print(colors.RED + "------------------------------ Error occured. Kafka home path is required to install the plugin. Process exited.  ------------------------------" + colors.RESET)
        return
    
    kafka_group_name=input_validate("kafka group name")
    if not kafka_group_name:
        print()
        print(colors.RED + "------------------------------ Error occured. Kafka group name is required to install the plugin. Process exited.  ------------------------------" + colors.RESET)
        return
    

    print(colors.GREEN +"    Hostname, Kafka JMX port, Kafka Server port, Kafka topic name, Kafka home and Kafka group name received."+ colors.RESET)
    print()

    
    
    if not check_directory(agent_temp_path):
            print("    Site24x7 Linux agent directory not found.")
            print(colors.RED + "------------------------------ Error occured. Process exited. ------------------------------" + colors.RESET)
            return

    plugins_temp_path=os.path.join(agent_temp_path,"plugins/")
    if not check_directory(plugins_temp_path):
        if not make_directory(plugins_temp_path):
            print("")
            print(colors.RED + "------------------------------ Error occured. Process exited. ------------------------------" + colors.RESET)
            return 
    print(colors.GREEN +"    Installation in progress."+ colors.RESET)
    print()
    print("    Downloading the Kafka plugin files from Site24x7's GitHub repository.")

    if not down_move(plugin_name, plugin_url, plugins_temp_path):
        print("")
        print(colors.RED + "------------------------------ Error occured. Process exited. ------------------------------" + colors.RESET)
        return 
    print(colors.GREEN +"    Downloaded the Kafka plugin files successfully."+ colors.RESET)
    print()


    py_update_cmd = [ "sed", "-i", "1s|^.*|#! /usr/bin/python3|", f"{plugins_temp_path}{plugin_name}/{plugin_name}.py" ]
    if not execute_command(py_update_cmd):
        print(colors.RED + "------------------------------ Error occured. Process exited. ------------------------------" + colors.RESET)
        return 

    cmd=f"chmod 744 {plugins_temp_path}/{plugin_name}/{plugin_name}.py"
    if not execute_command(cmd):
        print("")
        print(colors.RED + "------------------------------ Error occured. Process exited. ------------------------------" + colors.RESET)
        return 
    print("")

    args={"kafka_host":kafka_host, "kafka_jmx_port":kafka_jmx_port, "kafka_server_port": kafka_server_port, "kafka_topic_name":kafka_topic_name, "kafka_home":kafka_home, "kafka_group_name":kafka_group_name}

    arguments=f"""--kafka_host={args["kafka_host"]} --kafka_jmx_port={args["kafka_jmx_port"]} --kafka_server_port={args["kafka_server_port"]} --kafka_topic_name={args["kafka_topic_name"]} --kafka_home={args["kafka_home"]} --kafka_group_name={args["kafka_group_name"]}"""
    cmd=f"{plugins_temp_path}/{plugin_name}/{plugin_name}.py"+ " "+arguments
    result=execute_command(cmd, need_out=True)
    if not plugin_validator(result):
        print("")
        print(colors.RED + "------------------------------ Error occured. Process exited. ------------------------------" + colors.RESET)
        return
    print("")

    print("    Adding the plugin configurations in the kafka.cfg file.")
    if not plugin_config_setter(plugin_name, plugins_temp_path, arguments, display_name=args["kafka_topic_name"]):
        print("")
        print(colors.RED + "------------------------------ Error occured. Process exited. ------------------------------" + colors.RESET)
        return 
    print("    Plugin configurations added successfully.")
    print()

    print("    Updating the plugin in the Site24x7 Agent directory")
    if not move_plugin(plugin_name, plugins_temp_path, agent_plugin_path):
        print("")
        print(colors.RED + "------------------------------ Error occured. Process exited. ------------------------------" + colors.RESET)
        return 
    print("    Added the plugin in the Site24x7 Agent directory")
    print()


    print(colors.GREEN +"------------------------------  Plugin installed successfully ------------------------------"+ colors.RESET)



if __name__ == "__main__":
    plugin_name="kafka"
    plugin_url="https://raw.githubusercontent.com/site24x7/plugins/master/kafka"
    initiate(plugin_name, plugin_url)



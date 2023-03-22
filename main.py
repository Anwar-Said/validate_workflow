"""
This module automates cwl workflows validation.

Author: Anwar Said
Date: 22nd March 2023
"""

import os
import sys
import subprocess
import json
import re
import argparse

def interractive_command(command):

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # stdout, stderr = process.communicate()
    output = ""
    while True:
        line = process.stdout.readline().decode()
        print(line)
        if line == "" and process.poll() is not None:
            break
        output += line
    print(line, end="") 
    
def get_docker_id(name):
    directory = name
    docker_key = None
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            with open(os.path.join(directory, filename), 'r') as json_file:
                data = json.load(json_file)
                requirements = data.get('requirements')
                
                if 'DockerRequirement' not in requirements.keys():
                    continue
                else:
                    docker_key = requirements.get("DockerRequirement").get("dockerPull")
                    break

    return docker_key
def command_registry(path_to_cli_jar):
    cmd_export = "export LEAP_CLI_DIR="+path_to_cli_jar
    cmd_echo = 'echo $LEAP_CLI_DIR'
    login_command = "java -jar leap_cli.jar user --login"
    logout_command ="java -jar leap_cli.jar user --logout"
    cmds = [cmd_export,'\n',cmd_echo]
    cmd_jar_login=  ['cd ',path_to_cli_jar,'\n',login_command]
    cmd_jar_logout=  ['cd ',path_to_cli_jar,'\n',logout_command]
    # command = ''.join(cmds)
    command_login = ''.join(cmd_jar_login)
    command_logout = ''.join(cmd_jar_logout)
    docker_pull = 'docker pull '+docker_key
    return command_login, command_logout,docker_pull,cmd_export
def prepare_cwl_command(path_to_wl):
    if os.path.exists(path_to_wl+'/README.md'):
        print("Workflow could not be located! Please provide a valide path to workflow directory!")
        sys.exit()
    with open(path_to_wl+'/README.md', 'r') as file:
        readme_content = file.read()
    cmd_search = "cwltool\s+(.*)"
    match = re.search(cmd_search, readme_content)
    cwl_tool_cmd = match.group()
    ##search for input id
    input_search = r"Required inputs\n(.+)"
    input_match = re.search(input_search, readme_content)
    if input_match:
        next_line = input_match.group(1)
    input = next_line.split(" ")[2]
    # print(cwl_tool_cmd)
    if "/" in path_to_wl:
        f_name = path_to_wl.split("/")[-1]
    else:
        f_name = path_to_wl
    with open(os.path.join(path_to_wl,f_name+".cwl.json"), 'r') as json_file:
        # file_contents = json_file.read()
        cwl_json =  json.load(json_file)
    id = cwl_json.get('inputs').get(input).get('default')

    updated_cwl_cmd = cwl_tool_cmd.replace("...",id)
    return updated_cwl_cmd


if __name__ == "__main__":
    
    path_to_wl = sys.argv[1]
    path_to_cli_jar =  sys.argv[2]
    if not os.path.exists(path_to_wl):
        print("Path to workflow could not located! Please provide a valide path")
        sys.exit()
    if not os.path.exists(path_to_cli_jar):
        print("Path to cli jar file could not located! Please provide a valide path")
        sys.exit()
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--path_to_wl', type=str, default='None')
    # parser.add_argument('--experiment', type=str, default='fixed')
    # args = parser.parse_args()
    # path_to_wl, path_to_cli_jar = args.path_to_wl,args.path_to_cli_jar
    print("The cogs are turning, and the cwl magic has begun!")
    docker_key = get_docker_id(path_to_wl)
    if docker_key == None:
        print("Docker key could not be located! Pleaese provide a valid path to the directory of CWL")
        sys.exit()
    
    command_login, command_logout,docker_pull,cmd_export = command_registry(path_to_cli_jar)
    interractive_command(command_login)
    interractive_command(docker_pull)
    print("Docker has been pulled successfully!")
    cwl_command = prepare_cwl_command(path_to_wl)
    all_commands = [cmd_export,"\n","cd "+path_to_wl, "\n",cwl_command]
    all_commands =''.join(all_commands)
    print("Environment created successfully! now running cwltool command", all_commands)
    interractive_command(all_commands)
    print("workflow has been executed successfully!")
    interractive_command(command_logout)



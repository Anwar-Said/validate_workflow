"""
This module automates cwl workflows validation.

Author: Anwar Said
Date: 22nd March 2023
"""


import tkinter as tk
from tkinter import ttk
import threading
import time
# from utils import *
import logging
import os
import sys
import subprocess
import json
import re
import argparse

class Validation:
    def __init__(self):
        self.root = tk.Tk()
        # self.root = root
        self.root.geometry("700x500")
        self.root.title("Workflow Validation")
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("green.Horizontal.TProgressbar", foreground='green', background='green')
        custom_font = ("Open Sans", 10,"bold")
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=500, mode="determinate",style="green.Horizontal.TProgressbar")
        self.progress_bar.grid(row=0, column=0, columnspan=5, padx=20, pady=20,sticky='nsew')
        self.root.grid_rowconfigure(0, minsize=70)
        # progress_bar.grid_configure(ipady=10, ipadx=10, pady=20, padx=20, sticky="nsew")
        # Create the checkboxes
        # self.checked_image = tk.PhotoImage(file="validate_workflow-main/icons/correct.png",height=27, width=27)
        # self.unchecked_image = tk.PhotoImage(file="validate_workflow-main/icons/uncheck.png",height=27, width=27)
        # self.default_image = tk.PhotoImage(file="validate_workflow-main/icons/checkbox1.png",height=27, width=27)

        self.checked_image = tk.PhotoImage(file="icons/correct.png",height=27, width=27)
        self.unchecked_image = tk.PhotoImage(file="icons/uncheck.png",height=27, width=27)
        self.default_image = tk.PhotoImage(file="icons/checkbox1.png",height=27, width=27)
        self.var_local = tk.BooleanVar()
        self.var_data = tk.BooleanVar()
        self.var_docker = tk.BooleanVar()
        self.var_dep = tk.BooleanVar()
        self.var_success = tk.BooleanVar()

        self.local_env = tk.Checkbutton(self.root, text="Local Environment",font=custom_font,image=self.default_image, compound="left",selectimage=self.checked_image, indicatoron=False,variable=self.var_local)
        self.data_pull = tk.Checkbutton(self.root, text="Data pull",font=custom_font,image=self.default_image, compound="left",selectimage=self.checked_image, indicatoron=False,variable=self.var_data)
        self.docker_pull = tk.Checkbutton(self.root, text="Docker pull",font=custom_font,image=self.default_image, compound="left",selectimage=self.checked_image, indicatoron=False,variable=self.var_docker)
        self.unmet_dep = tk.Checkbutton(self.root, text="Dependencies",font=custom_font,image=self.default_image, compound="left",selectimage=self.checked_image, indicatoron=False,variable=self.var_dep)
        self.success = tk.Checkbutton(self.root, text="Successful",font=custom_font,image=self.default_image, compound="left",selectimage=self.checked_image, indicatoron=False,variable=self.var_success)
        
        self.local_env.grid(row=1, column=0, padx=10, pady=5)
        self.data_pull.grid(row=1, column=1, padx=10, pady=5)
        self.docker_pull.grid(row=1, column=2, padx=10, pady=5)
        self.unmet_dep.grid(row=1, column=3, padx=10, pady=5)
        self.success.grid(row=1, column=4, padx=10, pady=5)
        self.root.grid_columnconfigure(1, minsize=100)
        self.root.grid_rowconfigure(1, minsize=50)

        log_font = ("Verdana", 10,"bold")
        scrollbar = tk.Scrollbar(self.root)
        scrollbar.grid(row=2, column=4,padx = 10,pady = 10,sticky="NS")
        self.log = tk.Text(self.root, height=25,padx = 10,font = log_font, yscrollcommand=scrollbar.set)
        self.log.configure(background="white",foreground="black")
        self.log.grid(row=2, column=0,columnspan=5, padx=10, pady=10)
        scrollbar.config(command=self.log.yview)


        self.worker_thread = threading.Thread(target=self.validate_workflow())
        self.worker_thread.start()

        self.root.protocol("WM_DELETE_WINDOW", self.stop_worker)
        self.worker_stopped = False
        self.root.mainloop()

    def validate_workflow(self):
        home_dir = os.path.expanduser('~')
        home_dir = home_dir+"/leap_cli"
        if not os.path.exists(home_dir) and os.access(home_dir, os.R_OK):
            print("to be implemented - download leap cli and set path")
        
        else:
            self.log.insert(tk.END,"Local environment has been created successfully! \n \n")
            self.local_env.select()
            self.root.update()
        self.log.insert(tk.END,"Executing Workflow ... \n \n")
        # self.local_env.select()
        self.progress_bar['value'] = 10
        self.root.update()
        cwl_command = self.prepare_cwl_command()
        # self.interractive_command(cwl_command)  

    def interractive_command(self,command):
        log_file = open("log.log", "a")
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # stdout, stderr = process.communicate()
        log = ""
        while True:
            line = process.stdout.readline().decode()
            log_file.write(line)
            print(line)
            if line == "" and process.poll() is not None:
                break
            log += line
            flag = self.parse_log(log)
            if flag:
                break
        log_file.close()
    def parse_log(self,log):
        flag = False
        if "Error reading data from file:" in log:
            self.log.insert(tk.END, "Cannot download data from DATALAKE! please ensure that the data is linked correctly \n \n")
            self.data_pull.configure(image = self.unchecked_image)
            self.root.update()
            flag = True

        if not self.var_data.get() and "Download Operation Completed" in log:
            self.log.insert(tk.END, "Data download operation completed! \n \n")
            self.data_pull.select()
            self.progress_bar['value'] = 40
            self.root.update()
            
        if "Docker is required to run this tool" in log:
            self.log.insert(tk.END, "Docker is required! Please check the docker is running on local machine and the docker image is up to date.\n \n")
            self.docker_pull.configure(image = self.unchecked_image)
            self.root.update()
            flag = True
        if "Pulling from" in log:
            self.log.insert(tk.END, "Pulling docker image ... \n \n")
            # self.docker_pull.configure(image = self.unchecked_image)
            self.root.update()
        if not self.var_docker.get() and  "Pull complete" in log:
            self.log.insert(tk.END, "Image has been pulled successfully! \n \n")
            # self.docker_pull.configure(image = self.checked_image)
            self.docker_pull.select()
            self.progress_bar['value'] = 70
            self.root.update()

        if not self.var_docker.get() and "[job Preprocess HK Data]" in log:
            self.log.insert(tk.END, "Docker image is up to date! \n \n")
            # self.docker_pull.configure(image = self.checked_image)
            self.docker_pull.select()
            self.progress_bar['value'] = 70
            self.root.update()
        if "Final process status is permanentFail" in log:
            message = "Workflow execution failed! Please make sure that the workflow has corretly been built and met all the dependencies (input, output, the docker image is up to date). \n \n"
            self.log.insert(tk.END,message)
            # self.docker_pull.configure(image = self.checked_image)
            self.unmet_dep.configure(image = self.unchecked_image)
            self.docker_pull.configure(image = self.unchecked_image)
            self.success.configure(image = self.unchecked_image)
            self.root.update()
        if "Final process status is success" in log:
            self.log.insert(tk.END, "Workflow has been executed successfully! \n \n")
            # self.docker_pull.configure(image = self.checked_image)
            self.unmet_dep.select()
            self.success.select()
            self.progress_bar['value'] = 100
            self.root.update()
        return flag 
            


    def prepare_cwl_command(self):
        with open('README.md', 'r') as file:
        # with open('validate_workflow-main/README.md', 'r') as file:    
            readme_content = file.read()
        cmd_search = "cwltool\s+(.*)"
        match = re.search(cmd_search, readme_content)
        cwl_tool_cmd = match.group()
        index = cwl_tool_cmd.find(".json")
        if index != -1:
            updated_cwl_cmd = cwl_tool_cmd[:index+5]
        else:
            updated_cwl_cmd = cwl_tool_cmd
        return updated_cwl_cmd
    
        
    def stop_worker(self):
        self.worker_stopped = True
        self.worker_thread.join()
        self.root.destroy()

def main():
    # root = tk.Tk()
     Validation()
    
    

if __name__ == "__main__":
    main()
    


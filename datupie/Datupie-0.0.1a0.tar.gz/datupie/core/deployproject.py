from datupie.core.startproject import StartCommand
import requests
import os
import json

class DeployCommand(StartCommand):
    def __init__(self):
        StartCommand.__init__(self)
        self.uri = "http://35.172.203.237:8081/deploy"
        self.uri_status = "http://35.172.203.237:8081/status"
    
    def deployproject(self):
        name_project = input("Type the name of (data science) project you would to deploy: ")
        data = dict({'project':name_project, 'file':name_project})
        response = requests.post(self.uri, json=data)
        
        if response.text == "It seems that is already a architecture deployed":
            self.create_folder_projects(project_name = name_project)
            response_status = requests.post(self.uri_status,json=data)
            if os.path.exists(f"{self.abspath}/{name_project}"):
                with open(f"{self.abspath}/{name_project}/{name_project}.tf.json", "w") as _file:
                    json.dump(response_status.json(),_file)
                with open(f"{self.abspath}/{name_project}/project.cfg", "w") as _file:
                    _file.write("[metadata]\n")
                    _file.write(f"project = {name_project}\n")
                    _file.write(f"architecture = {self.abspath}/{name_project}/{name_project}.tf.json\n")                
            else : print(response_status.text)
        elif response.text == "Resources were not deployed":
            print("Some error ocurrs while deploying")
        else : print(response.text)

    def create_folder_projects(self, **kwards):
        if os.path.exists(f"{self.abspath}/{kwards['project_name']}"):
            print("The project exists in local")
        else:
            confirmation = str(input("There isn't exists a local project, would you like to create it? [y/N]: "))
            if confirmation == "y":
                os.mkdir(f"{self.abspath}/{kwards['project_name']}")
                main_dirs = [kwards['project_name'],"test"]
                secondary_dirs = ["clean","prepare","transform","inference","data"]
                for _dir in main_dirs:
                    os.mkdir(f"{self.abspath}/{kwards['project_name']}/{_dir}")
                    with open(f"{self.abspath}/{kwards['project_name']}/{_dir}/__init__.py","w") : pass
                    if _dir == kwards['project_name']:
                        with open(f"{self.abspath}/{kwards['project_name']}/{_dir}/__main__.py","w") as main_file : 
                            main_file.write(f"from {kwards['project_name']}.clean import clean\n")
                            main_file.write(f"from {kwards['project_name']}.prepare import prepare\n")
                            main_file.write(f"from {kwards['project_name']}.transform import transform\n")
                            main_file.write(f"from {kwards['project_name']}.inference import inference\n\n")
                            main_file.write(f"if __name__ == '__main__':\n")
                            main_file.write(f"\t## your code here datupian")

                for _dir in secondary_dirs:
                    os.mkdir(f"{self.abspath}/{kwards['project_name']}/{kwards['project_name']}/{_dir}")
                    if _dir == "data" : pass
                    else :
                        with open(f"{self.abspath}/{kwards['project_name']}/{kwards['project_name']}/{_dir}/__init__.py","w") : pass
                        with open(f"{self.abspath}/{kwards['project_name']}/{kwards['project_name']}/{_dir}/{_dir}.py","w") : pass
                        with open(f"{self.abspath}/{kwards['project_name']}/{kwards['project_name']}/{_dir}/{_dir}.ipynb","w") as _file : 
                            json.dump({
                                "metadata": {
                                    "language_info": {
                                        "codemirror_mode": {
                                            "name": "ipython",
                                            "version": 3
                                        },
                                        "file_extension": ".py",
                                        "mimetype": "text/x-python",
                                        "name": "python",
                                        "nbconvert_exporter": "python",
                                        "pygments_lexer": "ipython3",
                                        "version": 3
                                    },
                                    "orig_nbformat": 2
                                },
                                "nbformat": 4,
                                "nbformat_minor": 2,
                                "cells": [{
                                    "cell_type": "code",
                                    "execution_count": "",
                                    "metadata": {},
                                    "outputs": [],
                                    "source": [
                                        "import datup as dt\n",
                                        "import pandas as pd\n",
                                        "import numpy as np"
                                    ]
                                }]
                            }, _file)
            else:
                print("Project is created at server. For deploy it type datupie-admin deployproject on command prompt")




        
    



import os
import json

def get_project_path(path = None):
    if not path:
        path = os.getcwd()
    files = os.listdir(path)
    if ".tracerbullet" in files and os.path.isdir(path+"/.tracerbullet"):
        return path
    return None 

def get_project_config(path):
    with open(path+"/config.json","r") as config_file:
        return json.loads(config_file.read())

def save_project_config(path,config):
    with open(path+"/config.json","w") as config_file:
        config_file.write(json.dumps(config))

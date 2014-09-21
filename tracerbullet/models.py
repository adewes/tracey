from __future__ import absolute_import
from .helpers import get_project_config,save_project_config

import os

class Project(object):

    def __init__(self,path):
        self.__dict__['config'] = {}
        self.__dict__['path'] = path

    def __len__(self):
        return len(self.config)

    def __contains__(self,key):
        return True if key in self.config else False

    def __getitem__(self,key):
        return self.config[key]

    def __delitem__(self,key):
        if key in self.config:
            del self.config[key]

    def __getattr__(self,attr):
        try:
            return self.config[attr]
        except KeyError:
            raise AttributeError("Unknown attribute: %s" % attr)

    def __setattr__(self,attr,value):
        self.config[attr] = value

    __setitem__ = __setattr__

    def __delattr__(self,attr):
        if attr in self.config:
            del self.config[attr]

    def save(self):
        save_project_config(self.path,self.config)

    def load(self):
        self.__dict__['config'] = get_project_config(self.path)

    def save_profile(self,profile):
        cnt = 1
        output_dir = self.path+"/profiles"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_file = output_dir+"/%d_%6d.json" % (int(time.time()),cnt)
        while os.path.exists(output_file):
            cnt+=1
            output_file = output_dir+"/%d_%6d.json" % (int(time.time()),cnt)

        with open(output_file,"wb") as output_file:
            output_file.write(json.dumps(profile,indent = 2))


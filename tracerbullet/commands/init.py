# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from base import BaseCommand
from tracerbullet.helpers import save_project_config

import sys
import os
import os.path
import json
import time
import uuid

"""
Creates a new project.
"""

class Command(BaseCommand):

    requires_valid_project = False

    options = BaseCommand.options

    description = """
    Initializes a new tracerbullet project in the current directory.
    """

    def run(self):
        print "Initializing new project"

        project_path = os.getcwd()
        config_path = project_path+"/.tracerbullet"
        print config_path

        if os.path.exists(config_path):
            print "Found another project with the same path, aborting."
            return -1

        config = {
            'project_id' : uuid.uuid4().hex,
        }

        os.makedirs(config_path)
        save_project_config(config_path,config)

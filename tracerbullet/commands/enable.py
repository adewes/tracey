# -*- coding: utf-8 -*-
from __future__ import unicode_literals,absolute_import

import traceback
import sys
import time
import pprint
import os
import os.path
import json
import argparse
import uuid

from .base import BaseCommand

from tracerbullet.helpers import save_project_config
from tracerbullet.tracer import Tracer


"""
Runs the profiler
"""

class Command(BaseCommand):

    requires_valid_project = True


    description = """
    Enable the profiler
    """

    def run(self):
        print "Previous status:" + ("enabled" if 'enabled' in self.project and self.project['enabled'] else 'disabled')
        self.project['enabled'] = True 
        print "New status:" + ("enabled" if 'enabled' in self.project and self.project['enabled'] else 'disabled')
        self.project.save()
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
from tracerbullet.server.app import app

"""
Runs the profiler
"""

class Command(BaseCommand):

    requires_valid_project = True

    options = BaseCommand.options +[
    ]

    description = """
    Runs the server.
    """

    def run(self):

        app.run(debug = False,host = '0.0.0.0',port = 8888)

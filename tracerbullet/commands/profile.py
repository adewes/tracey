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
import signal

from .base import BaseCommand

from tracerbullet.helpers import save_project_config
from tracerbullet.tracer import Tracer
from tracerbullet.server.app import ServerProcess
from multithreading import Thread

"""
Runs the profiler
"""

class Command(BaseCommand):

    requires_valid_project = True

    options = BaseCommand.options +[
        {
        'name'        : '--o',
        'action'      : 'store',
        'dest'        : 'output',
        'default'     : "tracerbullet_%d.json" % int(time.time()),
        'help'        : 'where to store profiler output.'
        },
    ]

    description = """
    Profiles a given script.
    """

    def process_pipe(self,signum,frame):
        self.tracer.pause()
        while not self.server.command_queue.empty():
            command = self.server.command_queue.get()
            command_name = command[0]
            command_params = command[1:]
            if command_name == "get_profile":
                profile = self.tracer.processed_profile
                self.server.response_queue.put(profile)
            elif command_name == "add_code":
                code_id = command_params[0]
                if not 'tracked_code' in self.project:
                    self.project['tracked_code'] = {}
                self.project['tracked_code'][code_id] = True
                self.project.save()
                print "Adding code: %s" % code_id
                self.tracer.add_code_by_id(code_id)
                self.server.response_queue.put("ok")
            elif command_name == "remove_code":
                code_id = command_params[0]
                if 'tracked_code' in self.project:
                    self.project['tracked_code'][code_id] = False
                self.project.save()
                print "Removing code: %s" % code_id
                self.tracer.remove_code_by_id(code_id)
                self.server.response_queue.put("ok")
        self.tracer.resume()

    def run(self):

        print "Profiling..."

        outfile = self.opts['output']

        self.tracer = Tracer({'verbose' : False,'project_path' : os.path.dirname(__file__)})
        with open(self.filename,"r") as python_file:
            sys.argv = [os.path.abspath(self.filename)]+sys.argv[3:]
            try:
                lc = {'__name__':'__main__','__file__' : self.filename}
                start_time = time.time()
                compiled_code = compile(python_file.read(),self.filename,'exec')
                self.tracer.add_code(compiled_code)
                if 'tracked_code' in self.project:
                    for code_id,track in self.project['tracked_code'].items():
                        if track:
                            self.tracer.add_code_by_id(code_id)
                        else:
                            self.tracer.remove_code_by_id(code_id)
                self.tracer.start(add_caller = False)
                self.server = ServerProcess()
                self.server.start()
                signal.signal(signal.SIGALRM,self.process_pipe)
                signal.setitimer(signal.ITIMER_REAL,0.01,0.01)
                exec compiled_code in lc,lc
            except SystemExit as e:
                pass
            except BaseException as e:
                print "An exception occured during the execution:"
                traceback.print_exc()
            finally:
                self.tracer.stop()
                stop_time = time.time()

            profile = self.tracer.processed_profile
            pprint.pprint(profile)

            print "Elapsed time: %g" % (stop_time-start_time)

            with open(outfile,"wb") as output_file:
                output_file.write(json.dumps(profile,indent = 2))


            print "[Hit ENTER to stop server and exit]"

            try:
                sys.stdin.readline()
            finally:
                self.server.terminate()
                signal.setitimer(signal.ITIMER_REAL,0)



    def parse_args(self,raw_args):

        filename = os.path.abspath(raw_args[0])

        if '--' in raw_args:
            i = raw_args.index('--')
            our_args= raw_args[1:i]
            self.args_for_cmd = raw_args[i+2:]
        else:
            our_args = raw_args[1:]

        rc = super(Command,self).parse_args(our_args)

        self.filename = filename

        return rc

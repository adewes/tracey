#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (unicode_literals,absolute_import)
import sys
import time

from types import ModuleType
from tracerbullet import commands
from tracerbullet.helpers import get_project_path,get_project_config
from tracerbullet.models import Project

def load_command_class():
    i = 1
    current_module = commands
    command_chain = []
    while not hasattr(current_module,'Command'):
        if len(sys.argv) < i+1:
            sys.stderr.write("Usage: tracerbullet [command] [command] [...] [args]\n\nType \"checkmate help\" for help\n")
            exit(-1)
        cmd = sys.argv[i]
        command_chain.append(cmd)
        i+=1
        if not hasattr(current_module,cmd):
            sys.stderr.write("Unknown command: %s\n" % " ".join(command_chain))
            exit(-1)
        current_module = getattr(current_module,cmd)

    return current_module.Command,command_chain

def main():

    CommandClass,command_chain = load_command_class()
    project_path = get_project_path()   

    if project_path:

        try:
            project = Project(project_path+"/.tracerbullet")
            project.load()
        except (IOError,):
            sys.stderr.write("No project configuration found!\n")
            exit(-1)

    else:
        if CommandClass.requires_valid_project:
            sys.stderr.write("Cannot find a tracerbullet project in the current directory tree, aborting.\n")
            exit(-1)
        project = None

    command = CommandClass(project,prog = sys.argv[0]+" "+" ".join(command_chain),args = sys.argv[1+len(command_chain):])

    try:
        if 'help' in command.opts and command.opts['help']:
            print command.help_message()
            exit(0)
        exit(command.run())
    except KeyboardInterrupt:
        print "[CTRL-C pressed, aborting]"
        exit(-1)

if __name__ == '__main__':
    main()
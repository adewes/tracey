# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import argparse
import copy

class BaseCommand(object):

    requires_valid_project = True
    options = [
        {
        'name'        : '--help',
        'action'      : 'store_true',
        'dest'        : 'help',
        'default'     : False,
        'help'        : 'display this help message.'
        },
        {
        'name'        : '--non-interactive',
        'action'      : 'store_true',
        'dest'        : 'non_interactive',
        'default'     : False,
        'help'        : 'non-interactive mode.'
        },
        ]

    description = None

    def __init__(self,project = None,prog = None,args = None):
        self.project = project
        self.prog = prog
        self.parse_args(args if args else [])

    def _get_arg_parser(self):
        parser = argparse.ArgumentParser(self.prog,add_help = False,description = self.description)
        return parser

    def parse_args(self,raw_args):
        parser = self._get_arg_parser()
        for opt in self.options:
            c_opt = copy.deepcopy(opt)
            name = c_opt['name']
            del c_opt['name']
            parser.add_argument(name,**c_opt)
        args,self.extra_args = parser.parse_known_args(raw_args)
        if args.help:
            return parser.print_help()
        self.raw_args = raw_args
        self.opts = vars(args)

    def help_message(self):
        parser = self._get_arg_parser()
        return parser.format_help()
        
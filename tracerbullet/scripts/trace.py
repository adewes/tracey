#!/usr/bin/python
from tracerbullet.ctracer import Tracer
import traceback
import sys
import time
import os
import os.path
import json
import argparse

def parse_args(args):
    print args
    parser = argparse.ArgumentParser(description='Perform line-by-line profiling of a Python program.')
    parser.add_argument("-o", help="location of JSON file that contains line statistics",
                    action="store",default = "tracerbullet_%d.json" % int(time.time()) )
    options = parser.parse_args(args)
    return options

def main():
    filename = os.path.basename(__file__)

    if len(sys.argv) < 2:
        print "Usage: %s [command name] [options] [--] [command arguments]" % filename
        exit(-1)

    if '--' in sys.argv:
        i = sys.argv.index('--')
        our_args= sys.argv[1:i]
        args_for_cmd = sys.argv[i+1:]

    args = parse_args(our_args[1:])

    filename = our_args[0]
    outfile = args.o

    tracer = Tracer(verbose = False,method = "raw",trace_hierarchy = True)

    with open(filename,"r") as python_file:
        sys.argv = [os.path.abspath(filename)]+sys.argv[3:]
        try:
            tracer.start()
            exec python_file in {'__name__':'__main__'}
        except SystemExit as e:
            pass
        except BaseException as e:
            print "An exception occured during the execution"
            traceback.print_exc()
        finally:
            tracer.stop()
    profile = tracer.profile
    if __file__ in profile:
        del profile[__file__]
    profile_items = tracer.get_sorted_profile()
    print "Elapsed time: %g" % tracer.elapsed_time

    with open(outfile,"wb") as output_file:
        output_file.write(json.dumps(profile_items,indent = 2))


if __name__ == '__main__':
    main()

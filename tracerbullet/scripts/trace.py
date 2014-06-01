#!/usr/bin/python
from tracerbullet.tracer import Tracer
import traceback
import sys
import time
import pprint
import os
import os.path
import json
import argparse

from tracerbullet.profiler import set_profiler,get_profiler

def parse_args(args):
    print args
    parser = argparse.ArgumentParser(description='Perform line-by-line profiling of a Python program.')
    parser.add_argument("-o", help="location of JSON file that contains line statistics",
                    action="store",default = "tracerbullet_%d.json" % int(time.time()) )
    options = parser.parse_args(args)
    return options

def main():
    filename = os.path.basename(__file__)

    if len(sys.argv) < 2 or not '--' in sys.argv:
        print "Usage: %s [options] -- [command] [arguments]" % filename
        exit(-1)

    if '--' in sys.argv:
        i = sys.argv.index('--')
        our_args= sys.argv[1:i]
        filename = os.path.abspath(sys.argv[i+1])
        args_for_cmd = sys.argv[i+2:]

    args = parse_args(our_args[1:])

    outfile = args.o

    tracer = Tracer(verbose = False,method = "normal")
    set_profiler(tracer)

    with open(filename,"r") as python_file:
        sys.argv = [os.path.abspath(filename)]+sys.argv[3:]
        try:
            lc = {'__name__':'__main__'}
            start_time = time.time()
            compiled_code = compile(python_file.read(),filename,'exec')
            tracer.add_code(compiled_code)
            tracer.add_code_by_id(filename+":sleep_some_more")
            tracer.start(add_caller = False)
            exec compiled_code in lc,lc
        except SystemExit as e:
            pass
        except BaseException as e:
            print "An exception occured during the execution"
            traceback.print_exc()
        finally:
            tracer.stop()
            stop_time = time.time()
    assert get_profiler() == tracer
    profile = tracer.processed_profile
    pprint.pprint(profile)
    print "Elapsed time: %g" % (stop_time-start_time)

    with open(outfile,"wb") as output_file:
        output_file.write(json.dumps(profile,indent = 2))


if __name__ == '__main__':
    main()
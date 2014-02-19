#!/usr/bin/python
from tracerbullet import Tracer
import traceback
import sys
import os
import json

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print "Usage: simple_profiler.py [command name] [output file] [args to command]"

    filename = sys.argv[1]
    outfile = sys.argv[2]

    tracer = Tracer()

    with open(filename,"r") as python_file:
        sys.argv = [os.path.abspath(filename)]+sys.argv[3:]
        try:
            tracer.start()
            exec python_file
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
    for filename,line_timings in profile.items():
        total_time = max([x[1] for x  in line_timings.values()])
        profile[filename] = {'total_time' : total_time,'line_timings' : line_timings}
    profile_items = sorted(profile.items(),key = lambda x: -x[1]['total_time'])
    print "Elapsed time: %g" % tracer.elapsed_time

    with open(outfile,"wb") as output_file:
        output_file.write(json.dumps(profile_items,indent = 2))


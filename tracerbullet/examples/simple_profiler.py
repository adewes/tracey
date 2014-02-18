#from tracerbullet import Tracer
import time
import sys  
import pprint
import os
import json
from example_module import foo
from collections import defaultdict

timings = defaultdict(lambda : defaultdict(lambda : [0,0]) )
last_time = None
trace_stack = []

def my_func():
    time.sleep(0.1)
    for i in range(0,100000):
        foo()
    print "That's it"


def traceit(frame, event, arg):
    global last_time,trace_stack
    current_time = time.time()
    if last_time:
        elapsed_time = current_time-last_time
    else:
        elapsed_time = 0
    last_time = current_time
    if event == "line":
        lineno = frame.f_lineno
        cnts = timings[frame.f_code.co_filename][frame.f_lineno]
        cnts[0]+=1
        cnts[1]+=elapsed_time
#        print "Trace stack:",trace_stack
        #for  in trace_stack:
        #    timings[filename][line_number][1]+=elapsed_time
        print "Line     :", frame.f_code.co_filename,lineno
    elif event in ("call","c_call"):
        print "Adding   :",frame.f_code.co_filename,frame.f_lineno
        trace_stack.append(frame)
    elif event in ("return","exception","c_return","c_exception"):
        returning_filename = frame.f_back.f_code.co_filename
        returning_line_number = frame.f_back.f_lineno
        print "Removing :",frame.f_back.f_code.co_filename,frame.f_back.f_lineno
#        print "return or exception:",frame.f_code.co_filename,frame.f_back.f_code.co_filename
        trace_stack.remove(frame)
    return traceit

if __name__ == '__main__':
    filename = sys.argv[1]
    outfile = sys.argv[2]
    if len(sys.argv) < 3:
        print "Usage: simple_profiler.py [command name] [output file] [args to command]"
    start = time.time()
    with open(filename,"r") as python_file:
        sys.argv = [os.path.abspath(filename)]+sys.argv[3:]
        try:
            sys.settrace(traceit)
            exec python_file
        except SystemExit as e:
            pass
        finally:
            sys.settrace(None)
    for filename,line_timings in timings.items():
        total_time = sum([x[1] for x  in line_timings.values()])
        timings[filename] = {'total_time' : total_time,'line_timings' : line_timings}
    sorted_timings = sorted(timings.items(),key = lambda x: -x[1]['total_time'])
    print "Elapsed time: %g" % (time.time()-start)
    with open(outfile,"wb") as output_file:
        output_file.write(json.dumps(sorted_timings,indent = 2))
    print "Done..."
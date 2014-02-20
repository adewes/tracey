#from tracerbullet import Tracer
import time
import sys  
import inspect
import copy

from collections import defaultdict

class Tracer(object):

    def __init__(self,verbose = True,trace_hierarchy = False,method = "normal"):
        self.verbose = verbose
        self.trace_hierarchy = trace_hierarchy
        self.reset()

    def reset(self):

        self._profile = defaultdict(lambda : defaultdict(lambda : [0,0]) )
        self._last_time = None
        self._trace_stack = []
        self._start_time = 0
        self._stop_time = 0
        self._last_executed_statement = None

    def get_sorted_profile(self):
        sorted_profile = {}
        for filename,line_timings in self.profile.items():
            total_time = max([x[1] for x  in line_timings.values()])
            sorted_profile[filename] = {'total_time' : total_time,'line_timings' : line_timings}
        profile_items = sorted(sorted_profile.items(),key = lambda x: -x[1]['total_time'])
        return profile_items

    def start(self):
        self._start_time = time.time()
        sys.settrace(self.trace)

    def stop(self,delete_self = True):
        sys.settrace(None)
        self._stop_time = time.time()
        if delete_self:
            if __file__ in self._profile:
                del self._profile[__file__]
            if __file__[:-1] in self._profile:
                del self._profile[__file__[:-1]]

    @property
    def profile(self):
        return self._profile

    @property
    def elapsed_time(self):
        return self._stop_time - self._start_time

    def trace(self,frame, event, arg,tracers = None):

        current_time = time.time()
        if self._last_time:
            elapsed_time = current_time-self._last_time
        else:
            elapsed_time = 0
        self._last_time = current_time

        if self.verbose:
            print "line    :",frame.f_code.co_filename,frame.f_lineno
    
        if self._last_executed_statement:
    
            if self.verbose:
                print "\t\t\t",self._last_executed_statement[0],self._last_executed_statement[1]," + ",elapsed_time

            cnts = self._profile[self._last_executed_statement[0]][self._last_executed_statement[1]]
            cnts[0]+=1
            cnts[1]+=elapsed_time

            if self.trace_hierarchy:
                for filename,line_number in self._trace_stack:
                    if self.verbose:
                        print "\t\t\t",filename,line_number," + ",elapsed_time
                    cnts = self._profile[filename][line_number]
                    cnts[1]+=elapsed_time

        self._last_executed_statement = (frame.f_code.co_filename,frame.f_lineno)

        if not self.trace_hierarchy:
            return self.trace

        if event == "line":
            pass
        elif event in ("call","c_call"):
            self._trace_stack.append([frame.f_back.f_code.co_filename,frame.f_back.f_lineno])
            if self.verbose:
                print "call    :",frame.f_code.co_filename,frame.f_lineno,"\t",frame.f_back.f_code.co_filename,frame.f_back.f_lineno
        elif event in ("return","c_return"):
            self._trace_stack.remove([frame.f_back.f_code.co_filename,frame.f_back.f_lineno])
            if self.verbose:
                print "return  :",frame.f_code.co_filename,frame.f_lineno,"\t",frame.f_back.f_code.co_filename,frame.f_back.f_lineno
        return self.trace

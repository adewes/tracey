#from tracerbullet import Tracer
import time
import sys  
import inspect
import copy

from collections import defaultdict
import tracerbullet

class Tracer(object):

    def __init__(self,verbose = True,trace_hierarchy = False,method = "normal"):
        self.verbose = verbose
        self.reset()

    def reset(self):

        self._profile = defaultdict(lambda : defaultdict(lambda : [0,0]) )
        self._last_executed_code = {}
        self._profile = {}
        self._n_starts = 0
        self._code_to_track = {}
        self._processed_profile = None

    def get_sorted_profile(self):
        sorted_profile = {}
        for filename,line_timings in self.profile.items():
            total_time = max([x[1] for x  in line_timings.values()])
            sorted_profile[filename] = {'total_time' : total_time,'line_timings' : line_timings}
        profile_items = sorted(sorted_profile.items(),key = lambda x: -x[1]['total_time'])
        return profile_items

    def start(self):
        self._n_starts+=1
        sys.settrace(self.trace)

    def stop(self,delete_self = True):
        self._n_starts-=1
        if self._n_starts == 0:
            sys.settrace(None)
            self._processed_profile = {}

    def process_profile(self):
        for code,timings in self._profile.items():
            if not code.co_filename in self._processed_profile:
                self._processed_profile[code.co_filename] = {}
            d = self._processed_profile[code.co_filename]
            for line,details in timings.items():
                if not line in d:
                    d[line] = [0,0]
                d[line][0]+=details[0]
                d[line][1]+=details[1]
        return self._processed_profile

    @property
    def profile(self):
        return self._profile

    @property
    def processed_profile(self):
        if not self._processed_profile:
            self.process_profile()
        return self._processed_profile

    @property
    def elapsed_time(self):
        return self._stop_time - self._start_time

    def add_code(self,code):
        if not code in self._code_to_track:
            self._code_to_track[code] = 1

    def remove_code(self,code):
        if code in self._code_to_track:
            del self._code_to_track[code]

    def trace(self,frame, event, arg,tracers = None):

        if not frame.f_code in self._code_to_track:
            return self.trace

        current_time = time.time()

        if frame in self._last_executed_code:
            last_executed_code,last_executed_line,last_executed_time = self._last_executed_code[frame]
            elapsed_time = current_time-last_executed_time

            if not last_executed_code in self._profile:
                self._profile[last_executed_code] = {}
            if not last_executed_line in self._profile[last_executed_code]:
                self._profile[last_executed_code][last_executed_line] = [0,0.0]

            pr = self._profile[last_executed_code][last_executed_line]

            pr[0]+=1
            pr[1]+=elapsed_time

        if event == "line":
            self._last_executed_code[frame] = (frame.f_code,frame.f_lineno,current_time)
        else:
            if frame in self._last_executed_code:
                del self._last_executed_code[frame]

        return self.trace
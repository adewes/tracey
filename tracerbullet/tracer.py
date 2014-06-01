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
        self._adjacent_code = defaultdict(lambda :0)
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

    def start(self,add_caller = True):
        self._n_starts+=1
        if add_caller:
            #We add the calling frame so that we can trace it.
            self.add_code(sys._getframe(1).f_code)
        sys.settrace(self.trace)

    def stop(self,delete_self = True):
        self._n_starts-=1
        if self._n_starts == 0:
            sys.settrace(None)
            self._processed_profile = {}

    def _get_source(self,filename,min_line,max_line):
        with open(filename,"r") as input_file:
            content = input_file.read()
            lines = content.split("\n")
            return lines[min_line-1:max_line+1]

    def process_profile(self):
        self._processed_profile = {
            'profiles' : [],
            'adjacent_code' : [],
        }

        for code,n_calls in self._adjacent_code.items():
            details = {
                'filename' : code.co_filename,
                'code_id' : self.get_code_id(code),
                'name' : code.co_name,
                'n_calls' : n_calls
            }
            self._processed_profile['adjacent_code'].append(details)

        for code,timings in self._profile.items():
            
            code_id = self.get_code_id(code)

            details = {
                'code_id' : code_id,
                'filename' : code.co_filename,
                'name' : code.co_name,
                'times' : {}
            }

            d = details['times']
            min_line = -1
            max_line = -1
            for line,line_details in timings.items():
                if line < min_line or min_line == -1:
                    min_line = line
                if line > max_line or max_line == -1:
                    max_line = line
                if not line in d:
                    d[line] = [0,0]
                d[line][0]+=line_details[0]
                d[line][1]+=line_details[1]

            details['source'] = (self._get_source(code.co_filename,min_line,max_line),(min_line,max_line))

            self._processed_profile['profiles'].append(details)

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
        code_id = self.get_code_id(code)
        return self.add_code_by_id(code_id)

    def add_code_by_id(self,code_id):
        print "Adding:",code_id
        self._code_to_track[code_id] = 1

    def get_code_id(self,code):
        return code.co_filename+":"+code.co_name

    def remove_code(self,code):
        code_id = self.get_code_id(code)
        self.remove_code_by_id(code_id)

    def remove_code_by_id(self,code_id):
        if code_id in self._code_to_track:
            del self._code_to_track[code_id]

    def trace(self,frame, event, arg,tracers = None):

        code_id = frame.f_code.co_filename+":"+frame.f_code.co_name

        if not code_id in self._code_to_track:
            back_code_id = frame.f_back.f_code.co_filename+":"+frame.f_back.f_code.co_name
            if back_code_id in self._code_to_track and not frame.f_code in self._adjacent_code:
                self._adjacent_code[frame.f_code]+=1
                print frame.f_back.f_code.co_name,"->",frame.f_code.co_name+"("+frame.f_code.co_filename+")"
            return self.trace
        else:
            print "::"+code_id

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
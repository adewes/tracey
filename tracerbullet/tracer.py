import time
import sys  
import inspect
import copy
import os

from collections import defaultdict
import tracerbullet

class Tracer(object):

    def __init__(self,config):
        self.config = config
        self.reset()
        self.cnt = 0

    def reset(self):

        self._profile = defaultdict(lambda : defaultdict(lambda : [0,0]) )
        self._last_executed_code = {}
        self._profile = {}
        self._adjacent_code = defaultdict(lambda :defaultdict(lambda : defaultdict(lambda : 0)))
        self._n_starts = 0
        self._code_to_track = defaultdict(lambda : {})
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

    def pause(self):
        sys.settrace(None)

    def resume(self):
        sys.settrace(self.trace)

    def _get_source(self,filename,min_line,max_line):
        with open(filename,"r") as input_file:
            content = input_file.read()
            lines = content.split("\n")
            return lines[min_line-1 if min_line-1 >= 0 else 0:max_line+1]

    def get_module_name_from_filename(self,filename):
        absolute_filename = os.path.abspath(filename)
        best_match = None
        for path in sys.path:
            absolute_path = os.path.abspath(path)
            if absolute_filename.startswith(absolute_path):
                if best_match is None or len(absolute_path) > len(best_match):
                    best_match = absolute_path
        if best_match is not None:
            relative_filename = absolute_filename[len(best_match)+1:]
            if relative_filename.endswith("/__init__.py"):
                relative_filename=relative_filename[:-len("/__init__.py")]
            if relative_filename.endswith(".py"):
                relative_filename = relative_filename[:-3]
            module_name = relative_filename.replace("/",".")
            return module_name
        return None

    def process_profile(self):
        self._processed_profile = {
            'profiles' : [],
            'adjacent_code' : [],
        }

        for referer,adjacent_code_by_line in self._adjacent_code.items():
            for line_number,adjacent_code in adjacent_code_by_line.items():
                for code,n_calls in adjacent_code.items():
                    details = {
                        'filename' : code.co_filename,
                        'code_id' : self.get_code_id(code),
                        'name' : code.co_name,
                        'n_calls' : n_calls,
                        'referer' : referer,
                        'linking_line_number' : code.co_firstlineno,
                        'line_number' : line_number,
                        'module_name' : self.get_module_name_from_filename(code.co_filename)
                    }
                    self._processed_profile['adjacent_code'].append(details)

        for code,timings in self._profile.items():
            
            code_id = self.get_code_id(code)

            details = {
                'code_id' : code_id,
                'filename' : code.co_filename,
                'module_name' : self.get_module_name_from_filename(code.co_filename),
                'name' : code.co_name,
                'line_number' : code.co_firstlineno,
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
                d[line][0]+=len(line_details)
                d[line][1]+=sum(line_details)

            details['source'] = (self._get_source(code.co_filename,min_line-2,max_line+2),(min_line -2 if min_line - 2 >= 1 else 1,max_line+2))

            self._processed_profile['profiles'].append(details)

        self._processed_profile['tracked_code'] = [{'code_id' : code_id} for code_id in self._code_to_track['id'].keys()]

        for d in self._processed_profile['tracked_code']:
            filename,name = d['code_id'].split(":")
            d['filename'] = filename
            d['name'] = name
            d['module_name'] = self.get_module_name_from_filename(filename)

        return self._processed_profile

    @property
    def profile(self):
        return self._profile

    @property
    def processed_profile(self):
        self.process_profile()
        return self._processed_profile

    @property
    def elapsed_time(self):
        return self._stop_time - self._start_time

    def add_code(self,code):
        code_id = self.get_code_id(code)
        return self.add_code_by_id(code_id)

    def add_code_by_id(self,code_id):
        self._code_to_track['id'][code_id] = 1

    def add_code_by_function(self,fn):
        return self.add_code(fn.__code__)

    def add_code_by_name(self,code_name):
        self._code_to_track['name'][code_name] = 1

    def get_code_id(self,code):
        module_name = inspect.getmodulename(code.co_filename)
        return code.co_filename+":"+code.co_name

    def remove_code(self,code):
        code_id = self.get_code_id(code)
        self.remove_code_by_id(code_id)

    def remove_code_by_id(self,code_id):
        if code_id in self._code_to_track['id']:
            print "Removing: %s" % code_id
            del self._code_to_track['id'][code_id]
            for code in self._profile.keys():
                if self.get_code_id(code) == code_id:
                    print "Cleaning code profile..."
                    del self._profile[code]
    
    def trace(self,frame, event, arg,tracers = None):

        code_id = frame.f_code.co_filename+":"+frame.f_code.co_name
        if '_do_profile' in frame.f_locals:
            self._code_to_track['id'][frame.f_code.co_filename+":"+frame.f_code.co_name] = True

        back_code_id = frame.f_back.f_code.co_filename+":"+frame.f_back.f_code.co_name
        if back_code_id in self._code_to_track['id']:
            self._adjacent_code[back_code_id][frame.f_back.f_lineno][frame.f_code]+=1

        if not code_id in self._code_to_track['id'] and not frame.f_code.co_name in self._code_to_track['name'] \
           and not '_do_profile' in frame.f_locals:
            return self.trace

        current_time = time.time()

        if frame in self._last_executed_code:
            last_executed_code,last_executed_line,last_executed_time = self._last_executed_code[frame]
            elapsed_time = current_time-last_executed_time

            if not last_executed_code in self._profile:
                self._profile[last_executed_code] = {}
            if not last_executed_line in self._profile[last_executed_code]:
                self._profile[last_executed_code][last_executed_line] = []

            pr = self._profile[last_executed_code][last_executed_line]

            pr.append(elapsed_time)

        if event == "line":
            self._last_executed_code[frame] = (frame.f_code,frame.f_lineno,current_time)
        else:
            if frame in self._last_executed_code:
                del self._last_executed_code[frame]

        return self.trace
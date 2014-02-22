#from tracerbullet import Tracer
import time
import sys  
import inspect
import copy


from collections import defaultdict
from cpython cimport *
from libc.stdlib cimport malloc, realloc,free
from libc.string cimport memcpy

cdef extern from "frameobject.h":
    ctypedef int (*Py_tracefunc)(object self, PyFrameObject *py_frame, int what, PyObject *arg)

cdef extern from "time.h":
    cdef double clock()
    cdef int CLOCKS_PER_SEC

cdef extern from "Python.h":
    ctypedef long long PY_LONG_LONG

    cdef void PyEval_SetTrace(Py_tracefunc func, object arg)

    # They're actually #defines, but whatever.
    cdef int PyTrace_CALL
    cdef int PyTrace_EXCEPTION
    cdef int PyTrace_LINE
    cdef int PyTrace_RETURN
    cdef int PyTrace_C_CALL
    cdef int PyTrace_C_EXCEPTION
    cdef int PyTrace_C_RETURN

cdef class Tracer(object):

    cdef public double verbose
    cdef public _profile
    cdef public _last_executed_code
    cdef public double _start_time
    cdef public _processed_profile
    cdef public double _stop_time
    cdef public _code_to_track
    cdef public _n_starts
    cdef public method

    def get_sorted_profile(self):
        sorted_profile = {}
        for filename,line_timings in self._profile.items():
            total_time = max([x[1] for x  in line_timings.values()])
            sorted_profile[filename] = {'total_time' : total_time,'line_timings' : line_timings}
        profile_items = sorted(sorted_profile.items(),key = lambda x: -x[1]['total_time'])
        return profile_items

    def __init__(self,verbose = True,trace_hierarchy = False,method = "normal"):
        self.verbose = verbose
        self.method = method
        self.reset()

    cpdef reset(self):

        self._profile = {}
        self._last_executed_code = {}
        self._start_time = 0.0
        self._n_starts = 0
        self._stop_time = 0.0
        self._code_to_track = {}

    def add_code(self,code):
        if not code in self._code_to_track:
            self._code_to_track[code] = 1

    def remove_code(self,code):
        if code in self._code_to_track:
            del self._code_to_track[code]

    def stop(self,delete_self = True):
        self._n_starts-=1
        if self._n_starts == 0:
            sys.settrace(None)
            self._processed_profile = {}

    def start(self):
        self._n_starts+=1
        if self.method == "normal":
            PyEval_SetTrace(trace_call,self)
        elif self.method == "dummy":
            PyEval_SetTrace(trace_call_dummy,self)

    def stop(self,delete_self = True):
        sys.settrace(None)

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
    def processed_profile(self):
        self.process_profile()
        return self._processed_profile

    @property
    def profile(self):
        return self._profile

    @property
    def elapsed_time(self):
        return self._stop_time - self._start_time

cdef int trace_call_dummy(object self,PyFrameObject *py_frame,int event,PyObject* arg):
    
    return 0

cdef int trace_call(object self,PyFrameObject *py_frame,int event,PyObject* arg):

    cdef double current_time
    cdef double elapsed_time

    frame = <object>py_frame

    if not frame.f_code in self._code_to_track:
        return 0

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

    if event == PyTrace_LINE:
        self._last_executed_code[frame] = (frame.f_code,frame.f_lineno,current_time)
    else:
        if frame in self._last_executed_code:
            del self._last_executed_code[frame]

    return 0

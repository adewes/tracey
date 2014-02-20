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
    cdef public double _last_time
    cdef public _last_executed_statement
    cdef public _trace_stack
    cdef public double _start_time
    cdef public double _stop_time
    cdef public trace_hierarchy
    cdef public _call_trace
    cdef public _filename_map
    cdef public _filename_index 
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
        self.trace_hierarchy = trace_hierarchy
        self.method = method
        self._last_executed_statement = None
        self._trace_stack = []
        self._call_trace = []
        self.reset()

    cpdef reset(self):

        self._profile = {}
        self._filename_map = {}
        self._filename_index = 0
        self._last_executed_statement = None
        self._last_time = 0.0
        self._call_trace = []
        self._start_time = 0.0
        self._stop_time = 0.0

    cpdef _process_trace(self):

        trace_stack = []
        last_executed_statement = None
        elapsed_time = 0
        last_time = None
        reverse_filename_map = dict([(v,k) for k,v in self._filename_map.items()])
        for (current_time,event,filename_idx,line_number,back_filename_idx,back_line_number) in self._call_trace:

            filename = reverse_filename_map[filename_idx]
            back_filename = reverse_filename_map[back_filename_idx]

            if last_time:
                elapsed_time = current_time-last_time

            last_time = current_time

            if last_executed_statement:
                fn = last_executed_statement[0]
                ln = last_executed_statement[1]
                if not fn in self._profile:
                    self._profile[fn] = {}
                if not ln in self._profile[fn]:
                    self._profile[fn][ln] = [0,0]
                cnts = self._profile[fn][ln]
                cnts[0]+=1
                cnts[1]+=elapsed_time

                if self.trace_hierarchy:
                    for fn,ln in trace_stack:

                        if not fn in self._profile:
                            self._profile[fn] = {}
                        if not ln in self._profile[fn]:
                            self._profile[fn][ln] = [0,0]#

                        cnts = self._profile[fn][ln]
                        cnts[1]+=elapsed_time


            last_executed_statement = [filename,line_number]

            if event == PyTrace_CALL or event == PyTrace_C_CALL:
                if back_filename:
                    trace_stack.append([back_filename,back_line_number])
            elif event == PyTrace_RETURN or event == PyTrace_C_RETURN:
                if back_filename != None:
                    if [back_filename,back_line_number] in trace_stack:
                        trace_stack.remove([back_filename,back_line_number])

    def start(self):
        self._start_time = clock()/CLOCKS_PER_SEC
        if self.method == "raw":
            PyEval_SetTrace(trace_call_raw,self)
        elif self.method == "normal":
            PyEval_SetTrace(trace_call,self)
        elif self.method == "dummy":
            PyEval_SetTrace(trace_call_dummy,self)


    def stop(self,delete_self = True):
        sys.settrace(None)
        self._stop_time = clock()/CLOCKS_PER_SEC
        if self.method == "raw":
            self._process_trace()
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

cdef int trace_call_raw(object self,PyFrameObject *py_frame,int event,PyObject* arg):

    cdef double current_time
    current_time = time.time()
    frame = <object>py_frame

    for fname in [frame.f_code.co_filename,frame.f_back.f_code.co_filename]:
        if not fname in self._filename_map:
            self._filename_map[fname] = self._filename_index
            self._filename_index+=1

    self._call_trace.append([current_time,event,self._filename_map[frame.f_code.co_filename],frame.f_back.f_lineno,self._filename_map[frame.f_back.f_code.co_filename],frame.f_back.f_lineno])

    return 0

cdef int trace_call_dummy(object self,PyFrameObject *py_frame,int event,PyObject* arg):
    
    return 0

cdef int trace_call(object self,PyFrameObject *py_frame,int event,PyObject* arg):

    cdef double current_time
    cdef double elapsed_time
    cdef char *filename
    cdef int line_number

    current_time = clock()/CLOCKS_PER_SEC

    frame = <object>py_frame

    if self._last_time:
        elapsed_time = current_time-self._last_time
    else:
        elapsed_time = 0

    self._last_time = current_time

    if self._last_executed_statement:
        filename = self._last_executed_statement[0]
        line_number = self._last_executed_statement[1]
        if not filename in self._profile:
            self._profile[filename] = {}
        if not line_number in self._profile[filename]:
            self._profile[filename][line_number] = [0,0]
        cnts = self._profile[filename][line_number]
        cnts[0]+=1
        cnts[1]+=elapsed_time

        if self.trace_hierarchy:
            for fn,ln in self._trace_stack:

                if not fn in self._profile:
                    self._profile[fn] = {}
                if not ln in self._profile[fn]:
                    self._profile[fn][ln] = [0,0]#

                cnts = self._profile[fn][ln]
                cnts[1]+=elapsed_time

    self._last_executed_statement = (frame.f_code.co_filename,frame.f_lineno)

    if not self.trace_hierarchy:
        return 0

    if event == PyTrace_CALL or event == PyTrace_C_CALL:
        if frame.f_back != None:
            self._trace_stack.append([frame.f_back.f_code.co_filename,frame.f_back.f_lineno])
    elif event == PyTrace_RETURN or event == PyTrace_C_RETURN:
        if frame.f_back != None:
            if [frame.f_back.f_code.co_filename,frame.f_back.f_lineno] in self._trace_stack:
                self._trace_stack.remove([frame.f_back.f_code.co_filename,frame.f_back.f_lineno])
    return 0
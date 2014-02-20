#from tracerbullet import Tracer
import time
import sys  
import inspect
import copy

from collections import defaultdict
from cpython cimport *

cdef extern from "frameobject.h":
    ctypedef int (*Py_tracefunc)(object self, PyFrameObject *py_frame, int what, PyObject *arg)

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


    def __init__(self,verbose = True):
        self.verbose = verbose
        self.reset()

    def __cinit__(self,verbose = True):
        self._last_executed_statement = None
        self._trace_stack = []

    cpdef reset(self):

        self._profile = {}
        self._last_executed_statement = None
        self._last_time = 0.0
        self._trace_stack = []
        self._start_time = 0.0
        self._stop_time = 0.0

    def start(self):
        self._start_time = time.time()
        PyEval_SetTrace(trace_call, self)

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

cdef int trace_call(object self,PyFrameObject *py_frame,int event,PyObject* arg):

    cdef double current_time
    cdef double elapsed_time
    cdef char *filename
    cdef int line_number

    current_time = time.time()

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

        for fn,ln in self._trace_stack:
            cnts = self._profile[fn][ln]
            cnts[1]+=elapsed_time

    frame = <object>py_frame

    self._last_executed_statement = (frame.f_code.co_filename,frame.f_lineno)

    if event == PyTrace_CALL or event == PyTrace_C_CALL:
        if frame.f_back != None:
            self._trace_stack.append([frame.f_back.f_code.co_filename,frame.f_back.f_lineno])
    elif event == PyTrace_RETURN or event == PyTrace_C_RETURN:
        if frame.f_back != None:
            self._trace_stack.remove([frame.f_back.f_code.co_filename,frame.f_back.f_lineno])

    return 0

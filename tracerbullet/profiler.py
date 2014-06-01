from tracerbullet.ctracer import Tracer
from functools import wraps
        
tracer = None

def get_profiler():
    global tracer
    return tracer

def set_profiler(new_tracer):
    global tracer
    tracer = new_tracer

def print_profile():
    profiler = get_profiler()
    for filename,profile in profiler.processed_profile.items():
        print filename
        for line_number,(calls,time) in sorted(profile.items(),key = lambda x:x[0]):
            print "%.3d\t: %.3f s (%d)" % (line_number,time,calls)

class profile(object):

    def __init__(self,*args,**kwargs):
        global tracer
        if not tracer:
            tracer = Tracer(*args,**kwargs)

    def __call__(self,fn):
        global tracer

        @wraps(fn)
        def profile_fn(*args,**kwargs):
            tracer.add_code(fn.__code__)
            try:
                tracer.start()
                return fn(*args,**kwargs)
            finally:
                tracer.stop()
                tracer.remove_code(fn.__code__)
                
        return profile_fn
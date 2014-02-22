from tracerbullet.ctracer import Tracer

tracer = None

def get_profiler():
    global tracer
    return tracer

def set_profiler(new_tracer):
    global tracer
    tracer = new_tracer

class profile(object):

    def __init__(self,*args,**kwargs):
        global tracer
        if not tracer:
            tracer = Tracer(*args,**kwargs)

    def __call__(self,fn):
        global tracer

        def profile_fn(*args,**kwargs):
            tracer.add_code(fn.__code__)
            try:
                tracer.start()
                res = fn(*args,**kwargs)
            finally:
                tracer.stop()
                tracer.remove_code(fn.__code__)
            return res
                
        return profile_fn
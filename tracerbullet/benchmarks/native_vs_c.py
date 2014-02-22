import tracerbullet
import time
import sys
import pprint
import os

from tracerbullet.profiler import get_profiler,set_profiler

def benchmark(filename):

    native_tracer = tracerbullet.tracer.Tracer(verbose = False)
    ctracer = tracerbullet.ctracer.Tracer(verbose = False,method = "normal",trace_hierarchy = True)

    code = compile(open(filename,"r").read(),os.path.abspath(filename),"exec")

    def benchmark_tracer(tracer):

        total_time = 0
        for i in range(0,1):
            start_time = time.time()
            if tracer:
                tracer.reset()
            set_profiler(tracer)
            lc = dict(locals().items()+{'__name__':'__main__'}.items())
            try:
                exec code in lc,lc
            except SystemExit:
                pass
            stop_time = time.time()
            total_time+=stop_time-start_time
        if tracer:
            return total_time,tracer.processed_profile
        return total_time

    native_benchmark,native_result = benchmark_tracer(native_tracer)
    ctracer_benchmark,ctracer_result = benchmark_tracer(ctracer)

    assert set(native_result.keys()) == set(ctracer_result.keys())

    reference = benchmark_tracer(None)

    print "Result:"
    pprint.pprint(ctracer_result)

    print "Natives  : %.2e" % native_benchmark
    print "C        : %.2e" % ctracer_benchmark
    print "Reference: %.2e" % reference

if __name__ == '__main__':

    filename = sys.argv[1]

    sys.argv = sys.argv[1:]

    benchmark(filename)
import tracerbullet
import time
import sys

def benchmark(filename):

    native_tracer = tracerbullet.tracer.Tracer(verbose = False)
    ctracer = tracerbullet.ctracer.Tracer(verbose = False,method = "raw",trace_hierarchy = True)

    code = open(filename,"r").read()

    def benchmark_tracer(tracer):

        total_time = 0
        for i in range(0,4000):
            start_time = time.time()
            if tracer:
                tracer.reset()
                tracer.start()
            exec code in locals(),locals()
            stop_time = time.time()
            if tracer:
                tracer.stop()
            total_time+=stop_time-start_time
        if tracer:
            return total_time,tracer.profile
        return total_time

    native_benchmark,native_result = benchmark_tracer(native_tracer)
    ctracer_benchmark,ctracer_result = benchmark_tracer(ctracer)

#    assert native_result.keys() == ctracer_result.keys()

    reference = benchmark_tracer(None)

    print "Native   : %.2e" % native_benchmark
    print "C        : %.2e" % ctracer_benchmark
    print "Reference: %.2e" % reference

if __name__ == '__main__':

    filename = sys.argv[1]

    benchmark(filename)
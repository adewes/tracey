import time
from tracerbullet.profiler import profile,get_profiler
import time
from tracerbullet.examples.test_module import bar

@profile()
def foo(i):
    bar()
    return time.sleep(0.01)

def loong_wait():
    time.sleep(0.01)
    return 1

@profile()
def calc_something():
    s = 0
    for i in range(0,20):
        foo(i)
    return s

if __name__ == '__main__':
    calc_something()
#    profiler = get_profiler()
#    print profiler.processed_profile
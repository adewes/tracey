import time
import numpy as np
from tracerbullet.profiler import profile,get_profiler
import time
from tracerbullet.examples.test_module import bar

def foo(i):
    bar()
    z = np.zeros(100)
    z[:10]+10
    return time.sleep(0.01)

def loong_wait():
    time.sleep(0.01)
    return 1

def calc_something():
    s = 0
    for i in range(0,50):
        foo(i)
    return s

if __name__ == '__main__':
    calc_something()

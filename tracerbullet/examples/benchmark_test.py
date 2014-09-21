from __future__ import absolute_import
import time
import numpy as np
import time
import pprint

from tracerbullet.examples.test_module import bar

def foo(i):
    bar()
    z = np.zeros(100)
    z[:10]+10
    return time.sleep(0.01)

def loong_wait():
    print "waiting..."
    time.sleep(0.01)
    return 1

def calc_something():
    print "calculating somethging..."
    s = 0
    for i in range(0,50):
        foo(i)
    return s

if __name__ == '__main__':
    
    calc_something()

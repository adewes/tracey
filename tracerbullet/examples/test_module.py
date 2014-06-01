import time
from tracerbullet.profiler import profile

def bar():
    assert 1+1 == 2
    return "foo!"
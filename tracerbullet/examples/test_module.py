import time
from tracerbullet.profiler import profile

#@profile()
def bar():
    assert 1+1 == 2
    return "foo!"
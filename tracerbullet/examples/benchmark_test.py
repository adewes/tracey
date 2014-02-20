import time

def foo(i):
    return i*i

def calc_something():
    s = 0
    for i in range(0,10000):
        s+=foo(i)
    return s

if __name__ == '__main__':
    calc_something()

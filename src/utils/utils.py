import sys
import time
import platform

if sys.platform == 'win32':
    default_timer = time.perf_counter
else:
    default_timer = time.time

start = 0

def startTimer():
    nonlocal start
    start = default_timer()

def endTimer():
    end = default_timer()
    elapsed = (end - start) * 1000 * 1000
    print("Runtime: {:.2f}".format(elapsed) + " ns")
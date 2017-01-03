import random
import time

from concurrent.futures import ThreadPoolExecutor

import transResponseTime
from transResponseTime import measure_time


@measure_time(immediate=False, influx_set=True)
def a_test_method(sec=0.2):
    time.sleep(sec)

if __name__ == "__main__":

    tr = transResponseTime

    #  Plain Usage Examples
    tr.measure('plain_usage_exam', time.sleep, 0.5)
    tr.get_results()

    #  Decorator Usage Examples
    ls = []
    n_treads = 50
    ex = ThreadPoolExecutor(n_treads)
    for i in range(n_treads):
        time.sleep(2)
        ls.append(ex.submit(a_test_method, random.randint(3, 10)))

    while 'running' in str(ls):
        time.sleep(1)

    tr.get_results()

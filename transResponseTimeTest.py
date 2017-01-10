#!/usr/bin/python

import random
import time

from concurrent.futures import ThreadPoolExecutor

import transResponseTime
from transResponseTime import measure_time


@measure_time()
def a_test_method(sec=0.2):
    time.sleep(sec)

if __name__ == "__main__":

    tr = transResponseTime

    #  Plain Usage Examples
    tr.measure('plain_usage_exam', time.sleep, 0.5)
    tr.get_results()

    # you can also pass argumets to the decorator.
    # @measure_time(immediate=True, store=True)

    #  Decorator Usage Examples
    # ls = []
    # n_treads = 300
    # ex = ThreadPoolExecutor(n_treads)
    # for i in range(n_treads):
    #     ls.append(ex.submit(a_test_method, random.uniform(0.5, 5)))
    #     if (len(ls) % 20) == 0:
    #         time.sleep(int(random.uniform(1.5, 2.5)))
    #
    # while 'running' in str(ls):
    #     time.sleep(1)

    # tr.get_results()

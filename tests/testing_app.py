from transResponseTime import measure_time 
import time


class TestHello(object):
    @measure_time()
    def __init__(self):
        self.x = 0
        time.sleep(0.3)

    @measure_time()
    def test_hello_m1(self):
        time.sleep(0.1)

    @measure_time()
    def test_hello_m2(self):
            time.sleep(0.1)

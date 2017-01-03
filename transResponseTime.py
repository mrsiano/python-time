"""
Transaction Utils,

the following code is a framework was writen for handle, manage, and get transaction statistics.
it also extends profilehooks, and expose some additional capabilities.

some of advantages is the ability to publish stats directly to influxDB.
"""

import time
import transInfluxClient

from multiprocessing import Lock

transactions = []  # structure is {name: (timestamp, response time)}
lock = Lock()
results_format = "%.4f"
influx = None


def send_influx(trans, timestamp, duration):
    transInfluxClient.StartInflux('localhost', 'perf').send(trans, timestamp, duration)


def get_results():
    print ["{0} : {1}, {2}".format(entry, results_format % mapper[entry][0], mapper[entry][1])
           for mapper in transactions for entry in mapper]


def measure(method_name, func_to_run=None, *args):
    """
    Context manager to log request response time
    """
    _start_time = 0
    try:
        _start_time = time.time()
        if len(args) >= 1:
            func_to_run(*args)
        else:
            func_to_run()
    except Exception as e:
        raise e
    finally:
        _duration = (time.time() - _start_time)
        send_influx(method_name, _start_time, _duration)
        store_transaction(method_name, _start_time, _duration)


def store_transaction(name=None, start_time=None, duration=None):
    trans_map = dict()
    try:
        trans_map[name] = (duration, start_time)
        with lock:
            transactions.append(trans_map)
    except Exception as e:
        print 'failed to store trans' + str(e)


def measure_time(fn=None, immediate=True, store=True, influx_set=False):
    """Wrap `fn` and print its execution time, plus handled dictionary of a transactions.

     this extends logic of profilehooks.py

     and provide more flexibility, it save the execution time and save it to a dictionary.
     it can be collected by TranResponseTime.get_results()

    """
    if fn is None:
        def decorator(fnc):
            return measure_time(fnc, immediate, store, influx_set)
        return decorator

    fp = FuncTimer(fn, immediate, store, influx_set)

    def new_fn(*args, **kw):
        return fp(*args, **kw)
    return new_fn


class FuncTimer(object):

    def __init__(self, fnc, immediate=True, store=True, influx_set=True):
        self.sfn = fnc
        self.print_now = immediate
        self.store_now = store
        self.influx = influx_set

    def __call__(self, *args, **kw):
        """Profile a singe call to the function."""
        fn = self.sfn
        start_time = None
        try:
            start_time = time.time()
            return fn(*args, **kw)
        except Exception as e:
            print 'Ops something went wrong ' + str(e)
        finally:
            _duration = time.time() - start_time
            if self.influx:
                send_influx(fn.__name__, start_time, _duration)
            if self.print_now:
                with lock:
                    print "{0} : {1} ".format(fn.__name__, results_format % _duration)
            if self.store_now:
                store_transaction(fn.__name__, start_time, _duration)


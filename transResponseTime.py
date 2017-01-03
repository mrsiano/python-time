#!/usr/bin/python

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


def singleton(class_):
    instances = {}

    def get_instance(*args, **kwargs):
        if class_ not in instances:
            with lock:
                instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return get_instance


@singleton
class TransResponse(object):
    def __init__(self):
        import ConfigParser
        config = None
        try:
            config = ConfigParser.ConfigParser(allow_no_value=True)
            config.read('config.cfg')
            if config.get('run', 'report_to_influx'):
                global influx
                influx = transInfluxClient.GetInflux(config.get('influx', 'server'), config.get('influx', 'port'),
                                                     config.get('influx', 'dbname'), config.get('influx', 'log_file'),
                                                     config.get('influx', 'log_file'), config.get('influx', 'log_file'),
                                                     config.get('influx', 'time_pattern'))
        except Exception as e:
            print e
        finally:
            del config


TransResponse()


def send_influx(trans, timestamp, duration):
    influx.send(trans, timestamp, duration)


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
        finalize(False, True, method_name, _start_time, _duration)
        # send_influx(method_name, _start_time, _duration)
        # store_transaction(method_name, _start_time, _duration)


def store_transaction(name=None, start_time=None, duration=None):
    trans_map = dict()
    try:
        trans_map[name] = (duration, start_time)
        with lock:
            transactions.append(trans_map)
    except Exception as e:
        print 'failed to store trans' + str(e)


def measure_time(fn=None, immediate=False, store=True):
    """Wrap `fn` and print its execution time, plus handled dictionary of a transactions.

     this extends logic of profilehooks.py

     and provide more flexibility, it save the execution time and save it to a dictionary.
     it can be collected by TranResponseTime.get_results()

    """
    if fn is None:
        def decorator(fnc):
            return measure_time(fnc, immediate, store)
        return decorator

    fp = FuncTimer(fn, immediate, store)

    def new_fn(*args, **kw):
        return fp(*args, **kw)
    return new_fn


def finalize(toprint, tostore, name, start_time, duration):
    if influx:
        send_influx(name, start_time, duration)
    if toprint:
        with lock:
            print "{0} : {1} ".format(name, results_format % duration)
    if tostore:
        store_transaction(name, start_time, duration)


class FuncTimer(object):

    def __init__(self, fnc, immediate=True, store=True):
        self.sfn = fnc
        self.print_now = immediate
        self.store_now = store

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
            finalize(self.print_now, self.store_now, fn.__name__, start_time, _duration)
            # if self.influx:
            #     send_influx(fn.__name__, start_time, _duration)
            # if self.print_now:
            #     with lock:
            #         print "{0} : {1} ".format(fn.__name__, results_format % _duration)
            # if self.store_now:
            #     store_transaction(fn.__name__, start_time, _duration)


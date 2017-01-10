#!/usr/bin/python

"""
Transaction Utils,

the following code is a framework was writen for handle, manage, and get transaction statistics.
it also extends profilehooks, and expose some additional capabilities.

some of advantages is the ability to publish stats directly to influxDB.
"""

import time
import psutil
import transInfluxClient

from multiprocessing import Lock

transactions = []  # structure is {name: (timestamp, response time, rec, sent)}
lock = Lock()
results_format = "%.4f"
influx = None
net_dev = 'en0'
collect_net = False


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
            if config.getboolean('run', 'collect_net_io'):
                global collect_net, net_dev
                collect_net = True
                # TODO::// may be replace it with automatic manner.
                net_dev = config.get('run', 'net_device')
            if config.getboolean('run', 'report_to_influx'):
                # TODO:// fix the log format arg.
                global influx
                influx = transInfluxClient.GetInflux(config.get('influx', 'server'), config.get('influx', 'port'),
                                             config.get('influx', 'dbname'), config.get('influx', 'log_file'),
                                             config.get('influx', 'log_level'),
                                             pattern=config.get('influx', 'time_pattern'))
        except Exception as e:
            print e
        finally:
            del config


TransResponse()


def send_influx(trans, timestamp, duration, bsent=0, brecv=0):
    try:
        influx.send(trans, timestamp, duration, bsent, brecv)
    except Exception as e:
        print e


def get_results():
    print ["{0} : {1}, {2}".format(entry, results_format % mapper[entry][0], mapper[entry][1])
           for mapper in transactions for entry in mapper]


def measure(method_name, func_to_run=None, *args):
    """
    Context manager to log request response time
    """
    _start_time = 0
    global net_dev, collect_net
    if collect_net:
        net_io_dump = psutil.net_io_counters(True).get(net_dev)
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
        if collect_net:
            net_io_dump2 = psutil.net_io_counters(True).get(net_dev)
            sent = net_io_dump2[0] - net_io_dump[0]
            recv = net_io_dump2[1] - net_io_dump[1]
        finalize(False, True, method_name, _start_time, _duration, sent, recv)


def store_transaction(name=None, start_time=None, duration=None, recive=0, sent=0):
    trans_map = dict()
    try:
        trans_map[name] = (duration, start_time, sent, recive)
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


def finalize(toprint, tostore, name, start_time, duration, sent=0, recv=0):
    global influx
    if influx:
        send_influx(name, start_time, duration, sent, recv)
    with lock:
        if toprint:
            print "{0} : {1} ".format(name, results_format % duration)
        if tostore:
            store_transaction(name, start_time, duration, sent, recv)


class FuncTimer(object):

    def __init__(self, fnc, immediate=True, store=True):
        self.sfn = fnc
        self.print_now = immediate
        self.store_now = store

    def __call__(self, *args, **kw):
        """Profile a singe call to the function."""
        global net_dev, collect_net
        fn = self.sfn
        if collect_net:
            net_io_dump = psutil.net_io_counters(True).get(net_dev)
        start_time = time.time()
        try:
            return fn(*args, **kw)
        except Exception as e:
            # TODO:// function failure needs to be handled.
            pass
        finally:
            _duration = time.time() - start_time
            if collect_net:
                net_io_dump2 = psutil.net_io_counters(True).get(net_dev)
                sent = net_io_dump2[0] - net_io_dump[0]
                recv = net_io_dump2[1] - net_io_dump[1]
            finalize(self.print_now, self.store_now, fn.__name__, start_time, _duration, sent, recv)


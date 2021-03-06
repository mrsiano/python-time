#!/usr/bin/python

"""
The following is an python parser for influxdb client.
the following module requires the following python pkgs {influxdb, concurrent.futures}
"""


import logging

from concurrent.futures import ThreadPoolExecutor
from influxdb import client


def get_time_pattern(timestamp):
    return int(str(timestamp).split('.')[0] + str(timestamp).split('.')[1] + '0000000')


def singleton(class_):
    instances = {}

    def get_instance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return get_instance


@singleton
class GetInflux(object):
    def __init__(self, server, port, db, table_name, logfile, loglevel, logformat ="%(asctime)s - %(levelname)s - %(message)s",
                 pattern=None):
        # args
        self.log = None
        self.log_level = loglevel
        self.log_format = logformat
        self.log_file = logfile
        self.pattern = pattern
        self.server = server
        self.db_name = db
        self.table_name = table_name
        self.port = port

        self.logger()
        self.influx_connection = None
        self.get_influx_client()
        self.executor = ThreadPoolExecutor(max_workers=50)
        self.running = True

    def is_running(self):
        return self.running

    def logger(self):
        try:
            logging.basicConfig(filename=self.log_file, filemode='w', level=self.log_level, format=self.log_format)
            self.log = logging.getLogger(self.log_file)
            self.log.info('starting')
        except Exception as e:
            self.log.error('failed to start log {0} - {1}'.format(self.log_file, e))

    def get_influx_client(self):
        self.influx_connection = client.InfluxDBClient(host=self.server, database=self.db_name)

    def send_influx_points(self, points):
        try:
            if self.influx_connection is None:
                self.get_influx_client()
            self.influx_connection.write_points(points)
        except Exception as e:
            self.log.error('cannot add data points {0} due to {1}'.format(points, e))

    def send(self, trans_name, timestamp, duration, sent=0, recv=0):
        try:
            json_body = [
                {
                    "measurement": self.table_name,
                    "tags": {
                        "response time": trans_name
                    },
                    "time": get_time_pattern(timestamp),
                    "fields": {
                        "value": duration,
                        "bytes_sent": sent,
                        "bytes_recv": recv
                    }
                }
            ]
            self.executor.submit(self.send_influx_points, json_body)
        except Exception as e:
            self.log.error('failed to send data points'.format(e))

    def close(self):
        self.influx_connection.close()
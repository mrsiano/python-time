#!/usr/bin/python

# The following is an python parser for influxdb client.
# the following module requires the following python pkgs {influxdb, concurrent.futures}

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
    def __init__(self, server, port, db, logfile, loglevel, logformat, pattern):
        # args
        self.log = None
        self.log_level = loglevel
        self.log_format = logformat
        self.log_file = logfile
        self.pattern = pattern
        self.server = server
        self.dbname = db
        self.port = port

        self.initialize()

        self.logger()
        self.influx_connection = None
        self.get_influx_client()
        self.executor = ThreadPoolExecutor(max_workers=50)

    def initialize(self):
        import ConfigParser
        try:
            config = ConfigParser.ConfigParser(allow_no_value=True)
            config.read('config.cfg')
            self.server = config.get('influx', 'server')
            self.dbname = config.get('influx', 'dbname')
            self.port = config.get('influx', 'port')
            self.log_level = config.get('influx', 'log_level')
            self.log_format = config.get('influx', 'log_format')
            self.log_file = config.get('influx', 'log_file')
            self.pattern = config.get('influx', 'time_pattern')
        except Exception as e:
            print e
        finally:
            del config

    def logger(self):
        try:
            logging.basicConfig(filename=self.log_file, filemode='w', level=self.log_level, format=self.log_format)
            self.log = logging.getLogger(self.log_file)
            self.log.info('starting')
        except Exception as e:
            self.log.error('failed to start log {0} - {1}'.format(self.log_file, e))

    def get_influx_client(self):
        self.influx_connection = client.InfluxDBClient(host=self.server, database=self.dbname)

    def send_influx_points(self, points):
        try:
            if self.influx_connection is None:
                self.get_influx_client()
            self.influx_connection.write_points(points)
        except Exception as e:
            self.log.error('cannot add data points {0} due to {1}'.format(points, e))

    def send(self, trans_name, timestamp, duration):
        try:
            json_body = [
                {
                    "measurement": 'response',
                    "tags": {
                        "response time": trans_name
                    },
                    "time": get_time_pattern(timestamp),
                    "fields": {
                        "value": duration
                    }
                }
            ]
            self.executor.submit(self.send_influx_points, json_body)
        except Exception as e:
            self.log.error('failed to send data points'.format(e))

    def close(self):
        self.influx_connection.close()
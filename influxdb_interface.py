#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import logging

config = configparser.ConfigParser()
config.read('conf.ini')
influx_url = config['INFLUX']['url']
influx_bucket = config['INFLUX']['bucket']
influx_org = config['INFLUX']['org']
influx_token = config['INFLUX']['token']

# create someting like this as conf.ini
# [INFLUX]
# url = http://localhost:8086
# bucket = PPMhub
# org = RPG
# token = changemechangemechangemechangeme

class influx_writer:

    def __init__(self):
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        
    def write(self, measurement, field, val, bucket=influx_bucket, timestamp=None):
        if not timestamp:
            timestamp = datetime.utcnow()
        p = Point(measurement).field(field, float(val)).time(timestamp, WritePrecision.MS)
        logging.debug('writing point to influxdb: '+str(p))
        self.write_api.write(bucket, record=p)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

config = configparser.ConfigParser()
config.read('influx_login.ini')
url = config['DEFAULT']['url']
bucket = config['DEFAULT']['bucket']
org = config['DEFAULT']['org']
token = config['DEFAULT']['token']

# create someting like this as influx_login.ini
# [DEFAULT]
# url = http://localhost:8086
# bucket = PPMhub
# org = RPG
# token = changemechangemechangemechangeme

class influx_writer:

    def __init__(self):
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        
    def write(self, measurement, field, val):
        p = Point(measurement).field(field, val).time(datetime.utcnow(), WritePrecision.MS)
        self.write_api.write(bucket, record=p)
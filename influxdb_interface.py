#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser

from influxdb_client import InfluxDBClient
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
        
    def write(self, measurement, field, value):
        self.write_api.write(bucket, org, Point(self.measurement).tag("location", "coyote_creek").field(self.field, self.value).time(1))

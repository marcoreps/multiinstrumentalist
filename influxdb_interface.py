#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

class Writer():

    def __init__(self):
        token = " "
        self.org = "reps"
        self.bucket = "ppm"
        client = InfluxDBClient(url="http://localhost:8086", token=token)
        self.write_api = client.write_api(write_options=SYNCHRONOUS)


    def write(self, tag, field, val, time=datetime.utcnow()):
        point = Point("mem").tag("device", tag).field(field, val).time(time, WritePrecision.NS)

        self.write_api.write(self.bucket, self.org, point)
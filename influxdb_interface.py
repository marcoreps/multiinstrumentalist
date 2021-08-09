#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

class Writer():

    def __init__(self):
        token = " "
        org = "reps"
        bucket = "ppm"
        client = InfluxDBClient(url="http://localhost:8086", token=token)

    def write(self, tag, field, val, time=datetime.utcnow()):
        point = Point("mem").tag("device", tag).field(field, val).time(time, WritePrecision.NS)

        write_api.write(bucket, org, point)
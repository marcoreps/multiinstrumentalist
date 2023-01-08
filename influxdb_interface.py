#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import logging

class influx_writer:

    def __init__(self, url, token, org):
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        
    def write(self, bucket, measurement, field, val, timestamp=None, tags=None):
        if not timestamp:
            timestamp = datetime.utcnow()
        logging.debug('writing point to influxdb: measurement=%s field=%s val=%s'%(str(measurement),str(field),str(val)))
        p = Point(measurement).field(field, float(val)).time(timestamp, WritePrecision.MS)
        if tags is not None:
            for t in tags:
                p.tag(t[0], t[1])
        logging.debug('point made')
        self.write_api.write(bucket, record=p)
        logging.debug('point written, writer done')
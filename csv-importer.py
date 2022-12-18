#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import csv
from influxdb_interface import influx_writer

writer=influx_writer()

with open("import.csv", "r") as f:
    reader = csv.reader(f)
    next(reader)
    for i, line in enumerate(reader):
        datetime_object = datetime.strptime(line[0], '%Y-%m-%d %H:%M:%S')
        utc=datetime_object.astimezone(datetime.timezone.utc)
        write("ADRmu107", "3458A", line[1], utc)
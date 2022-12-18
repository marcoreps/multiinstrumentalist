#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
from influxdb_interface import influx_writer


with open("import.csv", "r") as f:
    reader = csv.reader(f, delimiter="\t")
    next(reader)
    for i, line in enumerate(reader):
        print(line[0])
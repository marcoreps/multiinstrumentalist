#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import threading
from datetime import datetime

from instruments.temp_sensor import TMP117
from instruments.multimeter import *

vxi_ip = "192.168.178.88"

short_sensor = TMP117(0x48)
long_sensor = TMP117(0x49)

#bench_2001 = K2001(16)
#bench_2001.config_DCV_9digit_1000()
bench_7081 = S7081(vxi_ip, 2)
bench_6581 = R6581T(vxi_ip, 3)
bench_6581.config_DCV_9digit()
print(bench_6581.read())

with open('5700A-10V_7081drifton_6581.csv', mode='w') as csv_file:
    writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['Time','Short Temp Sensor', 'Long Temp Sensor', 'A6581T Int Temp', 'A6581T', 'S7081'])
    while True:
        writer.writerow([datetime.now(), short_sensor.read(), long_sensor.read(), bench_6581.read_int_temp(), bench_6581.read(), bench_7081.read()])
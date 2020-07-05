#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import logging
import threading
import concurrent.futures

from datetime import datetime

from instruments.temp_sensor import TMP117
from instruments.multimeter import *

logging.basicConfig(level=logging.DEBUG,  format='%(asctime)s %(levelname)-8s %(message)s')

vxi_ip = "192.168.178.88"

instruments = []
instruments.append(TMP117(address=0x48, title="Short Temp Sensor"))
instruments.append(TMP117(address=0x49, title="Long Temp Sensor"))
instruments.append(S7081(ip=vxi_ip, gpib_address=2, title="Bench S7081"))
instruments.append(R6581T(ip=vxi_ip, gpib_address=3, title="Bench R6581T"))
instruments[-1].config_DCV_9digit()
        
with open('multithread_test.csv', mode='wb') as csv_file:
    writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow([x.get_title() for x in instruments])
    while True:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for instrument in instruments:
                executor.submit(instrument.read)
            executor.shutdown(wait=True)
        writer.writerow([x.get_read_val() for x in instruments])
        csv_file.flush()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import logging
import threading
import time



from influxdb_interface import MySeriesHelper

from instruments.temperature import *
from instruments.multimeter import *
from instruments.source import *

logging.basicConfig(level=logging.DEBUG,  format='%(asctime)s %(levelname)-8s %(message)s')

gpiblock = threading.Lock()

vxi_ip = "192.168.178.88"

instruments = dict()
instruments["temp_short"]=TMP117(address=0x48, title="Short Temp Sensor")
instruments["temp_long"]=TMP117(address=0x49, title="Long Temp Sensor")
#instruments["S7081"]=S7081(ip=vxi_ip, gpib_address=2, lock=gpiblock, title="Bench S7081")
#instruments["2002"]=K2002(ip=vxi_ip, gpib_address=5, lock=gpiblock, title="2002")
#instruments["2002"].config_2ADC_9digit_filtered()
#instruments["2002"].config_20DCV_9digit_filtered()
#instruments["R6581T"]=R6581T(ip=vxi_ip, gpib_address=3, lock=gpiblock, title="Bench R6581T")
#instruments["temp_R6581T"]=R6581T_temp(r6581t=instruments["R6581T"], title="R6581T Int Temp Sensor")
#instruments["A5235"]=Arroyo(title="Arroyo 5235")
#instruments["K237"]=K237(ip=vxi_ip, gpib_address=8, lock=gpiblock, title="Bench K237")
#instruments["F5700A"]=F5700A(ip=vxi_ip, gpib_address=1, lock=gpiblock, title="Fluke 5700A")



def HPM_test():
    logging.debug('HPM_test function')
    instruments["HPM2"]=HPM7177(dev='/dev/ttyUSB0', baud=921600, nfilter=10000, title='HPM7177 Unit 2')

    while True:
        time.sleep(1)
        logging.debug('main')
        #MySeriesHelper(instrument_name=instruments["temp_short"].get_title(), value=float(instruments["temp_short"].get_read_val()))
        #MySeriesHelper(instrument_name=instruments["temp_long"].get_title(), value=float(instruments["temp_long"].get_read_val()))
        if instruments["HPM2"].is_ready_to_read():
            logging.debug(str(instruments["HPM2"].get_read_val()))

        if not instruments["HPM2"].is_measuring():
            logging.debug('starting process')
            instruments["HPM2"].measure()
        
                
HPM_test()
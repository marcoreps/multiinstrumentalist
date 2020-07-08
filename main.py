#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import logging
import threading
import concurrent.futures
import time
import numpy


from influxdb_interface import MySeriesHelper

from datetime import datetime

from instruments.temp_sensor import TMP117
from instruments.multimeter import *
from instruments.source import F5700A

logging.basicConfig(level=logging.DEBUG,  format='%(asctime)s %(levelname)-8s %(message)s')

vxi_ip = "192.168.178.88"

instruments = []
instruments.append(TMP117(address=0x48, title="Short Temp Sensor"))
instruments.append(TMP117(address=0x49, title="Long Temp Sensor"))
#instruments.append(S7081(ip=vxi_ip, gpib_address=2, title="Bench S7081"))
instruments.append(R6581T(ip=vxi_ip, gpib_address=3, title="Bench R6581T"))
instruments[-1].config_DCV_9digit()
instruments.append(R6581T_temp(r6581t=instruments[-1], title="R6581T Int Temp Sensor"))
instruments.append(F5700A(ip=vxi_ip, gpib_address=4, title="Fluke 5700A"))
     
def write_csv_forever():     
    with open('multithread_test.csv', mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow([i.get_title() for i in instruments])
        while True:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for i in instruments:
                    executor.submit(i.read)
                executor.shutdown(wait=True)
            writer.writerow([i.get_read_val() for i in instruments])
            csv_file.flush()

def write_influxdb_forever():
    while True:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for i in instruments:
                executor.submit(i.read)
            executor.shutdown(wait=True)
        for i in instruments:
            MySeriesHelper(instrument_name=i.get_title(), value=float(i.get_read_val()))
            logging.debug(i.get_title()+' processed')
        logging.debug('MySeriesHelper.commit()')
        MySeriesHelper.commit()

def inl_test():
    start = -10
    step = 0.1
    end = 10
    
    instruments[4].oper()
    instruments[4].out(str(start)+"V")
    instruments[4].rangelck()
    
    for i in numpy.arange(start,end,step):
    
        instruments[4].out(str(i)+"V")
        
        
        instruments[0].read()
        MySeriesHelper(instrument_name=instruments[0].get_title(), value=float(instruments[0].get_read_val()))
        
        instruments[1].read()
        MySeriesHelper(instrument_name=instruments[1].get_title(), value=float(instruments[1].get_read_val()))
        
        instruments[3].read()
        MySeriesHelper(instrument_name=instruments[3].get_title(), value=float(instruments[3].get_read_val()))
        
        time.sleep(2)
        
        instruments[2].read()
        R6581T_read_val = float(instruments[2].get_read_val())
        MySeriesHelper(instrument_name=instruments[2].get_title(), value=R6581T_read_val)
        MySeriesHelper(instrument_name=instruments[4].get_title(), value=i)
        MySeriesHelper(instrument_name="difference", value=R6581T_read_val-i)
        
        MySeriesHelper.commit()
        
    instruments[4].stby()
        
inl_test()


        
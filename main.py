#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import logging
import threading
import time
import numpy
from multiprocessing import Process, Lock




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
    instruments["HPM1"]=HPM7177(dev='/dev/ttyUSB0', baud=921600, nfilter=10000, title='HPM7177 Unit 1', cal1=2147448089.450398, cal2=147862000)
    instruments["HPM2"]=HPM7177(dev='/dev/ttyUSB2', baud=921600, nfilter=10000, title='HPM7177 Unit 2', cal1=2147434771.52992, cal2=148003093)

    while True:
        for i in instruments.values():
            if i.is_readable():
                MySeriesHelper(instrument_name=i.get_title(), value=float(i.get_read_val()))
        time.sleep(1)
                
                
                
def HPM_INL():
    lock = Lock()
    instruments["HPM1"]=HPM7177(lock, dev='/dev/ttyUSB0', baud=921600, nfilter=10000, title='HPM7177 Unit 1', cal1=2147448089.450398, cal2=147862000)
    instruments["HPM2"]=HPM7177(lock, dev='/dev/ttyUSB2', baud=921600, nfilter=10000, title='HPM7177 Unit 2', cal1=2147434771.52992, cal2=148003093)
    instruments["F5700A"]=F5700A(ip=vxi_ip, gpib_address=1, lock=gpiblock, title="Fluke 5700A")
    
    umin = -10
    umax = 10
    ustep = 1
    wait_settle = 5
    samples_per_step = 1
    
    instruments["F5700A"].out(str(umin)+"V")
    instruments["F5700A"].oper()
    instruments["F5700A"].rangelck()

    for u in numpy.arange(umin, umax+1, ustep):
        instruments["F5700A"].out(str(u)+"V")
        logging.debug('main setting source to '+str(u)+'V')
        time.sleep(wait_settle)

        for j in range(samples_per_step):
            for i in instruments.values():
                if not i.is_measuring():
                    i.measure()
            time.sleep(1)

            MySeriesHelper(instrument_name=instruments["temp_short"].get_title(), value=float(instruments["temp_short"].get_read_val()))
            MySeriesHelper(instrument_name=instruments["temp_long"].get_title(), value=float(instruments["temp_long"].get_read_val()))
            calibrator_out = float(instruments["F5700A"].get_read_val())
            
            while not instruments["HPM1"].is_readable():
                time.sleep(0.1)
            hpm1_out = float(instruments["HPM1"].get_read_val())
            logging.debug('main hpm1 reporting '+str(hpm1_out))
            
            while not instruments["HPM2"].is_readable():
                time.sleep(0.1)
            hpm2_out = float(instruments["HPM2"].get_read_val())
            logging.debug('main hpm2 reporting '+str(hpm2_out))
            
            MySeriesHelper(instrument_name=instruments["HPM1"].get_title(), value=hpm1_out)
            MySeriesHelper(instrument_name=instruments["HPM2"].get_title(), value=hpm2_out)
            MySeriesHelper(instrument_name=instruments["F5700A"].get_title(), value=calibrator_out)
                
            MySeriesHelper(instrument_name="hpm1 ppm", value=(hpm1_out-calibrator_out)/0.00001)
            MySeriesHelper(instrument_name="hpm2 ppm", value=(hpm2_out-calibrator_out)/0.00001)        
            

        
    MySeriesHelper.commit()
                
HPM_INL()
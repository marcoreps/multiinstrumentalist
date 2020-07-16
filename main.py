#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import logging
import threading
import time
import numpy


from influxdb_interface import MySeriesHelper

from instruments.temp_sensor import *
from instruments.multimeter import *
from instruments.source import *

logging.basicConfig(level=logging.DEBUG,  format='%(asctime)s %(levelname)-8s %(message)s')

vxi_ip = "192.168.178.88"

instruments = dict()
instruments["temp_short"]=TMP117(address=0x48, title="Short Temp Sensor")
instruments["temp_long"]=TMP117(address=0x49, title="Long Temp Sensor")
instruments["S7081"]=S7081(ip=vxi_ip, gpib_address=6, title="Bench S7081")
instruments["2002"]=K2002(ip=vxi_ip, gpib_address=5, title="2002")
#instruments["2002"].config_2ADC_9digit_filtered()
instruments["2002"].config_20DCV_9digit_filtered()
instruments["R6581T"]=R6581T(ip=vxi_ip, gpib_address=3, title="Bench R6581T")
instruments["R6581T"].config_10DCV_9digit_filtered()
#instruments["temp_R6581T"]=R6581T_temp(r6581t=instruments["R6581T"], title="R6581T Int Temp Sensor")

instruments["F5700A"]=F5700A(ip=vxi_ip, gpib_address=1, title="Fluke 5700A")


def drift():
    instruments["F5700A"].out("10V")
    instruments["F5700A"].oper()


    while True:
        time.sleep(5)
        for i in instruments.values():
            if i.is_readable():
                if i.is_ready_to_read():
                    MySeriesHelper(instrument_name=i.get_title(), value=float(i.get_read_val()))
                if not i.is_measuring():
                    t = threading.Thread(target=i.measure())
                    
def linearity():
    umin = -10
    umax = 10
    ustep = 0.1
    wait_settle = 5
    
    instruments["F5700A"].out(str(umin)+"V")
    instruments["F5700A"].oper()
    instruments["F5700A"].rangelck()
    
    for u in numpy.arange(umin, umax, ustep):
        time.sleep(wait_settle)
        for i in instruments.values():
            t = threading.Thread(target=i.measure())
            
        while not all(i.is_ready_to_read() for i in instruments.values()):
            sleep(1)
        
        for i in instruments.values():
            MySeriesHelper(instrument_name=i.get_title(), value=float(i.get_read_val()))
        instruments["F5700A"].out(str(u)+"V")
        
        
linearity()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import logging
import threading
import concurrent.futures
import time
import numpy
import sched

from timeloop import Timeloop
from datetime import timedelta

from influxdb_interface import MySeriesHelper

from datetime import datetime

from instruments.temp_sensor import *
from instruments.multimeter import *
from instruments.source import *

logging.basicConfig(level=logging.DEBUG,  format='%(asctime)s %(levelname)-8s %(message)s')

vxi_ip = "192.168.178.88"

instruments = dict()
instruments["temp_short"]=TMP117(address=0x48, title="Short Temp Sensor")
instruments["temp_long"]=TMP117(address=0x49, title="Long Temp Sensor")
instruments["S7081"]=S7081(ip=vxi_ip, gpib_address=2, title="Bench S7081")
#instruments["2002"]=K2002(ip=vxi_ip, gpib_address=5, title="2002")
#instruments["2002"].config_20DCV_9digit_filtered()
#instruments["R6581T"]=R6581T(ip=vxi_ip, gpib_address=3, title="Bench R6581T")
#instruments["R6581T"].config_10DCV_9digit_filtered()
#instruments["temp_R6581T"]=R6581T_temp(r6581t=instruments["R6581T"], title="R6581T Int Temp Sensor")
instruments["F5700A"]=F5700A(ip=vxi_ip, gpib_address=4, title="Fluke 5700A")
     
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

def R6581T_inl_test():
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
    
def S7081_inl_test():
    start = -10
    step = 0.1
    end = 10
    
    instruments[3].oper()
    instruments[3].out(str(start)+"V")
    instruments[3].rangelck()
    
    for i in numpy.arange(start,end,step):
    
        instruments[3].out(str(i)+"V")
        
        
        instruments[0].read()
        MySeriesHelper(instrument_name=instruments[0].get_title(), value=float(instruments[0].get_read_val()))
        
        instruments[1].read()
        MySeriesHelper(instrument_name=instruments[1].get_title(), value=float(instruments[1].get_read_val()))
        
        time.sleep(2)
        
        instruments[2].read()
        R6581T_read_val = float(instruments[2].get_read_val())
        MySeriesHelper(instrument_name=instruments[2].get_title(), value=R6581T_read_val)
        MySeriesHelper(instrument_name=instruments[3].get_title(), value=i)
        MySeriesHelper(instrument_name="difference", value=R6581T_read_val-i)
        
        MySeriesHelper.commit()
        
    instruments[3].stby()
    
    
    
def read_write_instrument(i):
    logging.debug('read_write_instrument started')
    i.read()
    MySeriesHelper(instrument_name=i.get_title(), value=float(i.get_read_val()))
    
    
tl = Timeloop()

@tl.job(interval=timedelta(seconds=10))
def temp_short_job():
    read_write_instrument(instruments["temp_short"])
    
@tl.job(interval=timedelta(seconds=10))
def temp_long_job():
    read_write_instrument(instruments["temp_long"])
    
@tl.job(interval=timedelta(seconds=60))
def S7081_job():
    read_write_instrument(instruments["S7081"])
    
#tl.job(interval=timedelta(seconds=60))
#def S7081_job():
#    read_write_instrument(instruments["2002"])
    

instruments["F5700A"].out("10V")
instruments["F5700A"].oper()
logging.debug('tl starting')
tl.start(block=True)
    
    
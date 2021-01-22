#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import logging
import threading
import time
import multiprocessing 



from influxdb_interface import MySeriesHelper

from instruments.temperature import *
from instruments.multimeter import *
from instruments.source import *

logging.basicConfig(level=logging.DEBUG,  format='%(asctime)s %(levelname)-8s %(message)s')

loctite = threading.Lock()

vxi_ip = "192.168.178.88"

instruments = dict()
instruments["temp_short"]=TMP117(address=0x48, title="Short Temp Sensor")
instruments["temp_long"]=TMP117(address=0x49, title="Long Temp Sensor")
#instruments["S7081"]=S7081(ip=vxi_ip, gpib_address=2, lock=loctite, title="Bench S7081")
#instruments["2002"]=K2002(ip=vxi_ip, gpib_address=5, lock=loctite, title="2002")
#instruments["2002"].config_2ADC_9digit_filtered()
#instruments["2002"].config_20DCV_9digit_filtered()
#instruments["R6581T"]=R6581T(ip=vxi_ip, gpib_address=3, lock=loctite, title="Bench R6581T")
#instruments["temp_R6581T"]=R6581T_temp(r6581t=instruments["R6581T"], title="R6581T Int Temp Sensor")
#instruments["A5235"]=Arroyo(title="Arroyo 5235")
#instruments["K237"]=K237(ip=vxi_ip, gpib_address=8, lock=loctite, title="Bench K237")
#instruments["F5700A"]=F5700A(ip=vxi_ip, gpib_address=1, lock=loctite, title="Fluke 5700A")


def v_drift():
    instruments["S7081"]=S7081(ip=vxi_ip, gpib_address=2, lock=loctite, title="Bench S7081")
    instruments["S7081"].config_10DCV_9digit()

    while True:
        time.sleep(5)
        for i in instruments.values():
            if i.is_ready_to_read():
                MySeriesHelper(instrument_name=i.get_title(), value=float(i.get_read_val()))
            if not i.is_measuring():
                t = threading.Thread(target=i.measure())
                    
def linearity():
    umin = -10
    umax = 10
    ustep = 0.05
    wait_settle = 5
    
    instruments["F5700A"].out(str(umin)+"V")
    instruments["F5700A"].oper()
    instruments["F5700A"].rangelck()
    
    for u in numpy.arange(umin, umax, ustep):
        time.sleep(wait_settle)
        for i in instruments.values():
            t = threading.Thread(target=i.measure())
            
        while not all(i.is_ready_to_read() for i in instruments.values()):
            time.sleep(1)
            
        MySeriesHelper(instrument_name=instruments["temp_short"].get_title(), value=float(instruments["temp_short"].get_read_val()))
        MySeriesHelper(instrument_name=instruments["temp_long"].get_title(), value=float(instruments["temp_long"].get_read_val()))
        MySeriesHelper(instrument_name=instruments["temp_R6581T"].get_title(), value=float(instruments["temp_R6581T"].get_read_val()))
        
        calibrator_out = float(instruments["F5700A"].get_read_val())
        S7081_out = float(instruments["S7081"].get_read_val())
        K2002_out = float(instruments["2002"].get_read_val())
        R6581T_out = float(instruments["R6581T"].get_read_val())
        
        MySeriesHelper(instrument_name=instruments["S7081"].get_title(), value=S7081_out)
        MySeriesHelper(instrument_name=instruments["2002"].get_title(), value=K2002_out)
        MySeriesHelper(instrument_name=instruments["R6581T"].get_title(), value=R6581T_out)
        MySeriesHelper(instrument_name=instruments["F5700A"].get_title(), value=calibrator_out)
            
        MySeriesHelper(instrument_name="S7081 ppm", value=(calibrator_out-S7081_out)/0.00001)
        MySeriesHelper(instrument_name="2002 ppm", value=(calibrator_out-K2002_out)/0.00001)
        MySeriesHelper(instrument_name="R6581T ppm", value=(calibrator_out-R6581T_out)/0.00001)
        
        
        instruments["F5700A"].out(str(u)+"V")
        
        
def leakage():
    instruments["K237"].oper()
    while True:
        time.sleep(5)
        for i in instruments.values():
            if i.is_ready_to_read():
                MySeriesHelper(instrument_name=i.get_title(), value=float(i.get_read_val()))
            if not i.is_measuring():
                t = threading.Thread(target=i.measure())
                
                
                
def temperature_sweep():
    Tmin = 15
    Tmax = 30
    Tstep = 0.1
    wait = 1
    while True:
        for T in numpy.arange(Tmin, Tmax, Tstep):
            instruments["A5235"].out(T)
            for i in range(0, 60):
                time.sleep(wait)
                for i in instruments.values():
                    if i.is_ready_to_read():
                        MySeriesHelper(instrument_name=i.get_title(), value=float(i.get_read_val()))
                    if not i.is_measuring():
                        t = threading.Thread(target=i.measure())
                        
        for T in numpy.arange(Tmin, Tmax, Tstep):
            instruments["A5235"].out(15+30-T)
            for i in range(0, 60):
                time.sleep(wait)
                for i in instruments.values():
                    if i.is_ready_to_read():
                        MySeriesHelper(instrument_name=i.get_title(), value=float(i.get_read_val()))
                    if not i.is_measuring():
                        t = threading.Thread(target=i.measure())
                    
            
def r_drift():
    instruments["S7081"].config_10k_9digit()
    instruments["R6581T"].config_10k4W_9digit_filtered()

    while True:
        time.sleep(1)
        for i in instruments.values():
            if i.is_ready_to_read():
                MySeriesHelper(instrument_name=i.get_title(), value=float(i.get_read_val()))
            if not i.is_measuring():
                t = threading.Thread(target=i.measure())
                
def f732a_test():
    instruments["S7081"].config_10k_9digit()
    instruments["R6581T"].config_10DCV_9digit_filtered()

    while True:
        time.sleep(1)
        for i in instruments.values():
            if i.is_ready_to_read():
                MySeriesHelper(instrument_name=i.get_title(), value=float(i.get_read_val()))
            if not i.is_measuring():
                t = threading.Thread(target=i.measure())
                
def HPM_test():
    logging.debug('HPM_test function')
    instruments["HPM2"]=HPM7177(dev='/dev/ttyUSB0', baud=921600, nfilter=10000, title='HPM7177 Unit 2')
    process = multiprocessing.Process(target=instruments["HPM2"].measure)

    while True:
        time.sleep(1)
        logging.debug('main')
        MySeriesHelper(instrument_name=instruments["temp_short"].get_title(), value=float(instruments["temp_short"].get_read_val()))
        MySeriesHelper(instrument_name=instruments["temp_long"].get_title(), value=float(instruments["temp_long"].get_read_val()))
        if instruments["HPM2"].is_ready_to_read():
            process.terminate()
        if not instruments["HPM2"].is_measuring():
            logging.debug('starting process')
            process.start()
        
                
HPM_test()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import logging
import time
import numpy
from multiprocessing import Process, Lock
import datetime
import threading
import sys






from influxdb_interface import MySeriesHelper

from instruments.sensor import *
from instruments.multimeter import *
from instruments.source import *
from instruments.switch import *


#logging.basicConfig(filename='log.log', filemode='w', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s')
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s')

gpiblock = Lock()
seriallock = Lock()
onewire_lock = Lock()

vxi_ip = "192.168.178.88"

instruments = dict()
instruments["temp_short"]=TMP117(address=0x49, title="Short Temp Sensor")
instruments["temp_long"]=TMP117(address=0x48, title="Long Temp Sensor")

#instruments["CCS811_co2"]=CCS811(title="CCS811_co2", co2_tvoc="co2")
#instruments["S7081"]=S7081(ip=vxi_ip, gpib_address=2, lock=gpiblock, title="Bench S7081")
#instruments["2002"]=K2002(ip=vxi_ip, gpib_address=5, lock=gpiblock, title="2002")
#instruments["2002"].config_2ADC_9digit_filtered()
#instruments["2002"].config_20DCV_9digit_filtered()
#instruments["R6581T"]=R6581T(ip=vxi_ip, gpib_address=3, lock=gpiblock, title="Bench R6581T")
#instruments["temp_R6581T"]=R6581T_temp(r6581t=instruments["R6581T"], title="R6581T Int Temp Sensor")
#instruments["A5235"]=Arroyo(title="Arroyo 5235")
#instruments["K237"]=K237(ip=vxi_ip, gpib_address=8, lock=gpiblock, title="Bench K237")
#instruments["F5700A"]=F5700A(ip=vxi_ip, gpib_address=1, lock=gpiblock, title="Fluke 5700A")
#instruments["HP34401A"]=HP34401A(ip=vxi_ip, gpib_address=4, lock=gpiblock, title="Bench 34401A")
#instruments["3458A"]=3458A(ip=vxi_ip, gpib_address=22, lock=gpiblock, title="3458A")


hpm1_poly = [2.71693612e-105,-6.18663036e-095,6.15667772e-085,-3.51535638e-075,1.27108774e-065,-3.03035855e-056,4.80713857e-047,-4.99468673e-038,3.24643372e-029,-1.19312049e-020,6.76492263e-009,-1.45232376e+001]
hpm2_poly = [4.90537479e-105,-1.14952913e-094,1.18668695e-084,-7.10282444e-075,2.73015673e-065,-7.05222652e-056,1.24474509e-046,-1.49570850e-037,1.19440563e-028,-6.01075982e-020,6.77344822e-009,-1.45109108e+001]



def HPM_test():
    instruments["HPM1"]=HPM7177(seriallock, hpm1_poly, dev='/dev/ttyUSB0', baud=921600, nfilter=100000, title='HPM7177 Unit 1')
    instruments["HPM2"]=HPM7177(seriallock, hpm2_poly, dev='/dev/ttyUSB1', baud=921600, nfilter=100000, title='HPM7177 Unit 2')
    instruments["HPM1_PSU_TEMP"]=HPM7177_temp(onewire_lock, "00000cc5bc07", title='HPM7177 Unit 1 PSU Temperature sensor')
    instruments["HPM2_PSU_TEMP"]=HPM7177_temp(onewire_lock, "00000cc5bc14", title='HPM7177 Unit 2 PSU Temperature sensor')
    instruments["HPM1_MEZ_TEMP"]=HPM7177_temp(onewire_lock, "00000c7454a1", title='HPM7177 Unit 1 Mezzanine Temperature sensor')
    instruments["HPM1_MAIN_TEMP"]=HPM7177_temp(onewire_lock, "00000cc5f808", title='HPM7177 Unit 1 Main module Temperature sensor')
    instruments["HPM2_MEZ_TEMP"]=HPM7177_temp(onewire_lock, "00000c745496", title='HPM7177 Unit 2 Mezzanine Temperature sensor')
    instruments["HPM2_MAIN_TEMP"]=HPM7177_temp(onewire_lock, "00000cc5f815", title='HPM7177 Unit 2 Main module Temperature sensor')

    while True:
        for i in instruments.values():
            if i.is_readable():
                MySeriesHelper(instrument_name=i.get_title(), value=float(i.get_read_val()))
        time.sleep(0.1)
                
                
                
def HPM_INL():

    instruments["HPM1"]=HPM7177(seriallock, hpm1_poly, dev='/dev/ttyUSB0', baud=921600, nfilter=10000, title='HPM7177 Unit 1')
    #instruments["HPM2"]=HPM7177(seriallock, hpm2_poly, dev='/dev/ttyUSB1', baud=921600, nfilter=10000, title='HPM7177 Unit 2')
    #instruments["HPM1_PSU_TEMP"]=HPM7177_temp(onewire_lock, "00000cc5bc07", title='HPM7177 Unit 1 PSU Temperature sensor')
    #instruments["HPM2_PSU_TEMP"]=HPM7177_temp(onewire_lock, "00000cc5bc14", title='HPM7177 Unit 2 PSU Temperature sensor')
    #instruments["HPM1_MEZ_TEMP"]=HPM7177_temp(onewire_lock, "00000c7454a1", title='HPM7177 Unit 1 Mezzanine Temperature sensor')
    #instruments["HPM1_MAIN_TEMP"]=HPM7177_temp(onewire_lock, "00000cc5f808", title='HPM7177 Unit 1 Main module Temperature sensor')
    #instruments["HPM2_MEZ_TEMP"]=HPM7177_temp(onewire_lock, "00000c745496", title='HPM7177 Unit 2 Mezzanine Temperature sensor')
    #instruments["HPM2_MAIN_TEMP"]=HPM7177_temp(onewire_lock, "00000cc5f815", title='HPM7177 Unit 2 Main module Temperature sensor')
    instruments["F5700A"]=F5700A(ip=vxi_ip, gpib_address=1, lock=gpiblock, title="Fluke 5700A")
    
    umin = -10
    umax = 10
    ustep = 0.1
    wait_settle = 5
    samples_per_step = 1
    
    instruments["F5700A"].out(str(umin)+"V")
    instruments["F5700A"].oper()
    instruments["F5700A"].rangelck()
    
    with open('csv/HPM1_formula2.csv', mode='w') as csv_file:
        fieldnames = ['vref', 'hpm1_counts']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for u in numpy.arange(umin, umax+1, ustep):
            instruments["F5700A"].out(str(u)+"V")
            logging.debug('main setting source to '+str(u)+'V')
            time.sleep(wait_settle)
            instruments["HPM1"].measure()
            #instruments["HPM2"].measure()
            

            for j in range(samples_per_step):


                MySeriesHelper(instrument_name=instruments["temp_short"].get_title(), value=float(instruments["temp_short"].get_read_val()))
                MySeriesHelper(instrument_name=instruments["temp_long"].get_title(), value=float(instruments["temp_long"].get_read_val()))
                calibrator_out = u
                
                while not instruments["HPM1"].is_readable():
                    time.sleep(0.1)
                hpm1_out = float(instruments["HPM1"].get_read_val())
                logging.debug('main hpm1 reporting '+str(hpm1_out))
                
                #while not instruments["HPM2"].is_readable():
                #    time.sleep(0.1)
                #hpm2_out = float(instruments["HPM2"].get_read_val())
                #logging.debug('main hpm2 reporting '+str(hpm2_out))
                
                MySeriesHelper(instrument_name=instruments["HPM1"].get_title(), value=hpm1_out)
                #MySeriesHelper(instrument_name=instruments["HPM2"].get_title(), value=hpm2_out)
                MySeriesHelper(instrument_name=instruments["F5700A"].get_title(), value=calibrator_out)
                    
                MySeriesHelper(instrument_name="hpm1 ppm", value=(hpm1_out-calibrator_out)/0.00001)
                #MySeriesHelper(instrument_name="hpm2 ppm", value=(hpm2_out-calibrator_out)/0.00001)    

                writer.writerow({'vref': calibrator_out, 'hpm1_counts': hpm1_out})
            

        
    MySeriesHelper.commit()
    
     

def test_3458A():
    instruments["3458A"]=HP3458A(ip=vxi_ip, gpib_address=22, lock=gpiblock, title="3458A")
    instruments["3458A"].config_10DCV_9digit()
    #instruments["3458A"].config_10OHMF_9digit()
    instruments["3458A"].blank_display()
    instruments["3458A"].config_continuous_sampling()
    HP3458A_temperature=HP3458A_temp(HP3458A=instruments["3458A"], title="HP3458A Int Temp Sensor")
    #instruments["arroyo"]=Arroyo(dev='/dev/ttyUSB0', baud=38400, title='Arroyo TECSource')
    
    instruments["3458B"]=HP3458A(ip=vxi_ip, gpib_address=23, lock=gpiblock, title="3458B")
    instruments["3458B"].config_10DCV_9digit()
    #instruments["3458B"].config_10OHMF_9digit()
    #instruments["3458B"].config_10kOHMF_9digit()
    #instruments["3458B"].blank_display()
    instruments["3458B"].config_continuous_sampling()
    HP3458B_temperature=HP3458A_temp(HP3458A=instruments["3458B"], title="HP3458B Int Temp Sensor")
    
    #instruments["HPM1"]=HPM7177(seriallock, hpm1_poly, dev='/dev/ttyUSB0', baud=921600, nfilter=100000, title='HPM7177 Unit 1')
    #instruments["HPM2"]=HPM7177(seriallock, hpm2_poly, dev='/dev/ttyUSB1', baud=921600, nfilter=100000, title='HPM7177 Unit 2')
    
    #instruments["HPM1_PSU_TEMP"]=HPM7177_temp(onewire_lock, "00000cc5bc07", title='HPM7177 Unit 1 PSU Temperature sensor')
    #instruments["HPM2_PSU_TEMP"]=HPM7177_temp(onewire_lock, "00000cc5bc14", title='HPM7177 Unit 2 PSU Temperature sensor')
    #instruments["HPM1_MEZ_TEMP"]=HPM7177_temp(onewire_lock, "00000c7454a1", title='HPM7177 Unit 1 Mezzanine Temperature sensor')
    #instruments["HPM1_MAIN_TEMP"]=HPM7177_temp(onewire_lock, "00000cc5f808", title='HPM7177 Unit 1 Main module Temperature sensor')
    #instruments["HPM2_MEZ_TEMP"]=HPM7177_temp(onewire_lock, "00000c745496", title='HPM7177 Unit 2 Mezzanine Temperature sensor')
    #instruments["HPM2_MAIN_TEMP"]=HPM7177_temp(onewire_lock, "00000cc5f815", title='HPM7177 Unit 2 Main module Temperature sensor')
    

    while True:
        now = datetime.datetime.now()
        if not(now.minute % 10) and not(now.second):
            MySeriesHelper(instrument_name=HP3458A_temperature.get_title(), value=float(HP3458A_temperature.get_read_val()))
            MySeriesHelper(instrument_name=HP3458B_temperature.get_title(), value=float(HP3458B_temperature.get_read_val()))
            time.sleep(1)
        
        for i in instruments.values():
            if i.is_readable():
                MySeriesHelper(instrument_name=i.get_title(), value=float(i.get_read_val()))
        time.sleep(0.5)
        
        
def INL_3458A():
    instruments["F5700A"]=F5700A(ip=vxi_ip, gpib_address=1, lock=gpiblock, title="Fluke 5700A")
    instruments["3458A"]=HP3458A(ip=vxi_ip, gpib_address=22, lock=gpiblock, title="3458A")
    instruments["3458A"].config_10DCV_9digit()
    instruments["S7081"]=S7081(ip=vxi_ip, gpib_address=2, lock=gpiblock, title="Bench S7081")
    instruments["S7081"].config_10DCV_9digit()
    
    umin = -10
    umax = 10
    ustep = 0.5
    wait_settle = 15
    samples_per_step = 1
    
    instruments["F5700A"].out(str(umin)+"V")
    instruments["F5700A"].oper()
    instruments["F5700A"].rangelck()
    time.sleep(180)
    
    with open('csv/3458A_INL_run3.csv', mode='w') as csv_file:
        fieldnames = ['vref', '3458A_volt', '7081_volt']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for u in numpy.arange(umin, umax+0.01, ustep):
            instruments["F5700A"].out(str(u)+"V")
            logging.debug('main setting source to '+str(u)+'V')
            time.sleep(wait_settle)
            for i in instruments.values():
                i.measure()

            for j in range(samples_per_step):
            
                while any(i.is_readable() == False for i in instruments.values()):
                    time.sleep(1)

                MySeriesHelper(instrument_name=instruments["temp_short"].get_title(), value=float(instruments["temp_short"].get_read_val()))
                MySeriesHelper(instrument_name=instruments["temp_long"].get_title(), value=float(instruments["temp_long"].get_read_val()))
                calibrator_out = u
                
                HP3458A_out = float(instruments["3458A"].get_read_val())
                S7081_out = float(instruments["S7081"].get_read_val())

                MySeriesHelper(instrument_name=instruments["3458A"].get_title(), value=HP3458A_out)
                MySeriesHelper(instrument_name=instruments["S7081"].get_title(), value=S7081_out)
                MySeriesHelper(instrument_name=instruments["F5700A"].get_title(), value=calibrator_out)
                    
                MySeriesHelper(instrument_name="3458A ppm", value=(HP3458A_out-calibrator_out)/0.00001)
                MySeriesHelper(instrument_name="7081 ppm", value=(S7081_out-calibrator_out)/0.00001)

                writer.writerow({'vref': calibrator_out, '3458A_volt': HP3458A_out, '7081_volt': S7081_out})
        
    MySeriesHelper.commit()
    
    
def temperature_sweep():

    instruments["3458A"]=HP3458A(ip=vxi_ip, gpib_address=22, lock=gpiblock, title="3458A")
    instruments["3458A"].config_10DCV_9digit()
    #instruments["3458A"].config_1OHMF_9digit()
    instruments["3458A"].config_continuous_sampling()
    HP3458A_temperature=HP3458A_temp(HP3458A=instruments["3458A"], title="HP3458A Int Temp Sensor")
    instruments["arroyo"]=Arroyo(dev='/dev/ttyUSB2', baud=38400, title='Arroyo TECSource')
    
    tmin = 30
    tmax = 90
    tstep = 1
    wait_settle = 60
    samples_per_step = 1
    
    for t in numpy.arange(tmin, tmax+0.01, tstep):
        instruments["arroyo"].out(t)
        time.sleep(wait_settle)
        now = datetime.datetime.now()
        if not(now.minute % 10) and not(now.second):
            MySeriesHelper(instrument_name=HP3458A_temperature.get_title(), value=float(HP3458A_temperature.get_read_val()))
            time.sleep(1)
        
        for i in instruments.values():
            if i.is_readable():
                MySeriesHelper(instrument_name=i.get_title(), value=float(i.get_read_val()))
        time.sleep(0.5)
        


def scanner():

# Br    N   channels[12] 732A
# BrW   P   channels[12] 732A
# Or    N   channels[13] LTZmu
# OrW   P   channels[13] LTZmu
# Bl    N   channels[14] 3458A
# BlW   P   channels[14] 3458A
# Gr    N   channels[15] 3458B
# GrW   P   channels[15] 3458B

    switch_delay = 5
    internal_timer = datetime.datetime.now()

    HP3458=HP3458A(ip=vxi_ip, gpib_address=22, lock=gpiblock, title="3458A")
    HP3458.config_10DCV_9digit()
    HP3458.blank_display()
    HP3458_temperature=HP3458A_temp(HP3458A=HP3458, title="HP3458A Int Temp Sensor")
    
    K3458B=HP3458A(ip=vxi_ip, gpib_address=23, lock=gpiblock, title="3458B")
    K3458B.config_10DCV_9digit()
    K3458B.blank_display()
    HP3458B_temperature=HP3458A_temp(HP3458A=K3458B, title="HP3458B Int Temp Sensor")
    
    switch=takovsky_scanner()
    
    switch.switchingCloseRelay(channels[14])
    
    while True:
        now = datetime.datetime.now()
        delta = now - internal_timer
        if delta.total_seconds() > 600:
            internal_timer = now
            MySeriesHelper(instrument_name=HP3458_temperature.get_title(), value=float(HP3458_temperature.get_read_val()))
            MySeriesHelper(instrument_name=HP3458B_temperature.get_title(), value=float(HP3458B_temperature.get_read_val()))
            
        for i in instruments.values():
            if i.is_readable():
                MySeriesHelper(instrument_name=i.get_title(), value=float(i.get_read_val()))
        
        # Measure 732A with 3458A
        switch.switchingCloseRelay(channels[12])
        time.sleep(switch_delay)
        HP3458.measure()
        while not HP3458.is_readable():
            time.sleep(0.1)
        MySeriesHelper(instrument_name="732A 3458A", value=float(HP3458.get_read_val()))
        switch.switchingOpenRelay(channels[14])
        
        # Measure 732A with 3458B
        switch.switchingCloseRelay(channels[15])
        time.sleep(switch_delay)
        K3458B.measure()
        while not K3458B.is_readable():
            time.sleep(0.1)
        MySeriesHelper(instrument_name="732A 3458B", value=float(K3458B.get_read_val()))
        switch.switchingOpenRelay(channels[12])
        
        # Measure LTZmu with 3458B
        switch.switchingCloseRelay(channels[13])
        time.sleep(switch_delay)
        K3458B.measure()
        while not K3458B.is_readable():
            time.sleep(0.1)
        MySeriesHelper(instrument_name="LTZmu 3458B", value=float(K3458B.get_read_val()))
        switch.switchingOpenRelay(channels[15])
        
        # Measure LTZmu with 3458A
        switch.switchingCloseRelay(channels[14])
        time.sleep(switch_delay)
        HP3458.measure()
        while not HP3458.is_readable():
            time.sleep(0.1)
        MySeriesHelper(instrument_name="LTZmu 3458A", value=float(HP3458.get_read_val()))
        switch.switchingOpenRelay(channels[13])
        
if __name__ == '__main__':
    try:
        #HPM_INL()
        #HPM_test()
        #INL_34401()
        test_3458A()
        #INL_3458A()
        #temperature_sweep()
        #scanner()
        
    except (KeyboardInterrupt, SystemExit) as exErr:
        print("\nkthxbye")
        sys.exit(0)
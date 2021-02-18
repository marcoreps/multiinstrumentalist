#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import logging
import time
import numpy
from multiprocessing import Process, Lock




from influxdb_interface import MySeriesHelper

from instruments.temperature import *
from instruments.multimeter import *
from instruments.source import *


#logging.basicConfig(filename='log.log', filemode='w', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s')
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s')

gpiblock = Lock()
seriallock = Lock()
onewire_lock = Lock()

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


hpm1_poly = [-3.51593532e-96,  6.75874660e-86, -5.62487551e-76,  2.66345177e-66, -7.94362256e-57,  1.56331493e-47, -2.07025468e-38,  1.84240813e-29, -1.06911600e-20,  6.76670027e-09, -1.45237740e+01]
hpm2_poly = [-2.08518515e-96,  3.37626791e-86, -2.10980311e-76,  5.51512175e-67,  1.68433739e-58, -5.14018299e-48,  1.51231959e-38, -2.25282568e-29,  1.88826926e-20,  6.74800382e-09, -1.45074450e+01]



def HPM_test():
    instruments["HPM1"]=HPM7177(seriallock, hpm1_poly, dev='/dev/ttyUSB0', baud=921600, nfilter=100000, title='HPM7177 Unit 1')
    #instruments["HPM2"]=HPM7177(seriallock, hpm2_poly, dev='/dev/ttyUSB1', baud=921600, nfilter=100000, title='HPM7177 Unit 2')
    #instruments["HPM1_PSU_TEMP"]=HPM7177_temp(onewire_lock, "00000cc5bc07", title='HPM7177 Unit 1 PSU Temperature sensor')
    #instruments["HPM2_PSU_TEMP"]=HPM7177_temp(onewire_lock, "00000cc5bc14", title='HPM7177 Unit 2 PSU Temperature sensor')
    #instruments["HPM1_MEZ_TEMP"]=HPM7177_temp(onewire_lock, "00000c7454a1", title='HPM7177 Unit 1 Mezzanine Temperature sensor')
    #instruments["HPM1_MAIN_TEMP"]=HPM7177_temp(onewire_lock, "00000cc5f808", title='HPM7177 Unit 1 Main module Temperature sensor')
    #instruments["HPM2_MEZ_TEMP"]=HPM7177_temp(onewire_lock, "00000c745496", title='HPM7177 Unit 2 Mezzanine Temperature sensor')
    #instruments["HPM2_MAIN_TEMP"]=HPM7177_temp(onewire_lock, "00000cc5f815", title='HPM7177 Unit 2 Main module Temperature sensor')

    while True:
        for i in instruments.values():
            if i.is_readable():
                MySeriesHelper(instrument_name=i.get_title(), value=float(i.get_read_val()))
        time.sleep(0.1)
                
                
                
def HPM_INL():

    hpm1_poly = [-3.51593532e-96,  6.75874660e-86, -5.62487551e-76,  2.66345177e-66, -7.94362256e-57,  1.56331493e-47, -2.07025468e-38,  1.84240813e-29, -1.06911600e-20,  6.76670027e-09, -1.45237740e+01]
    hpm2_poly = [-2.08518515e-96,  3.37626791e-86, -2.10980311e-76,  5.51512175e-67,  1.68433739e-58, -5.14018299e-48,  1.51231959e-38, -2.25282568e-29,  1.88826926e-20,  6.74800382e-09, -1.45074450e+01]


    #instruments["HPM1"]=HPM7177(seriallock, hpm1_poly, dev='/dev/ttyUSB0', baud=921600, nfilter=10000, title='HPM7177 Unit 1')
    instruments["HPM2"]=HPM7177(seriallock, hpm2_poly, dev='/dev/ttyUSB1', baud=921600, nfilter=10000, title='HPM7177 Unit 2')
    instruments["F5700A"]=F5700A(ip=vxi_ip, gpib_address=1, lock=gpiblock, title="Fluke 5700A")
    
    umin = -10
    umax = 10
    ustep = 0.5
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
            
            #while not instruments["HPM1"].is_readable():
            #    time.sleep(0.1)
            #hpm1_out = float(instruments["HPM1"].get_read_val())
            #logging.debug('main hpm1 reporting '+str(hpm1_out))
            
            while not instruments["HPM2"].is_readable():
                time.sleep(0.1)
            hpm2_out = float(instruments["HPM2"].get_read_val())
            logging.debug('main hpm2 reporting '+str(hpm2_out))
            
            #MySeriesHelper(instrument_name=instruments["HPM1"].get_title(), value=hpm1_out)
            MySeriesHelper(instrument_name=instruments["HPM2"].get_title(), value=hpm2_out)
            MySeriesHelper(instrument_name=instruments["F5700A"].get_title(), value=calibrator_out)
                
            #MySeriesHelper(instrument_name="hpm1 ppm", value=(hpm1_out-calibrator_out)/0.00001)
            MySeriesHelper(instrument_name="hpm2 ppm", value=(hpm2_out-calibrator_out)/0.00001)        
            

        
    MySeriesHelper.commit()
                
#HPM_INL()
HPM_test()
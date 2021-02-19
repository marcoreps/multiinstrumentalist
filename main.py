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


hpm1_poly = [ 3.86176642e-114, -9.81689143e-104,  1.11813121e-093, -7.54130050e-084,  3.35327321e-074, -1.03537079e-064,  2.27566849e-055, -3.58561312e-046,  4.01520654e-037, -3.11055187e-028,  1.57817321e-019,  6.71607803e-009, -1.45170536e+001]
hpm2_poly = [ 3.47340882e-114, -8.58353517e-104,  9.46339469e-094, -6.14901286e-084,  2.62099486e-074, -7.72021893e-065,  1.61224992e-055, -2.40818795e-046,  2.55794696e-037, -1.88808477e-028,  9.20978486e-020,  6.72969056e-009, -1.45053766e+001]



def HPM_test():
    instruments["HPM1"]=HPM7177(seriallock, hpm1_poly, dev='/dev/ttyUSB0', baud=921600, nfilter=100000, title='HPM7177 Unit 1')
    instruments["HPM2"]=HPM7177(seriallock, hpm2_poly, dev='/dev/ttyUSB1', baud=921600, nfilter=100000, title='HPM7177 Unit 2')
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


    instruments["HPM1"]=HPM7177(seriallock, hpm1_poly, dev='/dev/ttyUSB0', baud=921600, nfilter=10000, title='HPM7177 Unit 1')
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
    
    with open('inl.csv', mode='w') as csv_file:
        #fieldnames = ['vref', 'hpm1_counts', 'hpm2_counts']
        #writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        #writer.writeheader()

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

                #writer.writerow({'vref': calibrator_out, 'hpm1_counts': hpm1_out, 'hpm2_counts': hpm2_out})
            

        
    MySeriesHelper.commit()
                
HPM_INL()
#HPM_test()
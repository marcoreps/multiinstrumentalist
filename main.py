#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import logging
from time import time
import numpy
from multiprocessing import Process, Lock
import sys
import sched
import itertools


from influxdb_interface import MySeriesHelper

from instruments.sensor import *
from instruments.multimeter import *
from instruments.source import *
from instruments.switch import *


#logging.basicConfig(filename='log.log', filemode='w', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s')
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s')
logging.info("Starting ...")

gpiblock = Lock()
seriallock = Lock()
onewire_lock = Lock()

vxi_ip = "192.168.0.88"

instruments = dict()
#instruments["temp_short"]=TMP117(address=0x49, title="Short Temp Sensor")
instruments["temp_long"]=TMP117(address=0x4A, title="Long Temp Sensor")

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

    NPLC = 200

    instruments["3458A"]=HP3458A(ip=vxi_ip, gpib_address=24, lock=gpiblock, title="3458A FFY00")
    instruments["3458A"].config_10DCV_9digit()
    #instruments["3458A"].config_10OHMF_9digit()
    #instruments["3458A"].config_10kOHMF_9digit()
    #instruments["3458A"].config_1mA_9digit()
    instruments["3458A"].config_NPLC(NPLC)
    instruments["3458A"].blank_display()
    instruments["3458A"].config_trigger_auto()
    HP3458A_temperature=HP3458A_temp(HP3458A=instruments["3458A"], title="HP3458A Int Temp Sensor")
    
    #instruments["arroyo"]=Arroyo(dev='/dev/ttyUSB0', baud=38400, title='Arroyo TECSource')
    
    instruments["3458B"]=HP3458A(ip=vxi_ip, gpib_address=23, lock=gpiblock, title="3458B")
    instruments["3458B"].config_10DCV_9digit()
    #instruments["3458B"].config_10OHMF_9digit()
    #instruments["3458B"].config_10kOHMF_9digit()
    #instruments["3458B"].config_1mA_9digit()
    instruments["3458B"].config_NPLC(NPLC)
    instruments["3458B"].blank_display()
    instruments["3458B"].config_trigger_auto()
    HP3458B_temperature=HP3458A_temp(HP3458A=instruments["3458B"], title="HP3458B Int Temp Sensor")
    
    #instruments["temp_ADRmu4"]=TMP117(address=0x49, title="ADRmu4 Temp Sensor")
    
    sch = sched.scheduler(time.time, time.sleep)
    
    i = 3
    logging.info("Planning ahead: Measurements ...")
    while i < 60*60*24*2:
        sch.enter(i, 10, instruments["3458A"].trigger_once)
        sch.enter(i, 10, instruments["3458B"].trigger_once)
        i = i + NPLC * 0.05 + 0.5
        sch.enter(i, 10, read_inst_scanner, argument=(instruments["3458A"], "ADRmu2 3458A FFY00"))
        sch.enter(i, 10, read_inst_scanner, argument=(instruments["3458B"], "ADRmu4 3458B"))
        i = i + 0.5
        
    i = 0
    logging.info("Planning ahead: Temperature sensors ...")
    while i < 60*60*24*2:
        #sch.enter(i, 10, read_inst_scanner, argument=(instruments["temp_short"], "Short Temp Sensor"))
        #sch.enter(i, 10, read_inst_scanner, argument=(instruments["temp_ADRmu4"], "ADRmu4 Temp Sensor"))
        sch.enter(i, 10, read_inst_scanner, argument=(instruments["temp_long"], "Long Temp Sensor"))
        i = i+10
        
    i = 1
    logging.info("Planning ahead: Internal temp sensors ...")
    while i < 60*60*24*2:
        sch.enter(i, 10, read_inst_scanner, argument=(HP3458A_temperature, "HP3458A Int Temp Sensor"))
        sch.enter(i, 10, read_inst_scanner, argument=(HP3458B_temperature, "HP3458B Int Temp Sensor"))
        i = i+60*10
        
    i = 2
    logging.info("Planning ahead: ACALs ...")
    while i < 60*60*24*2:
        sch.enter(i, 10, acal_inst, argument=(sch, 60*60, 9, instruments["3458A"]))
        sch.enter(i, 10, acal_inst, argument=(sch, 60*60, 9, instruments["3458B"]))
        i = i+60*5
        sch.enter(i, 10, read_cal_params, argument=(instruments["3458A"], ))
        sch.enter(i, 10, read_cal_params, argument=(instruments["3458B"], ))
        i = i+60*60
        
    logging.info("Starting schedule ...")
    sch.run()
    
             
def INL_3458A():
    timestr = time.strftime("%Y%m%d-%H%M%S_")
    instruments["F5700A"]=F5700A(ip=vxi_ip, gpib_address=1, lock=gpiblock, title="PTB 5700A")
    instruments["3458A"]=HP3458A(ip=vxi_ip, gpib_address=22, lock=gpiblock, title="Reps 3458A")
    instruments["3458B"]=HP3458A(ip=vxi_ip, gpib_address=23, lock=gpiblock, title="Reps 3458B")
    instruments["3458P"]=HP3458A(ip=vxi_ip, gpib_address=24, lock=gpiblock, title="PTB 3458A")
    instruments["3458A"].config_DCV(10)
    instruments["3458A"].config_NDIG(9)
    instruments["3458A"].config_trigger_auto()
    
    instruments["3458B"].config_DCV(10)
    instruments["3458B"].config_NDIG(9)
    instruments["3458B"].config_trigger_auto()
    
    instruments["3458P"].config_DCV(10)
    instruments["3458P"].config_NDIG(9)
    instruments["3458P"].config_trigger_auto()
    
    umin = -10
    umax = 10
    ustep = 0.5
    wait_settle = 20
    samples_per_step = 1
    
    instruments["F5700A"].out(str(umin)+"V")
    instruments["F5700A"].oper()
    instruments["F5700A"].rangelck()
    time.sleep(180)
    
    with open('csv/'+timestr+'REPS5700A_PTB3458A_3458A_3458B_INL.csv', mode='w') as csv_file:
        fieldnames = ['vref', '3458A_volt', '3458B_volt', '3458P_volt']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for u in numpy.arange(umin, umax+0.01, ustep):
            instruments["F5700A"].out(str(u)+"V")
            logging.debug('main setting source to '+str(u)+'V')
            instruments["3458A"].config_NPLC(10)
            instruments["3458B"].config_NPLC(10)
            instruments["3458P"].config_NPLC(10)
            instruments["3458A"].config_trigger_auto()
            instruments["3458B"].config_trigger_auto()
            instruments["3458P"].config_trigger_auto()
            time.sleep(wait_settle)
            instruments["3458A"].config_NPLC(100)
            instruments["3458P"].config_NPLC(100)
            instruments["3458B"].config_NPLC(100)
            instruments["3458A"].config_trigger_hold()
            instruments["3458B"].config_trigger_hold()
            instruments["3458P"].config_trigger_hold()
            
            for i in instruments.values():
                i.measure()

            for j in range(samples_per_step):
            
                while any(i.is_readable() == False for i in instruments.values()):
                    time.sleep(1)

                #MySeriesHelper(instrument_name=instruments["temp_short"].get_title(), value=float(instruments["temp_short"].get_read_val()))
                MySeriesHelper(instrument_name=instruments["temp_long"].get_title(), value=float(instruments["temp_long"].get_read_val()))
                calibrator_out = u
                
                HP3458A_out = float(instruments["3458A"].get_read_val())
                HP3458B_out = float(instruments["3458B"].get_read_val())
                HP3458P_out = float(instruments["3458P"].get_read_val())

                MySeriesHelper(instrument_name=instruments["3458A"].get_title(), value=HP3458A_out)
                MySeriesHelper(instrument_name=instruments["3458B"].get_title(), value=HP3458B_out)
                MySeriesHelper(instrument_name=instruments["3458P"].get_title(), value=HP3458P_out)
                MySeriesHelper(instrument_name=instruments["F5700A"].get_title(), value=calibrator_out)
                    
                MySeriesHelper(instrument_name="3458A ppm", value=(HP3458A_out-calibrator_out)/0.00001)
                MySeriesHelper(instrument_name="3458B ppm", value=(HP3458B_out-calibrator_out)/0.00001)
                MySeriesHelper(instrument_name="3458P ppm", value=(HP3458P_out-calibrator_out)/0.00001)

                writer.writerow({'vref': calibrator_out, '3458A_volt': HP3458A_out, '3458B_volt': HP3458B_out, '3458P_volt': HP3458P_out})
        
    MySeriesHelper.commit()

def temperature_sweep():


    instruments["3458A"]=HP3458A(ip=vxi_ip, gpib_address=22, lock=gpiblock, title="3458A LTZheater")
    instruments["3458A"].config_DCV(10)
    instruments["3458A"].config_NDIG(9)
    instruments["3458A"].config_NPLC(50)
    instruments["3458A"].config_trigger_auto()
    
    instruments["arroyo"]=Arroyo(dev='/dev/ttyUSB0', baud=38400, title='Arroyo TECSource')
    
    instruments["3458B"]=HP3458A(ip=vxi_ip, gpib_address=23, lock=gpiblock, title="3458B Vz")
    instruments["3458B"].config_DCV(10)
    instruments["3458B"].config_NDIG(9)
    instruments["3458B"].config_NPLC(50)
    instruments["3458B"].config_trigger_auto()
    
    tmin = 15
    tmax = 40
    tstep = 0.1
    wait_settle = 10

    sch = sched.scheduler(time.time, time.sleep)
    sch.enter(1, 10, recursive_read_inst, argument=(sch, 2, 10, instruments["3458A"]))
    sch.enter(1, 10, recursive_read_inst, argument=(sch, 2, 10, instruments["3458B"]))
    sch.enter(1, 10, recursive_read_inst, argument=(sch, 2, 10, instruments["arroyo"]))
    i=0
    for t in numpy.arange(tmin, tmax+0.01, tstep):
    #for t in numpy.flip(numpy.arange(tmin, tmax+0.01, tstep)):
        i+=1
        sch.enter(i*wait_settle, 9, instruments["arroyo"].out, argument=([t]))
    sch.run()

def read_inst_scanner(inst, title):
    if inst.is_readable():
        MySeriesHelper(instrument_name=title, value=float(inst.get_read_val()))
    else:
        logging.info(inst.get_title()+' was not readable')

def scanner():

# III   Br    N   channels[0] ADRmu1 +
# III   BrW   P   channels[0] ADRmu1 -
# III   Or    N   channels[1] ADRmu2 +
# III   OrW   P   channels[1] ADRmu2 -
# III   Bl    N   channels[2] ADRmu3 +
# III   BlW   P   channels[2] ADRmu3 -
# III   Gr    N   channels[3] ADRmu4 +
# III   GrW   P   channels[3] ADRmu4 -

# IV    Br    N   channels[4] 3458A +
# IV    BrW   P   channels[4] 3458A -
# IV    Or    N   channels[5] 3458B +
# IV    OrW   P   channels[5] 3458B -
# IV    Bl    N   channels[6] 
# IV    BlW   P   channels[6] 
# IV    Gr    N   channels[7] 
# IV    GrW   P   channels[7] 

    switch_delay = 5
    NPLC = 200
    runtime = 60*60*24*2

    #instruments["temp_ADRmu1"]=TMP117(address=0x48, title="ADRmu1 Temp Sensor")
    #instruments["temp_ADRmu2"]=TMP117(address=0x4B, title="ADRmu2 Temp Sensor")
    #instruments["temp_ADRmu3"]=TMP117(address=0x4A, title="ADRmu3 Temp Sensor")
    #instruments["temp_ADRmu4"]=TMP117(address=0x49, title="ADRmu4 Temp Sensor")
    
    instruments["3458A"]=HP3458A(ip=vxi_ip, gpib_address=22, lock=gpiblock, title="3458A")
    instruments["3458A"].config_DCV(10)
    instruments["3458A"].config_NDIG(9)
    instruments["3458A"].config_NPLC(NPLC)
    instruments["3458A"].blank_display()
    instruments["3458A"].config_trigger_hold()
    HP3458A_temperature=HP3458A_temp(HP3458A=instruments["3458A"], title="HP3458A Int Temp Sensor")
    
    instruments["3458B"]=HP3458A(ip=vxi_ip, gpib_address=23, lock=gpiblock, title="3458B")
    instruments["3458B"].config_DCV(10)
    instruments["3458B"].config_NDIG(9)
    instruments["3458B"].config_NPLC(NPLC)
    instruments["3458B"].blank_display()
    instruments["3458B"].config_trigger_hold()
    HP3458B_temperature=HP3458A_temp(HP3458A=instruments["3458B"], title="HP3458B Int Temp Sensor")
    
    scanner_sources = [(channels[0], "ADRmu1"), (channels[1], "ADRmu2"), (channels[2], "ADRmu3"), (channels[3], "ADRmu4")]
    scanner_meters = [(channels[4], instruments["3458A"]), (channels[5], instruments["3458B"])]

    switch=takovsky_scanner()
    
    sch = sched.scheduler(time.time, time.sleep)
    
    scanner_permutations = list(itertools.product(scanner_sources, scanner_meters))

    seconds = 1
    i = 0

    while seconds < runtime:
        j = i%len(scanner_permutations)
        sch.enter(seconds, 10, switch.switchingCloseRelay, argument=(scanner_permutations[j][0][0],)) # Close source
        sch.enter(seconds, 10, switch.switchingCloseRelay, argument=(scanner_permutations[j][1][0],)) # Close meter
        seconds = seconds + switch_delay
        sch.enter(seconds, 10, scanner_permutations[j][1][1].trigger_once)
        seconds = seconds + NPLC * 0.04 + 0.1
        sch.enter(seconds, 10, read_inst_scanner, argument=(scanner_permutations[j][1][1], scanner_permutations[j][0][1]+" "+scanner_permutations[j][1][1].get_title()))
        sch.enter(seconds, 10, switch.switchingOpenRelay, argument=(scanner_permutations[j][0][0],)) # Open source
        sch.enter(seconds, 10, switch.switchingOpenRelay, argument=(scanner_permutations[j][1][0],)) # Open meter
        i=i+1
        
    seconds = 0
    while seconds < runtime:
        sch.enter(seconds, 9, read_cal_params, argument=(instruments["3458A"],))
        sch.enter(seconds, 9, read_cal_params, argument=(instruments["3458B"],))
        seconds = seconds + 1
        sch.enter(seconds, 9, acal_inst, argument=(sch, 60*60, 9, instruments["3458A"]))
        sch.enter(seconds, 9, acal_inst, argument=(sch, 60*60, 9, instruments["3458B"]))
        seconds = seconds + 200
        sch.enter(seconds, 9, instruments["3458A"].blank_display)
        sch.enter(seconds, 9, instruments["3458B"].blank_display)
        seconds = seconds + 60*60*2
        
    
    #sch.enter(1, 11, recursive_read_inst, argument=(sch, 1, 11, instruments["temp_short"]))
    sch.enter(10, 11, recursive_read_inst, argument=(sch, 10, 11, instruments["temp_long"]))
    #sch.enter(1, 11, recursive_read_inst, argument=(sch, 1, 11, instruments["temp_ADRmu1"]))
    #sch.enter(1, 11, recursive_read_inst, argument=(sch, 1, 11, instruments["temp_ADRmu2"]))
    sch.enter(61*10, 9, recursive_read_inst, argument=(sch, 61*10, 9, HP3458A_temperature))
    sch.enter(61*10, 9, recursive_read_inst, argument=(sch, 61*10, 9, HP3458B_temperature))
    sch.run()


def auto_ACAL_3458A():
    
    instruments["3458B"]=HP3458A(ip=vxi_ip, gpib_address=23, lock=gpiblock, title="3458B")
    instruments["3458B"].config_10DCV_9digit()
    #instruments["3458B"].config_10OHMF_9digit()
    #instruments["3458B"].config_10kOHMF_9digit()
    instruments["3458B"].config_NPLC100()
    instruments["3458B"].blank_display()
    instruments["3458B"].config_trigger_auto()
    HP3458B_temperature=HP3458A_temp(HP3458A=instruments["3458B"], title="HP3458B Int Temp Sensor")
    last_temp = instruments["temp_short"].get_read_val()

    while True:
        now = datetime.datetime.now()
        if not(now.minute % 10) and not(now.second) and instruments["3458B"].is_readable():
            MySeriesHelper(instrument_name=HP3458B_temperature.get_title(), value=float(HP3458B_temperature.get_read_val()))
            time.sleep(1)
        temperature = instruments["temp_short"].get_read_val()
        logging.debug("Actual Temp = %s   Last ACAL temp = %s" % (temperature, last_temp))
        if abs(last_temp - temperature) > 1:
            instruments["3458B"].acal_DCV()
            time.sleep(80)
            last_temp = instruments["temp_short"].get_read_val()

        for i in instruments.values():
            if i.is_readable():
                MySeriesHelper(instrument_name=i.get_title(), value=float(i.get_read_val()))
        time.sleep(1)
        
def scanner2():

# III   Br    N   channels[0] ADRmu1 +
# III   BrW   P   channels[0] ADRmu1 -
# III   Or    N   channels[1] ADRmu2 +
# III   OrW   P   channels[1] ADRmu2 -
# III   Bl    N   channels[2] ADRmu3 +
# III   BlW   P   channels[2] ADRmu3 -
# III   Gr    N   channels[3] ADRmu4 +
# III   GrW   P   channels[3] ADRmu4 -

# IV    Br    N   channels[4] 
# IV    BrW   P   channels[4] 
# IV    Or    N   channels[5] 
# IV    OrW   P   channels[5] 
# IV    Bl    N   channels[6] 3458A +
# IV    BlW   P   channels[6] 3458A -
# IV    Gr    N   channels[7] 3458B +
# IV    GrW   P   channels[7] 3458B -

    switch_delay = 5
    NPLC = 1000
    runtime = 60*60*24*7

    #instruments["temp_ADRmu1"]=TMP117(address=0x48, title="ADRmu1 Temp Sensor")
    #instruments["temp_ADRmu2"]=TMP117(address=0x4B, title="ADRmu2 Temp Sensor")
    #instruments["temp_ADRmu3"]=TMP117(address=0x4A, title="ADRmu3 Temp Sensor")
    #instruments["temp_ADRmu4"]=TMP117(address=0x49, title="ADRmu4 Temp Sensor")
    
    instruments["3458A"]=HP3458A(ip=vxi_ip, gpib_address=22, lock=gpiblock, title="3458A")
    instruments["3458A"].config_DCV(10)
    instruments["3458A"].config_NDIG(9)
    instruments["3458A"].config_NPLC(NPLC)
    instruments["3458A"].blank_display()
    instruments["3458A"].config_trigger_hold()
    HP3458A_temperature=HP3458A_temp(HP3458A=instruments["3458A"], title="HP3458A Int Temp Sensor")
    
    instruments["3458B"]=HP3458A(ip=vxi_ip, gpib_address=23, lock=gpiblock, title="3458B")
    instruments["3458B"].config_DCV(10)
    instruments["3458B"].config_NDIG(9)
    instruments["3458B"].config_NPLC(NPLC)
    instruments["3458B"].blank_display()
    instruments["3458B"].config_trigger_hold()
    HP3458B_temperature=HP3458A_temp(HP3458A=instruments["3458B"], title="HP3458B Int Temp Sensor")
    
    scanner_sources = [(channels[0], "ADRmu1"), (channels[1], "ADRmu2"), (channels[2], "ADRmu3"), (channels[3], "ADRmu4")]
    scanner_meters = [(channels[6], instruments["3458A"]), (channels[7], instruments["3458B"])]

    switch=takovsky_scanner()
    
    sch = sched.scheduler(time.time, time.sleep)
    
    scanner_permutations = list(itertools.product(scanner_sources, scanner_meters))

    seconds = 60*5+60*60*4
    i = 0

    while seconds < runtime:
        for perm in scanner_permutations:
            sch.enter(seconds, 10, switch.switchingCloseRelay, argument=(perm[0][0],)) # Close source
            sch.enter(seconds, 10, switch.switchingCloseRelay, argument=(perm[1][0],)) # Close meter
            seconds = seconds + switch_delay
            sch.enter(seconds, 10, perm[1][1].trigger_once)
            seconds = seconds + NPLC * 0.04 + 0.1
            sch.enter(seconds, 10, read_inst_scanner, argument=(perm[1][1], perm[0][1]+" "+perm[1][1].get_title()))
            sch.enter(seconds, 10, switch.switchingOpenRelay, argument=(perm[0][0],)) # Open source
            sch.enter(seconds, 10, switch.switchingOpenRelay, argument=(perm[1][0],)) # Open meter
        seconds = seconds + 60*60*24
        
    seconds = 60*60*4
    while seconds < runtime:
        sch.enter(seconds, 9, acal_inst, argument=(sch, 60*60, 9, instruments["3458A"]))
        sch.enter(seconds, 9, acal_inst, argument=(sch, 60*60, 9, instruments["3458B"]))
        seconds = seconds + 300
        sch.enter(seconds, 9, read_cal_params, argument=(instruments["3458A"],))
        sch.enter(seconds, 9, read_cal_params, argument=(instruments["3458B"],))
        seconds = seconds + 1
        sch.enter(seconds, 9, instruments["3458A"].blank_display)
        sch.enter(seconds, 9, instruments["3458B"].blank_display)
        seconds = seconds + 60*60*24
        
    
    #sch.enter(1, 11, recursive_read_inst, argument=(sch, 1, 11, instruments["temp_short"]))
    sch.enter(10, 11, recursive_read_inst, argument=(sch, 10, 11, instruments["temp_long"]))
    #sch.enter(1, 11, recursive_read_inst, argument=(sch, 1, 11, instruments["temp_ADRmu1"]))
    #sch.enter(1, 11, recursive_read_inst, argument=(sch, 1, 11, instruments["temp_ADRmu2"]))
    #sch.enter(61*10, 9, recursive_read_inst, argument=(sch, 61*10, 9, HP3458A_temperature))
    #sch.enter(61*10, 9, recursive_read_inst, argument=(sch, 61*10, 9, HP3458B_temperature))
    sch.run()
     
def recursive_read_inst(sch, interval, priority, inst):
    sch.enter(interval, priority, recursive_read_inst, argument=(sch, interval, priority, inst))
    if inst.is_readable():
        MySeriesHelper(instrument_name=inst.get_title(), value=float(inst.get_read_val()))
        
def read_cal_params(inst):
    while not inst.is_ready():
        logging.info("%s was not ready for read_cal_params." % (inst.get_title()))
        time.sleep(1)
    MySeriesHelper(instrument_name=inst.get_title()+" CAL? 72", value=float(inst.get_cal_72()))
    MySeriesHelper(instrument_name=inst.get_title()+" CAL? 73", value=float(inst.get_cal_73()))
    MySeriesHelper(instrument_name=inst.get_title()+" CAL? 175", value=float(inst.get_cal_175()))
        
def acal_inst(sch, interval, priority, inst):
    while not inst.is_ready():
        logging.info("%s was not ready for acal_inst." % (inst.get_title()))
        time.sleep(1)
    inst.acal_DCV()
    read_cal_params

def log_3458A_calparams():

    #instruments["temp_ADRmu1"]=TMP117(address=0x48, title="ADRmu1 Temp Sensor")
    instruments["temp_ADRmu2"]=TMP117(address=0x4B, title="ADRmu2 Temp Sensor")
    
    #instruments["3458A"]=HP3458A(ip=vxi_ip, gpib_address=22, lock=gpiblock, title="3458A")
    instruments["3458A"]=HP3458A(ip=vxi_ip, gpib_address=22, lock=gpiblock, title="ADRmu2 3458A")
    instruments["3458A"].config_10DCV_9digit()
    #instruments["3458A"].config_10OHMF_9digit()
    #instruments["3458A"].config_10kOHMF_9digit()
    instruments["3458A"].config_NPLC(200)
    instruments["3458A"].blank_display()
    instruments["3458A"].config_trigger_auto()
    HP3458A_temperature=HP3458A_temp(HP3458A=instruments["3458A"], title="HP3458A Int Temp Sensor")
    
    instruments["3458B"]=HP3458A(ip=vxi_ip, gpib_address=23, lock=gpiblock, title="ADRmu2 3458B")
    instruments["3458B"].config_10DCV_9digit()
    #instruments["3458B"].config_10OHMF_9digit()
    #instruments["3458B"].config_10kOHMF_9digit()
    instruments["3458B"].config_NPLC(200)
    instruments["3458B"].blank_display()
    instruments["3458B"].config_trigger_auto()
    HP3458B_temperature=HP3458A_temp(HP3458A=instruments["3458B"], title="HP3458B Int Temp Sensor")
    
    sch = sched.scheduler(time.time, time.sleep)
    sch.enter(2, 10, read_inst, argument=(sch, 2, 10, instruments["3458A"]))
    sch.enter(2, 10, read_inst, argument=(sch, 2, 10, instruments["3458B"]))
    sch.enter(1, 11, read_inst, argument=(sch, 1, 11, instruments["temp_short"]))
    sch.enter(1, 11, read_inst, argument=(sch, 1, 11, instruments["temp_long"]))
    #sch.enter(1, 11, read_inst, argument=(sch, 1, 11, instruments["temp_ADRmu1"]))
    sch.enter(1, 11, read_inst, argument=(sch, 1, 11, instruments["temp_ADRmu2"]))
    sch.enter(61*10, 9, read_inst, argument=(sch, 61*10, 9, HP3458A_temperature))
    sch.enter(61*10, 9, read_inst, argument=(sch, 61*10, 9, HP3458B_temperature))
    sch.enter(60*60, 8, acal_inst, argument=(sch, 60*60, 8, instruments["3458A"]))
    sch.enter(60*60, 8, acal_inst, argument=(sch, 60*60, 8, instruments["3458B"]))
    sch.run()   
    
def noise_3458A():

    seconds_per_step=60*20

    instruments["3458A"]=HP3458A(ip=vxi_ip, gpib_address=22, lock=gpiblock, title="3458A")
    instruments["3458A"].config_10DCV_9digit()
    #instruments["3458A"].config_10OHMF_9digit()
    #instruments["3458A"].config_10kOHMF_9digit()
    #instruments["3458A"].config_1mA_9digit()
    instruments["3458A"].blank_display()
    instruments["3458A"].config_trigger_auto()
    HP3458A_temperature=HP3458A_temp(HP3458A=instruments["3458A"], title="HP3458A Int Temp Sensor")
    
    instruments["3458B"]=HP3458A(ip=vxi_ip, gpib_address=23, lock=gpiblock, title="3458B")
    instruments["3458B"].config_10DCV_9digit()
    #instruments["3458B"].config_10OHMF_9digit()
    #instruments["3458B"].config_10kOHMF_9digit()
    #instruments["3458B"].config_1mA_9digit()
    instruments["3458B"].blank_display()
    instruments["3458B"].config_trigger_auto()
    HP3458B_temperature=HP3458A_temp(HP3458A=instruments["3458B"], title="HP3458B Int Temp Sensor")
    
    NPLCs = [0.1, 1, 10, 50, 100, 500, 1000]
    
    with open('csv/3458A_vs_B_noise.csv', mode='w') as csv_file:
        fieldnames = ['NPLC', '3458A_reading', '3458B_reading']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        
        for NPLC in NPLCs:
            logging.info("NPLC "+str(NPLC))
            instruments["3458A"].config_NPLC(NPLC)
            instruments["3458B"].config_NPLC(NPLC)
            start = datetime.datetime.now()
            deltat = datetime.datetime.now() - start
            while deltat.seconds < seconds_per_step:
                #while not instruments["3458A"].is_readable():
                    #time.sleep(0.1)
                readingA = instruments["3458A"].get_read_val()
                #while not instruments["3458B"].is_readable():
                    #time.sleep(0.1)
                readingB = instruments["3458B"].get_read_val()
                logging.debug( str(NPLC) + "," + str(readingA) + "," + str(readingB) )
                writer.writerow({'NPLC': NPLC, '3458A_reading': readingA, '3458B_reading': readingB})
                deltat = datetime.datetime.now() - start
                
def pt100_scanner():

    # III   Br    N   channels[0] CH1
    # III   BrW   P   channels[0] CH1
    # III   Or    N   channels[1] CH2
    # III   OrW   P   channels[1] CH2
    # III   Bl    N   channels[2] CH3
    # III   BlW   P   channels[2] CH3
    # III   Gr    N   channels[3] CH4
    # III   GrW   P   channels[3] CH4

    # IV    Br    N   channels[4] CH5
    # IV    BrW   P   channels[4] CH5
    # IV    Or    N   channels[5] CH6
    # IV    OrW   P   channels[5] CH6
    # IV    Bl    N   channels[6] CH7
    # IV    BlW   P   channels[6] CH7
    # IV    Gr    N   channels[7] CH8
    # IV    GrW   P   channels[7] CH8
    
    # IV    Br    N   channels[8] CH9
    # IV    BrW   P   channels[8] CH9
    # IV    Or    N   channels[9] CH10
    # IV    OrW   P   channels[9] CH10
    # IV    Bl    N   channels[10] CH11
    # IV    BlW   P   channels[10] CH11
    # IV    Gr    N   channels[11] 3458B
    # IV    GrW   P   channels[11] 3458B
    
    switch_delay=0

    switch=takovsky_scanner()
    
    instruments["3458B"]=HP3458A(ip=vxi_ip, gpib_address=23, lock=gpiblock, title="3458B")
    instruments["3458B"].config_PT100_2W()
    instruments["3458B"].config_trigger_hold()
    
    switch.switchingCloseRelay(channels[11]) # Connect 3458B    
    
    while True:
        for i in range(11):
            if i == 0:
                switch.switchingOpenRelay(channels[10])
            else:
                switch.switchingOpenRelay(channels[i-1])
            switch.switchingCloseRelay(channels[i])

            time.sleep(switch_delay)
            instruments["3458B"].trigger_once()
            MySeriesHelper(instrument_name="PT100 Ch"+str(i+1), value=float(instruments["3458B"].get_read_val()))

def readstb_test():

    NPLC = 200
    
    instruments["3458A"]=HP3458A(ip=vxi_ip, gpib_address=22, lock=gpiblock, title="3458A")
    instruments["3458A"].config_DCV(10)
    #instruments["3458A"].config_10OHMF_9digit()
    #instruments["3458A"].config_10kOHMF_9digit()
    instruments["3458A"].config_NDIG(9)
    instruments["3458A"].config_NPLC(NPLC)
    instruments["3458A"].blank_display()
    instruments["3458A"].config_trigger_hold()
    HP3458A_temperature=HP3458A_temp(HP3458A=instruments["3458A"], title="HP3458A Int Temp Sensor")
    
    while True:
        print(instruments["3458A"].is_ready())
        time.sleep(0.1)

if __name__ == '__main__':
    try:
        #HPM_INL()
        #HPM_test()
        #INL_34401()
        #test_3458A()
        #INL_3458A()
        temperature_sweep()
        #scanner2()
        #auto_ACAL_3458A()
        #log_3458A_calparams()
        #noise_3458A()
        #pt100_scanner()
        #readstb_test()
        
    except (KeyboardInterrupt, SystemExit) as exErr:
        logging.info("kthxbye")
        sys.exit(0)
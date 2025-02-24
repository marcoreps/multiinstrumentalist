#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyvisa
import csv
import logging
from time import time
import numpy
import sys
import sched
import itertools
import configparser
import datetime
import random
import statistics
from decimal import Decimal

from instruments.sensor import *
from instruments.multimeter import *
from instruments.source import *
from instruments.switch import *

from influxdb_interface import influx_writer

config = configparser.ConfigParser()
config.read('conf.ini')
influx_url = config['INFLUX']['url']
influx_token = config['INFLUX']['token']
influx_org = config['INFLUX']['org']

writer=influx_writer(influx_url, influx_token, influx_org)

#logging.basicConfig(filename='log.log', filemode='w', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s')
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s')
logging.info("Starting ...")

instruments = dict()
rm = pyvisa.ResourceManager()

def test_3458A():
    NPLC = 100
    instruments["3458B"]=HP3458A(rm, 'TCPIP::192.168.178.65::gpib0,23', title='3458B')
    instruments["3458B"].config_DCV(10)
    instruments["3458B"].config_NDIG(9)
    instruments["3458B"].config_NPLC(NPLC)
    instruments["3458B"].config_trigger_auto()

    while(True):
        print(instruments["3458B"].get_read_val())

        
        
def test_W4950():
    instruments["W4950"]=W4950(ip=vxi_ip, gpib_address=9)
    instruments["W4950"].config_trigger_hold()
    instruments["W4950"].config_accuracy("HIGH")
    
    timestr = time.strftime("%Y%m%d-%H%M%S_")
    with open('csv/'+timestr+'4950_10V_HIACC_short.csv', mode='w') as csv_file:
        fieldnames = ['time', 'W4950_volt']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
    
        while True:
            instruments["W4950"].trigger_once()
            val = float(instruments["W4950"].get_read_val())
            print(val)
            writer.writerow({'time':time.time(), 'W4950_volt': val})
            
def INL_3458A():
    timestr = time.strftime("%Y%m%d-%H%M%S_")
    
    umin = -10.25
    umax = 10.25
    ustep = 0.25
    wait_settle = 20
    samples_per_meter_per_step = 1
    NPLC = 317
    
    instruments["F5700A"]=F5700A(rm, 'gpib0::1::INSTR', title='5700A')
    instruments["F5700A"].out(str(umin)+"V")
    instruments["F5700A"].oper()
    instruments["F5700A"].rangelck()
    
    instruments["3458A"]=HP3458A(rm, 'gpib0::22::INSTR', title='3458A')
    instruments["3458A"].config_DCV(10)
    instruments["3458A"].config_NDIG(9)
    instruments["3458A"].config_NPLC(NPLC)
    instruments["3458A"].config_trigger_auto()
    
    instruments["3458B"]=HP3458A(rm, 'gpib0::23::INSTR', title='3458B')
    instruments["3458B"].config_DCV(10)
    instruments["3458B"].config_NDIG(9)
    instruments["3458B"].config_NPLC(NPLC)
    instruments["3458B"].config_trigger_auto()
    
    instruments["8508A"]=F8508A(rm, 'gpib0::9::INSTR', title='8508A')
    instruments["8508A"].config_DCV(10)
    
    
    time.sleep(300)
    
    with open('csv/'+timestr+'REPS5700A_3458A_3458B_8508A_INL.csv', mode='w') as csv_file:
        csv_file.write("# INL run")
        csv_file.write("# wait_settle = "+str(wait_settle))
        csv_file.write("# samples_per_meter_per_step = "+str(samples_per_meter_per_step))
        csv_file.write("# NPLC = "+str(NPLC))
        
        fieldnames = ['vref', '3458A_volt', '3458B_volt', 'F8508_volt']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for u in numpy.arange(umin, umax+0.01, ustep):
            instruments["F5700A"].out(str(u)+"V")
            logging.debug('main setting source to '+str(u)+'V')
            instruments["3458A"].config_NPLC(10)
            instruments["3458B"].config_NPLC(10)
            instruments["8508A"].config_DCV_fast_on()
            instruments["3458A"].config_trigger_auto()
            instruments["3458B"].config_trigger_auto()
            instruments["8508A"].config_trigger_auto()
            time.sleep(wait_settle)
            instruments["3458A"].config_NPLC(NPLC)
            instruments["3458B"].config_NPLC(NPLC)
            instruments["8508A"].config_DCV_fast_on()
            instruments["3458A"].config_trigger_hold()
            instruments["3458B"].config_trigger_hold()
            instruments["8508A"].config_trigger_hold()
            
            calibrator_out = u
            
            HP3458A_out = 0.0
            HP3458B_out = 0.0
            F8508_out = 0.0
            
            for n in range (samples_per_meter_per_step):
            
                instruments["3458A"].trigger_once()
                HP3458A_out += float(instruments["3458A"].get_read_val()) / samples_per_meter_per_step
                
                instruments["3458B"].trigger_once()
                HP3458B_out += float(instruments["3458B"].get_read_val()) / samples_per_meter_per_step
                
                instruments["8508A"].trigger_once()
                F8508_out += float(instruments["8508A"].get_read_val()) / samples_per_meter_per_step
            
            writer.writerow({'vref': calibrator_out, '3458A_volt': HP3458A_out, '3458B_volt': HP3458B_out, 'F8508_volt': F8508_out})

def temperature_sweep():

    instruments["3458A"]=HP3458A(rm, 'gpib0::22::INSTR', title='3458A')
    instruments["3458A"].config_NDIG(9)
    instruments["3458A"].config_NPLC(100)
    instruments["3458A"].config_trigger_auto()
    
    instruments["arroyo"]=Arroyo(dev='/dev/ttyUSB0', baud=38400, title='Arroyo TECSource')
    
    #instruments["3458B"]=HP3458A(rm, 'gpib0::23::INSTR', title='3458B')
    #instruments["3458B"].config_NDIG(9)
    #instruments["3458B"].config_NPLC(100)
    #instruments["3458B"].config_trigger_auto()

    #instruments["8508A"]=F8508A(rm, 'gpib0::9::INSTR', title='8508A')
    #instruments["8508A"].config_DCV(100)
    #instruments["8508A"].config_DCV_fast_off()
    #instruments["8508A"].config_trigger_auto()



    
    
    tmin = 23
    tmax = 50
    tstep = 0.3
    wait_settle = 130

    sch = sched.scheduler(time.time, time.sleep)
    sch.enter(20, 10, recursive_read_inst, argument=(sch, 20, 10, instruments["3458A"], "Vz"))
    sch.enter(10, 10, recursive_read_inst, argument=(sch, 10, 10, instruments["arroyo"], "Chamber Temp"))
    i=wait_settle*5
    for t in numpy.arange(tmin, tmax+0.01, tstep):
    #for t in numpy.flip(numpy.arange(tmin, tmax+0.01, tstep)):
        i+=wait_settle
        sch.enter(i, 9, instruments["arroyo"].out, argument=([t]))
    i+=wait_settle*12
    #for t in numpy.arange(tmin, tmax+0.01, tstep):
    for t in numpy.flip(numpy.arange(tmin, tmax+0.01, tstep)):
        i+=wait_settle
        sch.enter(i, 9, instruments["arroyo"].out, argument=([t]))
    logging.info("This temperature sweep will take "+str(datetime.timedelta(seconds=i)))
    sch.run()

def read_inst_scanner(inst, dut, bucket="PPMhub"):
    logging.debug("Reading inst with title %s after a measurement of %s" % (inst.get_title(), dut))
    #if inst.is_readable():
    writer.write(bucket, dut, inst.get_title(), inst.get_read_val())
    #    logging.debug('debug step')
    #else:
    #    logging.info(inst.get_title()+' was not readable')



def auto_ACAL_3458A():
    
    instruments["3458B"]=HP3458A(ip=vxi_ip, gpib_address=23, title="3458B")
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
        
    
def scanner_once():

# III   Br    N   channels[0] ADRmu1 +
# III   BrW   P   channels[0] ADRmu1 -
# III   Or    N   channels[1] 3458P / W4950 +
# III   OrW   P   channels[1] 3458P / W4950 -
# III   Bl    N   channels[2] ADRmu3 +
# III   BlW   P   channels[2] ADRmu3 -
# III   Gr    N   channels[3] ADRmu15 +
# III   GrW   P   channels[3] ADRmu15 -

# IV    Br    N   channels[4] ADRmu9 +
# IV    BrW   P   channels[4] ADRmu9 -
# IV    Or    N   channels[5] ADRmu6 +
# IV    OrW   P   channels[5] ADRmu6 -
# IV    Bl    N   channels[6] ADRmu11 +
# IV    BlW   P   channels[6] ADRmu11 -
# IV    Gr    N   channels[7] ADRmu12 +
# IV    GrW   P   channels[7] ADRmu12 -

# II    Br    N   channels[8]   3458B +
# II    BrW   P   channels[8]   3458B -
# II    Or    N   channels[9]   
# II    OrW   P   channels[9]   
# II    Bl    N   channels[10]  ADRmu4 +
# II    BlW   P   channels[10]  ADRmu4 +
# II    Gr    N   channels[11]  ADRmu20 +
# II    GrW   P   channels[11]  ADRmu20 -

# I     Br    N   channels[12]  
# I     BrW   P   channels[12]  
# I     Or    N   channels[13]  
# I     OrW   P   channels[13]  
# I     Bl    N   channels[14]  
# I     BlW   P   channels[14]  
# I     Gr    N   channels[15]  
# I     GrW   P   channels[15]  

    switch_delay = 120
    NPLC = 100
    nmeasurements = 20
    
    
    instruments["3458B"]=HP3458A(rm, 'TCPIP::192.168.178.65::gpib0,23', title='3458B')
    instruments["3458B"].config_DCV(10)
    instruments["3458B"].config_NDIG(9)
    instruments["3458B"].config_NPLC(NPLC)
    instruments["3458B"].config_trigger_hold()
    
    instruments["3458P"]=HP3458A(rm, 'TCPIP::192.168.178.65::gpib0,22', title='3458P')
    instruments["3458P"].config_DCV(10)
    instruments["3458P"].config_NDIG(9)
    instruments["3458P"].config_NPLC(NPLC)
    instruments["3458P"].config_trigger_hold()
    
    #instruments["W4950"]=W4950(rm, 'gpib0::9::INSTR')
    #instruments["W4950"].config_accuracy("HIGH")
    #instruments["W4950"].config_DCV(10)
    #instruments["W4950"].config_trigger_hold()
    
    instruments["3458B"].acal_ALL()
    instruments["3458P"].acal_ALL()
    
    while not (instruments["3458B"].is_ready() and instruments["3458P"].is_ready()):
        time.sleep(5)


    read_cal_params(instruments["3458B"])
    read_cal_params(instruments["3458P"])

    
    scanner_sources = [(channels[0], "ADRmu1"), (channels[2], "ADRmu3"), (channels[3], "ADRmu15"), (channels[12], "ADRmu9"), (channels[14], "ADRmu11"), (channels[15], "ADRmu12"), (channels[13], "ADRmu6"), (channels[10], "ADRmu4"), (channels[11], "ADRmu20"), ]
    scanner_meters = [(channels[8], instruments["3458B"]), (channels[1], instruments["3458P"]), ]

    switch=takovsky_scanner()
    
    sch = sched.scheduler(time.time, time.sleep)
    
    seconds = 1
    
    scanner_permutations = list(itertools.product(scanner_sources, scanner_meters))
    
    t=[["wiring", "takovsky_scanner"],["guard","to_lo"], ]
        
    for perm in scanner_permutations:
        sch.enter(seconds, 10, switch.switchingCloseRelay, argument=(perm[0][0],)) # Close source
        sch.enter(seconds, 10, switch.switchingCloseRelay, argument=(perm[1][0],)) # Close meter
        seconds = seconds + switch_delay
        for measurement in range(nmeasurements):
            sch.enter(seconds, 10, perm[1][1].trigger_once)
            seconds = seconds + NPLC * 0.04 + 0.2
            sch.enter(seconds, 10, read_inst_scanner, argument=(perm[1][1], perm[0][1]))
            seconds = seconds + 1
        sch.enter(seconds, 10, switch.switchingOpenRelay, argument=(perm[0][0],)) # Open source
        sch.enter(seconds, 10, switch.switchingOpenRelay, argument=(perm[1][0],)) # Open meter
        
    logging.info("This round will take "+str(datetime.timedelta(seconds=seconds)))
    sch.run()
    instruments["3458P"].blank_display()
    instruments["3458B"].blank_display()
        
        
def read_cal_params(inst):
    while not inst.is_ready():
        logging.info("%s was not ready for read_cal_params." % (inst.get_title()))
        time.sleep(1)
    for n in range(1,254):
        writer.write("PPMhub", inst.get_title(), "CAL? "+str(n), inst.get_cal_param(n), tags=[["group","cal_params"], ])
        
 
def recursive_read_inst(sch, interval, priority, inst, name, bucket="Temperature sweep"):
    sch.enter(interval, priority, recursive_read_inst, argument=(sch, interval, priority, inst, name, bucket))
    writer.write(bucket, name, inst.get_title(), inst.get_read_val())
    
def noise_3458A():

    seconds_per_step=60*20

    instruments["3458A"]=HP3458A(ip=vxi_ip, gpib_address=22, title="3458A")
    instruments["3458A"].config_10DCV_9digit()
    #instruments["3458A"].config_10OHMF_9digit()
    #instruments["3458A"].config_10kOHMF_9digit()
    #instruments["3458A"].config_1mA_9digit()
    instruments["3458A"].blank_display()
    instruments["3458A"].config_trigger_auto()
    HP3458A_temperature=HP3458A_temp(HP3458A=instruments["3458A"], title="HP3458A Int Temp Sensor")
    
    instruments["3458B"]=HP3458A(ip=vxi_ip, gpib_address=23, title="3458B")
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
                


def rms_34420A():
    clock=datetime.datetime.now()
    print("Start time: " + str(clock))
    
    instruments["K34420A"]=HP34420A(rm, 'gpib0::8::INSTR', title='Keysight 34420A')
    instruments["K34420A"].config_DCV(0.001)
    #instruments["K34420A"].rel()
    #instruments["K34420A"].set_filter()
    #instruments["K34420A"].blank_display()
    instruments["K34420A"].config_trigger_auto()
    
    readings = [0]*500
    rel = [0]*100

    while True:
        for i in range(100):
            rel[i] = float(instruments["K34420A"].get_read_val())
        for i in range(500):
            readings[i] = float(instruments["K34420A"].get_read_val()) - numpy.mean(rel)
        
        clock=datetime.datetime.now()
        print(str(clock))
        print(numpy.mean(readings))
        #print(numpy.sqrt(numpy.mean(numpy.square(readings))))
        



def scanner_34420A():
    switch_delay = 120
    NPLC = 100
    nmeasurements = 100
    
    instruments["K34420A"]=HP34420A(rm, 'gpib0::8::INSTR', title='Keysight 34420A')
    instruments["K34420A"].config_DCV(0.001)
    
    scanner_sources = [(channels[0], "Ch0"), (channels[2], "Ch2"), (channels[3], "Ch3"), (channels[4], "Ch4"), (channels[6], "Ch6"), (channels[7], "Ch7"), (channels[5], "Ch5"), (channels[10], "Ch10"), (channels[11], "Ch11"), ]
    scanner_meters = [(channels[9], instruments["K34420A"]),   ]
    switch=takovsky_scanner()
    scanner_permutations = list(itertools.product(scanner_sources, scanner_meters))
    
    for perm in scanner_permutations:
        switch.switchingCloseRelay(perm[0][0])
        switch.switchingCloseRelay(perm[1][0],) # Close meter
        for measurement in range(nmeasurements):
            read_inst_scanner(perm[1][1], perm[0][1])
        switch.switchingOpenRelay(perm[0][0],) # Open source
        switch.switchingOpenRelay(perm[1][0],) # Open meter
        
        
def resistance_bridge_temperature_sweep():
    logging.info("resistance_bridge_temperature_sweep()")
    instruments["2182a"]=K2182A(rm, 'TCPIP::192.168.0.88::gpib0,4', title='Keithley 2182a')
    instruments["2182a"].config_DCV()

    instruments["arroyo"]=Arroyo(dev='/dev/ttyUSB0', baud=38400, title='Arroyo TECSource')
    
    instruments["8508a"]=F8508A(rm, 'TCPIP::192.168.0.88::gpib0,9', title='Fluke 8508A')
    #instruments["8508a"].config_pt100()

    
    tmin = 18
    tmax = 28
    tstep = 0.1
    wait_settle = 60*30

    sch = sched.scheduler(time.time, time.sleep)
    sch.enter(20, 10, recursive_read_inst, argument=(sch, 20, 10, instruments["2182a"], "VBridge"))
    sch.enter(10, 10, recursive_read_inst, argument=(sch, 10, 10, instruments["arroyo"], "Chamber Temp"))
    sch.enter(10, 10, recursive_read_inst, argument=(sch, 60*10, 10, instruments["8508a"], "DUT Temp"))

    i=wait_settle
    for t in numpy.arange(23, tmax+0.01, tstep):
        i+=wait_settle
        sch.enter(i, 9, instruments["arroyo"].out, argument=([t]))
    i+=wait_settle*4
    for t in numpy.flip(numpy.arange(23, tmax+0.01, tstep)):
        i+=wait_settle
        sch.enter(i, 9, instruments["arroyo"].out, argument=([t]))
    i+=wait_settle*4
    for t in numpy.flip(numpy.arange(tmin-0.01, 23, tstep)):
        i+=wait_settle
        sch.enter(i, 9, instruments["arroyo"].out, argument=([t]))
    i+=wait_settle*4
    for t in numpy.arange(tmin-0.01, 23, tstep):
        i+=wait_settle
        sch.enter(i, 9, instruments["arroyo"].out, argument=([t]))
    i+=wait_settle*4
    sch.enter(i, 9, logging.info, argument=("All done, but still recording until shutdown"))
        
    logging.info("This temperature sweep will take "+str(datetime.timedelta(seconds=i)))
    sch.run()
    
    
def voltage_temperature_sweep():
    logging.info("resistance_bridge_temperature_sweep()")

    instruments["arroyo"]=Arroyo(dev='/dev/ttyUSB0', baud=38400, title='Arroyo TECSource')
    
    #instruments["8508A"]=F8508A(rm, 'TCPIP::192.168.0.88::gpib0,9', title='Fluke 8508A')
    #instruments["8508A"].config_DCV(10)
    #instruments["8508A"].config_trigger_hold()
    
    instruments["2182a"]=K2182A(rm, 'TCPIP::192.168.0.88::gpib0,4', title='Keithley 2182a')
    instruments["2182a"].config_DCV()
    

    
    tmin = 18
    tmax = 28
    tstep = 0.5
    wait_settle = 60*10

    sch = sched.scheduler(time.time, time.sleep)
    sch.enter(20, 10, recursive_read_inst, argument=(sch, 20, 10, instruments["2182a"], "VBridge"))
    sch.enter(10, 10, recursive_read_inst, argument=(sch, 10, 10, instruments["arroyo"], "Chamber Temp"))
    #sch.enter(10, 10, recursive_read_inst, argument=(sch, 30, 10, instruments["8508A"], "hamon divider output"))

    i=0
    for t in numpy.arange(23, tmax+0.01, tstep):
        i+=wait_settle
        sch.enter(i, 9, instruments["arroyo"].out, argument=([t]))
    i+=wait_settle*4
    for t in numpy.flip(numpy.arange(23, tmax+0.01, tstep)):
        i+=wait_settle
        sch.enter(i, 9, instruments["arroyo"].out, argument=([t]))
    i+=wait_settle*4
    for t in numpy.flip(numpy.arange(tmin-0.01, 23, tstep)):
        i+=wait_settle
        sch.enter(i, 9, instruments["arroyo"].out, argument=([t]))
    i+=wait_settle*4
    for t in numpy.arange(tmin-0.01, 23, tstep):
        i+=wait_settle
        sch.enter(i, 9, instruments["arroyo"].out, argument=([t]))
    i+=wait_settle*4
    sch.enter(i, 9, logging.info, argument=("All done, but still recording until shutdown"))
        
    logging.info("This temperature sweep will take "+str(datetime.timedelta(seconds=i)))
    sch.run()
    
    
   
        
            
            
def nbs430():

    nsamples = 10
    switch_delay = 60
    
    
    error_counter = 0
    instruments["K34420A"]=HP34420A(rm, 'TCPIP::192.168.178.65::gpib0,8', title='Keysight 34420A')
    instruments["K34420A"].config_DCV("AUTO")
    instruments["K34420A"].config_trigger_hold()
    
    switch=rotary_scanner()
    
    while True:
        
        switch.switchingCloseRelay("k0") # Home switch
        switch.switchingCloseRelay("a0") # Home switch
        switch.switchingCloseRelay("e0") # Home switch
        switch.switchingCloseRelay("g0") # Home switch
        switch.switchingCloseRelay("i0") # Home switch
        switch.switchingCloseRelay("c0") # Home switch

        scanner_sources = [(1, "ADRmu6"), (2, "ADRmu4"), (3, "ADRmu1"), (4, "ADRmu9"),  (5, "ADRmu12"),]
        #scanner_sources = [(1, "ADRmu3"), (2, "ADRmu20"), (3, "ADRmu1"), (4, "ADRmu11"),  (5, "ADRmu12"),]
        scanner_permutations = set(itertools.combinations(scanner_sources, 2))
        
        polarity_1_samples = numpy.tile(0.0,nsamples)
        polarity_2_samples = numpy.tile(0.0,nsamples)
        
        while True:
        
            switch.switchingCloseRelay("k"+chr(59)) # Park source switches
            #switch.switchingCloseRelay("a"+chr(59)) # Park source switches
            switch.switchingCloseRelay("e"+chr(59)) # Park source switches
            switch.switchingCloseRelay("g"+chr(59)) # Park source switches
            #switch.switchingCloseRelay("i"+chr(59))
            switch.switchingCloseRelay("c"+chr(59))
            
            switch.switchingCloseRelay("a5") # Short VM
            switch.switchingCloseRelay("i"+chr(58)) # Short VM
            
            time.sleep(switch_delay)
            instruments["K34420A"].rel_off()
            
            for sample in range(nsamples):
                instruments["K34420A"].trigger_once()
                reading = instruments["K34420A"].get_read_val()
                polarity_2_samples[sample]=reading
                logging.debug("Shorted read "+str(reading))
                
            logging.debug("stdev "+str(statistics.stdev(polarity_2_samples)))
            if (statistics.stdev(polarity_2_samples)>3e-7):
                logging.error("stdev looks too high, switches a5 i"+chr(58))
                error_counter += 1
                logging.error("error_counter: "+str(error_counter))
                break
            
            writer.write("PPMhub", "Scanner short circuit", instruments["K34420A"].get_title(), statistics.mean(polarity_2_samples))
            instruments["K34420A"].rel()
            instruments["K34420A"].trigger_once()
            instruments["K34420A"].get_read_val()
        
        
            
            for perm in scanner_permutations:
            
                if(perm[0][1]>perm[1][1]): # We don't need both V1-V2 and V2-V1
                    perm=[perm[1],perm[0]] # so we use alphabetically sorted pairs
            
                logging.debug("error_counter "+str(error_counter))
            
                logging.debug("Looking at "+perm[0][1]+" and "+perm[1][1])
                
                switch.switchingCloseRelay("k"+chr(59)) # Park + side switches
                switch.switchingCloseRelay("e"+chr(59)) # Park + side switches
                
                switch.switchingCloseRelay("g"+chr(perm[0][0]+48)) # Connect Source 1 -
                switch.switchingCloseRelay("c"+chr(perm[1][0]+48)) # to Source 2 -
                
                switch.switchingCloseRelay("a"+chr(perm[0][0]+48)) # Connect VM + to Source 1 +
                switch.switchingCloseRelay("i"+chr(perm[1][0]+5+48)) # Connect VM - to Source 2 +
                
                time.sleep(switch_delay)
                
                #instruments["K34420A"].trigger_once() # First reading sometimes unreliable? Bc autorange perhaps?
                #instruments["K34420A"].get_read_val()
                
                for sample in range(nsamples):
                    instruments["K34420A"].trigger_once()
                    reading = instruments["K34420A"].get_read_val()
                    polarity_1_samples[sample]=reading
                    logging.debug("In 1 polarity read "+str(reading))
                    
                logging.debug("stdev "+str(statistics.stdev(polarity_1_samples)))
                if (statistics.stdev(polarity_1_samples)>3e-7):
                    logging.error("stdev looks too high, switches"+" g"+chr(perm[0][0]+48)+" c"+chr(perm[1][0]+48)+" a"+chr(perm[0][0]+48)+" i"+chr(perm[1][0]+5+48))
                    error_counter += 1
                    logging.error("error_counter: "+str(error_counter))
                    break
                    
                switch.switchingCloseRelay("g"+chr(59)) # Park - side switches
                switch.switchingCloseRelay("c"+chr(59)) # Park - side switches
                
                switch.switchingCloseRelay("k"+chr(perm[0][0]+48)) # Connect Source 1 +
                switch.switchingCloseRelay("e"+chr(perm[1][0]+48)) # to Source 2 +
                
                switch.switchingCloseRelay("a"+chr(perm[0][0]+5+48)) # Connect VM + to Source 1 -
                switch.switchingCloseRelay("i"+chr(perm[1][0]+48)) # Connect VM - to Source 2 -
                
                time.sleep(switch_delay)
                
                
                for sample in range(nsamples):
                    instruments["K34420A"].trigger_once()
                    reading = instruments["K34420A"].get_read_val()
                    polarity_2_samples[sample]=reading
                    logging.debug("In 2 polarity read "+str(reading))
                    
                logging.debug("stdev "+str(statistics.stdev(polarity_2_samples)))
                if (statistics.stdev(polarity_2_samples)>3e-7):
                    logging.error("stdev looks too high, switches"+" k"+chr(perm[0][0]+48)+" e"+chr(perm[1][0]+48)+" a"+chr(perm[0][0]+5+48)+" i"+chr(perm[1][0]+48))
                    error_counter += 1
                    logging.error("error_counter: "+str(error_counter))
                    break
                    
                difference = (statistics.mean(polarity_1_samples)-statistics.mean(polarity_2_samples))/2
                logging.debug("Difference looks like %.*f", 8, difference)
                writer.write("PPMhub", (perm[0][1]+" - "+perm[1][1]), instruments["K34420A"].get_title(), difference)


def resistance_bridge():
    logging.info("resistance_bridge_temperature_sweep()")
    instruments["K34420A"]=HP34420A(rm, 'gpib0::8::INSTR', title='Keysight 34420A')
    instruments["K34420A"].config_DCV("0")
    instruments["K34420A"].config_trigger_hold()
    instruments["K34420A"].trigger_once()
    instruments["K34420A"].rel()

    
    instruments["3458P"]=HP3458A(rm, 'gpib0::22::INSTR', title='3458P')
    instruments["3458P"].config_pt100()
    instruments["3458P"].config_NDIG(9)
    instruments["3458P"].config_NPLC(100)
    instruments["3458P"].config_trigger_hold()
    
    timestr = time.strftime("%Y%m%d-%H%M%S_")
    with open('csv/'+timestr+'_resistance_bridge.csv', mode='w') as csv_file:
        fieldnames = ['time', 'pt100', 'r_deviation']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        while True:
                instruments["K34420A"].trigger_once()
                instruments["3458P"].trigger_once()
                
                pt100 = float(instruments["3458P"].get_read_val())
                r_deviation = float(instruments["K34420A"].get_read_val())
                r_deviation = (r_deviation / 10E-9)*4E-6
                writer.writerow({'time':time.time(), 'pt100': pt100, 'r_deviation': r_deviation})
                logging.info("At "+str(pt100)+" °C resistance deviates %.*f Ohm", 8, r_deviation)
    
    
def f8508a_logger():

    instruments["8508A"]=F8508A(rm, 'TCPIP::192.168.0.88::gpib0,9', title='8508A')
    instruments["8508A"].config_DCV(100)
    instruments["8508A"].config_trigger_hold()
    
    while True:
        #instruments["8508A"].trigger_once()
        val = float(instruments["8508A"].get_read_val())
        writer.write("PPMhub", sys.argv[1], instruments["8508A"].get_title(), val)
        print(val)



def resistance_bridge_reversal():

    nsamples = 100
    switch_delay = 60
    error_counter = 0
    
    tmin = 18
    tmax = 28
    tstep = 0.1
    measurements_per_tstep = 20
    
    instruments["2182a"]=K2182A(rm, 'TCPIP::192.168.0.88::GPIB0,4', title='Keithley 2182a')
    instruments["2182a"].config_DCV()
    
    instruments["arroyo"]=Arroyo(dev='/dev/ttyUSB0', baud=38400, title='Arroyo TECSource')
    
    instruments["8508a"]=F8508A(rm, 'TCPIP::192.168.0.88::GPIB0,9', title='Fluke 8508A')
    
    switch=rotary_scanner()
    
    #switch.switchingCloseRelay("k0") # Home switch
    #switch.switchingCloseRelay("a0") # Home switch
    #switch.switchingCloseRelay("e0") # Home switch
    #switch.switchingCloseRelay("g0") # Home switch
    #switch.switchingCloseRelay("i0") # Home switch
    #switch.switchingCloseRelay("c0") # Home switch
    
    #switch.switchingCloseRelay("k"+chr(59)) # Park source switches
    #switch.switchingCloseRelay("e"+chr(59)) # Park source switches
    #switch.switchingCloseRelay("g"+chr(59)) # Park source switches
    #switch.switchingCloseRelay("c"+chr(59))
    #switch.switchingCloseRelay("a"+chr(59))
    #switch.switchingCloseRelay("i"+chr(59))
    
    polarity_1_samples = numpy.tile(0.0,nsamples)
    polarity_2_samples = numpy.tile(0.0,nsamples)
    
    from itertools import chain
    #temperatures = chain(numpy.arange(23, tmax+0.01, tstep), numpy.flip(numpy.arange(23, tmax+0.01, tstep)), numpy.flip(numpy.arange(tmin-0.01, 23, tstep)), numpy.arange(tmin-0.01, 23, tstep))
    temperatures = chain([28.0,28.0], numpy.flip(numpy.arange(23.0, 28.00001, tstep)), [23.0,23.0,23.0])
    #temperatures = [23.0, 28.0, 23.0, 18.0]
    

    
    while True:
        for t in temperatures:
            logging.info("Setting new chamber temperature: "+str(t)+" °C")
            instruments["arroyo"].out(t)
            time.sleep(switch_delay)
            
            for measurement in range(measurements_per_tstep):
            
                switch.switchingCloseRelay("a1") # Bridge+ to Source+
                switch.switchingCloseRelay("i1") # Bridge- to Source-
                
                time.sleep(switch_delay)
                
                for sample in range(nsamples):
                    writer.write("Temperature sweep", "Chamber Temp", instruments["arroyo"].get_title(), instruments["arroyo"].get_read_val())
                    reading = instruments["2182a"].get_read_val()
                    polarity_1_samples[sample]=reading
                    logging.debug("polarity 2 read "+str(reading))
                    
                logging.debug("stdev "+str(statistics.stdev(polarity_1_samples)))
                if (statistics.stdev(polarity_1_samples)>3e-7):
                    logging.error("stdev looks too high")
                    error_counter += 1
                    logging.error("error_counter: "+str(error_counter))
                    #break
                    
                switch.switchingCloseRelay("a6") # Bridge+ to Source-
                switch.switchingCloseRelay("i6") # Bridge- to Source+
                
                time.sleep(switch_delay)
                
                for sample in range(nsamples):
                    writer.write("Temperature sweep", "Chamber Temp", instruments["arroyo"].get_title(), instruments["arroyo"].get_read_val())
                    reading = instruments["2182a"].get_read_val()
                    polarity_2_samples[sample]=reading
                    logging.debug("polarity 2 read "+str(reading))
                    
                logging.debug("stdev "+str(statistics.stdev(polarity_2_samples)))
                if (statistics.stdev(polarity_2_samples)>3e-7):
                    logging.error("stdev looks too high")
                    error_counter += 1
                    logging.error("error_counter: "+str(error_counter))
                    #break
                    
                if (measurement == measurements_per_tstep-1):
                    logging.info("Asking 8508A for DUT temperature")
                    writer.write("Temperature sweep", "DUT Temperature", instruments["8508a"].get_title(), instruments["8508a"].get_read_val())

                        
                difference = (statistics.mean(polarity_1_samples)-statistics.mean(polarity_2_samples))/2
                logging.debug("Difference looks like %.*f", 8, difference)
                writer.write("Temperature sweep", "Reversible Resistance Bridge", instruments["2182a"].get_title(), difference)
                
                
def ratio_1281():

    delay = 600
    nsamples = 10

    instruments["arroyo"]=Arroyo(dev='/dev/ttyUSB0', baud=38400, title='Arroyo TECSource')

    instruments["1281"]=D1281(rm, 'TCPIP::192.168.178.65::gpib0,16', title='1281')
    instruments["1281"].config_DCV(0.1)
    instruments["1281"].config_ratio()
    instruments["1281"].config_trigger_hold()
    
    #temperatures = [23.0,28.0,23.0,18.0]
    temperatures = [18.0,23.0]
    
    while True:
        for t in temperatures:
            instruments["arroyo"].out(t)
            for sample in range(nsamples):
                time.sleep(delay)
                ratio=instruments["1281"].get_read_val()
                writer.write("Temperature sweep", "Divider Ratio", instruments["1281"].get_title(), ratio)
                writer.write("Temperature sweep", "Chamber Temp", instruments["arroyo"].get_title(), instruments["arroyo"].get_read_val())
                

    
try:
    #test_3458A()
    #test_W4950()
    #INL_3458A()
    #temperature_sweep()
    #scanner_once()
    #auto_ACAL_3458A()
    #noise_3458A()
    #pt100_scanner()
    #rms_34420A()
    #scanner_34420A()
    #resistance_bridge_temperature_sweep()
    #test_rotary_scanner_episode_2()
    nbs430()
    #resistance_bridge()
    #f8508a_logger()
    #voltage_temperature_sweep()
    #resistance_bridge_reversal()
    #ratio_1281()


except (KeyboardInterrupt, SystemExit) as exErr:

    #for instrument in instruments:
    #    instruments[instrument].blank_display()
        
    logging.info("kthxbye")
    sys.exit(0)
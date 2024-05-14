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
from statistics import mean 
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

    #switch=takovsky_scanner()
    #switch.switchingCloseRelay(channels[5])
    #switch.switchingCloseRelay(channels[6])

    NPLC = 200
    instruments["3458A"]=HP3458A(ip=vxi_ip, gpib_address=22, title="3458A")
    instruments["3458A"].config_DCV(10)
    instruments["3458A"].config_NDIG(9)
    instruments["3458A"].config_NPLC(NPLC)
    instruments["3458A"].config_trigger_auto()
    instruments["3458A"].blank_display()
    
    while True:
        if instruments["3458A"].is_readable():
            writer.write("PPMhub",str(sys.argv[1]), instruments["3458A"].get_title(), instruments["3458A"].get_read_val())
        #writer.write("lab_sensors", "Ambient Temp", instruments["long_tmp117"].get_title(), instruments["long_tmp117"].get_read_val())
        time.sleep(1)
        
        
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
    instruments["F5700A"]=F5700A(ip=vxi_ip, gpib_address=1, title="Reps 5700A")
    instruments["3458A"]=HP3458A(ip=vxi_ip, gpib_address=22, title="Reps 3458A")
    instruments["3458B"]=HP3458A(ip=vxi_ip, gpib_address=23, title="Reps 3458B")
    instruments["W4950"]=W4950(ip=vxi_ip, gpib_address=9)
    
    instruments["3458A"].config_DCV(10)
    instruments["3458A"].config_NDIG(9)
    instruments["3458A"].config_trigger_auto()
    
    instruments["3458B"].config_DCV(10)
    instruments["3458B"].config_NDIG(9)
    instruments["3458B"].config_trigger_auto()
    
    umin = -11
    umax = 11
    ustep = 0.25
    wait_settle = 20
    samples_per_meter_per_step = 1
    NPLC = 100
    
    instruments["F5700A"].out(str(umin)+"V")
    instruments["F5700A"].oper()
    instruments["F5700A"].rangelck()
    time.sleep(300)
    
    with open('csv/'+timestr+'REPS5700A_3458A_3458B_4950_INL.csv', mode='w') as csv_file:
        csv_file.write("# INL run")
        csv_file.write("# wait_settle = "+str(wait_settle))
        csv_file.write("# samples_per_meter_per_step = "+str(samples_per_meter_per_step))
        csv_file.write("# NPLC = "+str(NPLC))
        
        fieldnames = ['vref', '3458A_volt', '3458B_volt', 'W4950_volt']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for u in numpy.arange(umin, umax+0.01, ustep):
            instruments["F5700A"].out(str(u)+"V")
            logging.debug('main setting source to '+str(u)+'V')
            instruments["3458A"].config_NPLC(10)
            instruments["3458B"].config_NPLC(10)
            instruments["W4950"].config_accuracy("LOW")
            instruments["3458A"].config_trigger_auto()
            instruments["3458B"].config_trigger_auto()
            instruments["W4950"].config_trigger_auto()
            time.sleep(wait_settle)
            instruments["3458A"].config_NPLC(NPLC)
            instruments["3458B"].config_NPLC(NPLC)
            instruments["W4950"].config_accuracy("HIGH")
            instruments["3458A"].config_trigger_hold()
            instruments["3458B"].config_trigger_hold()
            instruments["W4950"].config_trigger_hold()
            
            calibrator_out = u
            
            HP3458A_out = 0.0
            HP3458B_out = 0.0
            W4950_out = 0.0
            
            for n in range (samples_per_meter_per_step):
            
                instruments["3458A"].trigger_once()
                HP3458A_out += float(instruments["3458A"].get_read_val()) / samples_per_meter_per_step
                
                instruments["3458B"].trigger_once()
                HP3458B_out += float(instruments["3458B"].get_read_val()) / samples_per_meter_per_step
                
                instruments["W4950"].trigger_once()
                W4950_out += float(instruments["W4950"].get_read_val()) / samples_per_meter_per_step
            
            writer.writerow({'vref': calibrator_out, '3458A_volt': HP3458A_out, '3458B_volt': HP3458B_out, 'W4950_volt': W4950_out})

def temperature_sweep():

    instruments["3458A"]=HP3458A(ip=vxi_ip, gpib_address=22, title="3458A")
    instruments["3458A"].config_NDIG(9)
    instruments["3458A"].config_NPLC(50)
    instruments["3458A"].config_trigger_auto()
    
    instruments["arroyo"]=Arroyo(dev='/dev/ttyUSB0', baud=38400, title='Arroyo TECSource')
    
    #instruments["3458B"]=HP3458A(ip=vxi_ip, gpib_address=23, title="3458B")
    #instruments["3458B"].config_NDIG(9)
    #instruments["3458B"].config_NPLC(50)
    #instruments["3458B"].config_trigger_auto()
    
    
    tmin = 16
    tmax = 24
    tstep = 0.1
    wait_settle = 180

    sch = sched.scheduler(time.time, time.sleep)
    sch.enter(20, 10, recursive_read_inst, argument=(sch, 20, 10, instruments["3458A"], "Vz"))
    sch.enter(10, 10, recursive_read_inst, argument=(sch, 10, 10, instruments["arroyo"], "Chamber Temp"))
    i=wait_settle*5
    for t in numpy.arange(tmin, tmax+0.01, tstep):
    #for t in numpy.flip(numpy.arange(tmin, tmax+0.01, tstep)):
        i+=wait_settle
        sch.enter(i, 9, instruments["arroyo"].out, argument=([t]))
    i+=wait_settle*10
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
# III   Or    N   channels[1] W4950 +
# III   OrW   P   channels[1] W4950 -
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
# II    Or    N   channels[9]   3458A +
# II    OrW   P   channels[9]   3458A -
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
    
    instruments["3458A"]=HP3458A(rm, 'GPIB0::22::INSTR', title='3458A')
    instruments["3458A"].config_DCV(10)
    instruments["3458A"].config_NDIG(9)
    instruments["3458A"].config_NPLC(NPLC)
    instruments["3458A"].config_trigger_hold()

    
    instruments["3458B"]=HP3458A(rm, 'GPIB0::23::INSTR', title='3458B')
    instruments["3458B"].config_DCV(10)
    instruments["3458B"].config_NDIG(9)
    instruments["3458B"].config_NPLC(NPLC)
    instruments["3458B"].config_trigger_hold()
    
    instruments["W4950"]=W4950(rm, 'GPIB0::9::INSTR')
    instruments["W4950"].config_accuracy("HIGH")
    instruments["W4950"].config_DCV(10)
    instruments["W4950"].config_trigger_hold()

    scanner_sources = [(channels[0], "ADRmu1"), (channels[2], "ADRmu3"), (channels[3], "ADRmu15"), (channels[4], "ADRmu9"), (channels[6], "ADRmu11"), (channels[7], "ADRmu12"), (channels[5], "ADRmu6"), (channels[10], "ADRmu4"), (channels[11], "ADRmu20"), ]
    scanner_meters = [(channels[9], instruments["3458A"]),  (channels[8], instruments["3458B"]), (channels[1], instruments["W4950"]), ]

    switch=takovsky_scanner()
    
    sch = sched.scheduler(time.time, time.sleep)
    
    scanner_permutations = list(itertools.product(scanner_sources, scanner_meters))
        
    seconds = 10
    sch.enter(seconds, 9, acal_inst, argument=(sch, 60*60, 9, instruments["3458A"]))
    sch.enter(seconds, 9, acal_inst, argument=(sch, 60*60, 9, instruments["3458B"]))
    seconds = seconds + 200
    sch.enter(seconds, 9, read_cal_params, argument=(instruments["3458A"],))
    sch.enter(seconds, 9, read_cal_params, argument=(instruments["3458B"],))
    seconds = seconds + 60
    
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
    instruments["3458A"].blank_display()
    instruments["3458B"].blank_display()
        
        
def read_cal_params(inst):
    while not inst.is_ready():
        logging.info("%s was not ready for read_cal_params." % (inst.get_title()))
        time.sleep(1)
    writer.write("PPMhub", inst.get_title(), "CAL? 72", inst.get_cal_72())
    writer.write("PPMhub", inst.get_title(), "CAL? 175", inst.get_cal_175())
        
def acal_inst(sch, interval, priority, inst):
    while not inst.is_ready():
        logging.info("%s was not ready for acal_inst." % (inst.get_title()))
        time.sleep(1)
    inst.acal_DCV()
    read_cal_params
 
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
    
    instruments["3458B"]=HP3458A(ip=vxi_ip, gpib_address=23, title="3458B")
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

def test_34420A():
    #instruments["HP34420A"]=HP34420A(rm, 'GPIB0::7::INSTR', title='HP 34420A')
    #instruments["HP34420A"].config_DCV(0.001)
    #instruments["HP34420A"].rel()
    #instruments["HP34420A"].blank_display()
    #instruments["HP34420A"].config_trigger_auto()
    clock=datetime.datetime.now()
    print("Reference time: " + str(clock))
    
    
    instruments["K34420A"]=HP34420A(rm, 'GPIB0::8::INSTR', title='Keysight 34420A')
    instruments["K34420A"].config_DCV(0.001)
    instruments["K34420A"].rel()
    #instruments["K34420A"].blank_display()
    instruments["K34420A"].config_trigger_auto()
    
    #while True:
        #writer.write(bucket, dut, inst.get_title(), inst.get_read_val())
        #writer.write("PPMhub", "ADRmu4 - ADRmu1", instruments["HP34420A"].get_title(), instruments["HP34420A"].get_read_val())
        #writer.write("PPMhub", "KS Shorting Plug", instruments["K34420A"].get_title(), instruments["K34420A"].get_read_val())
        
    timestr = time.strftime("%Y%m%d-%H%M%S_")
    with open('csv/'+timestr+'HP_34420A_short_NPLC100.csv', mode='w') as csv_file:
        fieldnames = ['time', '34420a_volt']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        while True:
                val = float(instruments["K34420A"].get_read_val())
                writer.writerow({'time':time.time(), '34420a_volt': val})


def scanner_34420A():
    switch_delay = 120
    NPLC = 100
    nmeasurements = 100
    
    instruments["K34420A"]=HP34420A(rm, 'GPIB0::8::INSTR', title='Keysight 34420A')
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
    instruments["K34420A"]=HP34420A(rm, 'GPIB0::8::INSTR', title='Keysight 34420A')
    instruments["K34420A"].config_DCV(0.001)
    
    instruments["arroyo"]=Arroyo(dev='/dev/ttyUSB0', baud=38400, title='Arroyo TECSource')
    
    tmin = 20
    tmax = 60
    tstep = 1
    wait_settle = 1000

    sch = sched.scheduler(time.time, time.sleep)
    sch.enter(20, 10, recursive_read_inst, argument=(sch, 20, 10, instruments["K34420A"], "VBridge"))
    sch.enter(10, 10, recursive_read_inst, argument=(sch, 10, 10, instruments["arroyo"], "Chamber Temp"))
    i=wait_settle*2
    for t in numpy.arange(tmin, tmax+0.01, tstep):
    #for t in numpy.flip(numpy.arange(tmin, tmax+0.01, tstep)):
        i+=wait_settle
        sch.enter(i, 9, instruments["arroyo"].out, argument=([t]))
    i+=wait_settle*10
    #for t in numpy.arange(tmin, tmax+0.01, tstep):
    for t in numpy.flip(numpy.arange(tmin, tmax+0.01, tstep)):
        i+=wait_settle
        sch.enter(i, 9, instruments["arroyo"].out, argument=([t]))
    logging.info("This temperature sweep will take "+str(datetime.timedelta(seconds=i)))
    sch.run()
    
    
    
def test_rotary_scanner():

    instruments["K34420A"]=HP34420A(rm, 'GPIB0::8::INSTR', title='Keysight 34420A')
    instruments["K34420A"].config_DCV(0.001)
    instruments["K34420A"].config_trigger_auto()
    
    switch=rotary_scanner()
    
    time.sleep(5)
    
    i=0
    nreadings=30
    
    while True:
        for k in range(100):
            i+=1
            pos=random.randint(1,11)
            logging.info("Going to switch position "+str(pos))
            switch.switchingCloseRelay(pos)
            while (switch.distanceToGo()):
                pass
        
        
        switch.home()
        time.sleep(5)
        
        switch.switchingCloseRelay(6)
        logging.info("Going to switch position 8")
        while (switch.distanceToGo()):
            pass
            
        time.sleep(60)
                
        for j in range(nreadings):
            writer.write("PPMhub", "EMF", instruments["K34420A"].get_title(), instruments["K34420A"].get_read_val())
            writer.write("PPMhub", "Actuations", "Rotary Scanner", i)
        
    
    
def test_rotary_scanner_episode_2():
        
    switch_delay = 10
    NPLC = 100
    nmeasurements = 10
    
    instruments["3458A"]=HP3458A(rm, 'GPIB0::22::INSTR', title='3458A')
    instruments["3458A"].config_DCV(10)
    instruments["3458A"].config_NDIG(9)
    instruments["3458A"].config_NPLC(NPLC)
    instruments["3458A"].config_trigger_hold()

    
    instruments["3458B"]=HP3458A(rm, 'GPIB0::23::INSTR', title='3458B')
    instruments["3458B"].config_DCV(10)
    instruments["3458B"].config_NDIG(9)
    instruments["3458B"].config_NPLC(NPLC)
    instruments["3458B"].config_trigger_hold()
    
    instruments["W4950"]=W4950(rm, 'GPIB0::9::INSTR')
    instruments["W4950"].config_accuracy("HIGH")
    instruments["W4950"].config_DCV(10)
    instruments["W4950"].config_trigger_hold()

    scanner_sources = [(1, "ADRmu1"), (2, "ADRmu4"), (3, "ADRmu3"), (4, "ADRmu15"), (5, "ADRmu6"), (6, "ADRmu9"), (7, "ADRmu11"), (8, "ADRmu12"), (9, "ADRmu20"), ]
    scanner_meters = [(9, instruments["3458A"]),  (4, instruments["3458B"]), (2, instruments["W4950"]), ]
    
    switch=rotary_scanner()

    scanner_permutations = list(itertools.product(scanner_sources, scanner_meters))
        
    instruments["3458A"].acal_DCV()
    instruments["3458B"].acal_DCV()
    read_cal_params(instruments["3458A"])
    read_cal_params(instruments["3458B"])
    
    t=[["wiring", "rotary_scanner"],["guard","to_lo"], ]
        
    for perm in scanner_permutations:
        switch.switchingCloseRelay("a0") # Home switch
        switch.switchingCloseRelay("f0") # Home switch
        switch.switchingCloseRelay("e0") # Home switch
        switch.switchingCloseRelay("c0") # Home switch
        
        switch.switchingCloseRelay("e"+str(perm[0][0])) # Close source
        switch.switchingCloseRelay("c"+str(perm[0][0])) # Close source
        switch.switchingCloseRelay("a"+str(perm[1][0])) # Close meter
        switch.switchingCloseRelay("f"+str(perm[1][0])) # Close meter
        
        time.sleep(switch_delay)

        for measurement in range(nmeasurements):
            perm[1][1].trigger_once()
            read_inst_scanner(perm[1][1], perm[0][1])

    instruments["3458A"].blank_display()
    instruments["3458B"].blank_display()
        
    
    
    
    
    
    
def nbs430():

    nsamples = 10 
    switch_delay = 60 
    
    instruments["K34420A"]=HP34420A(rm, 'GPIB0::8::INSTR', title='Keysight 34420A')
    instruments["K34420A"].config_DCV("AUTO")
    instruments["K34420A"].config_trigger_hold()
    
    switch=rotary_scanner()

    scanner_sources = [(1, "ADRmu1"), (2, "ADRmu4"), (3, "ADRmu6"), (4, "ADRmu9"),  (5, "ADRmu12"),]
    scanner_permutations = set(itertools.combinations(scanner_sources, 2))
    
    while True:
        
        for perm in scanner_permutations:
        
            logging.info("Looking at "+perm[0][1]+" and "+perm[1][1])
        
            switch.switchingCloseRelay("a0") # Home switch
            switch.switchingCloseRelay("b0") # Home switch
            switch.switchingCloseRelay("c0") # Home switch
            switch.switchingCloseRelay("d0") # Home switch
            switch.switchingCloseRelay("e0") # Home switch
            switch.switchingCloseRelay("f0") # Home switch
            
            switch.switchingCloseRelay("a11") # Park + side switches
            switch.switchingCloseRelay("e11") # Park + side switches
            
            switch.switchingCloseRelay("f"+str(perm[0][0])) # Connect Source 1 -
            switch.switchingCloseRelay("b"+str(perm[1][0])) # to Source 2 -
            
            switch.switchingCloseRelay("c"+str(perm[0][0])) # Connect VM + to Source 1 +
            switch.switchingCloseRelay("d"+str(perm[1][0]+5)) # Connect VM - to Source 2 +
            
            time.sleep(switch_delay)
            
            polarity_1_samples = numpy.tile(0.0,nsamples)
            
            #instruments["K34420A"].trigger_once() # First reading sometimes unreliable? Bc autorange perhaps?
            #instruments["K34420A"].get_read_val()
            
            for sample in range(nsamples):
                instruments["K34420A"].trigger_once()
                reading = instruments["K34420A"].get_read_val()
                polarity_1_samples[sample]=reading
                logging.info("In 1 polarity read "+str(reading))
                
            switch.switchingCloseRelay("f11") # Park - side switches
            switch.switchingCloseRelay("b11") # Park - side switches
            
            switch.switchingCloseRelay("a"+str(perm[0][0])) # Connect Source 1 +
            switch.switchingCloseRelay("e"+str(perm[1][0])) # to Source 2 +
            
            switch.switchingCloseRelay("c"+str(perm[0][0]+5)) # Connect VM + to Source 1 -
            switch.switchingCloseRelay("d"+str(perm[1][0])) # Connect VM - to Source 2 -
            
            time.sleep(switch_delay)
            
            polarity_2_samples = numpy.tile(0.0,nsamples)
            
            for sample in range(nsamples):
                instruments["K34420A"].trigger_once()
                reading = instruments["K34420A"].get_read_val()
                polarity_2_samples[sample]=reading
                logging.info("In 2 polarity read "+str(reading))
                
            difference = (mean(polarity_1_samples)-mean(polarity_2_samples))/2
            logging.info("Difference looks like %.*f", 8, difference)
            writer.write("PPMhub", (perm[0][1]+" - "+perm[1][1]), instruments["K34420A"].get_title(), difference)
        
        switch.switchingCloseRelay("a11") # Park source switches
        switch.switchingCloseRelay("e11") # Park source switches
        switch.switchingCloseRelay("d"+str(perm[0][0])) # Short VM
        
        time.sleep(switch_delay)
        instruments["K34420A"].rel_off()
        
        for sample in range(nsamples):
            instruments["K34420A"].trigger_once()
            reading = instruments["K34420A"].get_read_val()
            polarity_2_samples[sample]=reading
            logging.info("Shorted read "+str(reading))
        
        writer.write("PPMhub", "Scanner short circuit", instruments["K34420A"].get_title(), mean(polarity_2_samples))
        instruments["K34420A"].rel()
        
    
    
    
try:
    #test_3458A()
    #test_W4950()
    #INL_3458A()
    #temperature_sweep()
    #scanner_once()
    #auto_ACAL_3458A()
    #noise_3458A()
    #pt100_scanner()
    #test_34420A()
    #scanner_34420A()
    #resistance_bridge_temperature_sweep()
    #test_rotary_scanner_episode_2()
    nbs430()


except (KeyboardInterrupt, SystemExit) as exErr:

    #for instrument in instruments:
    #    instruments[instrument].blank_display()
        
    logging.info("kthxbye")
    sys.exit(0)
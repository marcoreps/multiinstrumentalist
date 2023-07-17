#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import sys
import logging
from time import time
import numpy
from multiprocessing import Process, Lock
import sys
import sched
import itertools
import configparser
import datetime

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

gpiblock = Lock()
seriallock = Lock()
onewire_lock = Lock()

vxi_ip = "192.168.0.88"

instruments = dict()
#instruments["temp_short"]=TMP117(address=0x49, title="Short Temp Sensor")
#instruments["long_tmp117"]=TMP117(address=0x4A, title="Long TMP117")

#instruments["A5235"]=Arroyo(title="Arroyo 5235")
#instruments["K237"]=K237(ip=vxi_ip, gpib_address=8, lock=gpiblock, title="Bench K237")
#instruments["F5700A"]=F5700A(ip=vxi_ip, gpib_address=1, lock=gpiblock, title="Fluke 5700A")
#instruments["HP34401A"]=HP34401A(ip=vxi_ip, gpib_address=4, lock=gpiblock, title="Bench 34401A")
#instruments["3458A"]=3458A(ip=vxi_ip, gpib_address=22, lock=gpiblock, title="3458A")



def test_3458A():

    #switch=takovsky_scanner()
    #switch.switchingCloseRelay(channels[5])
    #switch.switchingCloseRelay(channels[6])

    NPLC = 200
    instruments["3458A"]=HP3458A(ip=vxi_ip, gpib_address=22, lock=gpiblock, title="3458A")
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
        
def nplc_3458A():
    #switch=takovsky_scanner()
    #switch.switchingCloseRelay(channels[5])
    #switch.switchingCloseRelay(channels[6])

    NPLC = 1
    instruments["3458A"]=HP3458A(ip=vxi_ip, gpib_address=22, lock=gpiblock, title="3458A")
    instruments["3458A"].config_DCV(10)
    instruments["3458A"].config_NDIG(9)
    instruments["3458A"].config_NPLC(NPLC)
    instruments["3458A"].config_trigger_auto()
    
    while True:
        writer.write("PPMhub",str(sys.argv[1]), instruments["3458A"].get_title(), instruments["3458A"].get_read_val())
        
def test_W4950():
    instruments["W4950"]=W4950(ip=vxi_ip, gpib_address=9, lock=gpiblock)
    NPLC = 200
    instruments["3458A"]=HP3458A(ip=vxi_ip, gpib_address=22, lock=gpiblock, title="3458A")
    instruments["3458A"].config_DCV(10)
    instruments["3458A"].config_NDIG(9)
    instruments["3458A"].config_NPLC(NPLC)
    instruments["3458A"].config_trigger_hold()
    instruments["3458A"].blank_display()

    
    while True:
        instruments["W4950"].trigger_once()
        writer.write("PPMhub",str(sys.argv[1]), instruments["W4950"].get_title(), instruments["W4950"].get_read_val())
        instruments["3458A"].trigger_once()
        writer.write("PPMhub",str(sys.argv[1]), instruments["3458A"].get_title(), instruments["3458A"].get_read_val())
        writer.write("lab_sensors", "Ambient Temp", instruments["long_tmp117"].get_title(), instruments["long_tmp117"].get_read_val())

    
             
def INL_3458A():
    timestr = time.strftime("%Y%m%d-%H%M%S_")
    instruments["F5700A"]=F5700A(ip=vxi_ip, gpib_address=1, lock=gpiblock, title="Reps 5700A")
    instruments["3458A"]=HP3458A(ip=vxi_ip, gpib_address=22, lock=gpiblock, title="Reps 3458A")
    instruments["3458B"]=HP3458A(ip=vxi_ip, gpib_address=23, lock=gpiblock, title="Reps 3458B")
    instruments["W4950"]=W4950(ip=vxi_ip, gpib_address=9, lock=gpiblock)
    
    instruments["3458A"].config_DCV(10)
    instruments["3458A"].config_NDIG(9)
    instruments["3458A"].config_trigger_auto()
    
    instruments["3458B"].config_DCV(10)
    instruments["3458B"].config_NDIG(9)
    instruments["3458B"].config_trigger_auto()
    
    umin = -10
    umax = 10
    ustep = 0.5
    wait_settle = 20
    
    instruments["F5700A"].out(str(umin)+"V")
    instruments["F5700A"].oper()
    instruments["F5700A"].rangelck()
    time.sleep(180)
    
    with open('csv/'+timestr+'REPS5700A_3458A_3458B_4950_INL.csv', mode='w') as csv_file:
        fieldnames = ['vref', '3458A_volt', '3458B_volt', 'W4950_volt']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for u in numpy.arange(umin, umax+0.01, ustep):
            instruments["F5700A"].out(str(u)+"V")
            logging.debug('main setting source to '+str(u)+'V')
            instruments["3458A"].config_NPLC(10)
            instruments["3458B"].config_NPLC(10)
            instruments["3458A"].config_trigger_auto()
            instruments["3458B"].config_trigger_auto()
            instruments["W4950"].config_trigger_auto()
            time.sleep(wait_settle)
            instruments["3458A"].config_NPLC(100)
            instruments["3458B"].config_NPLC(100)
            instruments["3458A"].config_trigger_hold()
            instruments["3458B"].config_trigger_hold()
            instruments["W4950"].config_trigger_hold()
            
            calibrator_out = u
            
            instruments["3458A"].trigger_once()
            HP3458A_out = float(instruments["3458A"].get_read_val())
            
            instruments["3458B"].trigger_once()
            HP3458B_out = float(instruments["3458B"].get_read_val())
            
            instruments["W4950"].trigger_once()
            W4950_out = float(instruments["W4950"].get_read_val())
            
            writer.writerow({'vref': calibrator_out, '3458A_volt': HP3458A_out, '3458B_volt': HP3458B_out, 'W4950_volt': W4950_out})


def temperature_sweep():

    #instruments["3458A"]=HP3458A(ip=vxi_ip, gpib_address=22, lock=gpiblock, title="3458A")
    #instruments["3458A"].config_DCV(10)
    #instruments["3458A"].config_NDIG(9)
    #instruments["3458A"].config_NPLC(50)
    #instruments["3458A"].config_trigger_auto()
    
    instruments["arroyo"]=Arroyo(dev='/dev/ttyUSB0', baud=38400, title='Arroyo TECSource')
    
    instruments["3458B"]=HP3458A(ip=vxi_ip, gpib_address=23, lock=gpiblock, title="3458B")
    instruments["3458B"].config_DCV(10)
    instruments["3458B"].config_NDIG(9)
    instruments["3458B"].config_NPLC(50)
    instruments["3458B"].config_trigger_auto()
    
    tmin = 19
    tmax = 35
    tstep = 0.1
    wait_settle = 60

    sch = sched.scheduler(time.time, time.sleep)
    #sch.enter(10, 10, recursive_read_inst, argument=(sch, 10, 10, instruments["3458A"], "Vz"))
    sch.enter(10, 10, recursive_read_inst, argument=(sch, 10, 10, instruments["3458B"], "Vz"))
    sch.enter(10, 10, recursive_read_inst, argument=(sch, 10, 10, instruments["arroyo"], "Chamber Temp"))
    i=60*10
    for t in numpy.arange(tmin, tmax+0.01, tstep):
    #for t in numpy.flip(numpy.arange(tmin, tmax+0.01, tstep)):
        i+=wait_settle
        sch.enter(i, 9, instruments["arroyo"].out, argument=([t]))
    i+=30*60
    #for t in numpy.arange(tmin, tmax+0.01, tstep):
    for t in numpy.flip(numpy.arange(tmin, tmax+0.01, tstep)):
        i+=wait_settle
        sch.enter(i, 9, instruments["arroyo"].out, argument=([t]))
    logging.info("This temperature sweep will take "+str(datetime.timedelta(seconds=i)))
    sch.run()

def read_inst_scanner(inst, dut, bucket="PPMhub"):
    logging.debug("Reading inst with title %s after a measurement of %s" % (inst.get_title(), dut))
    if inst.is_readable():
        writer.write(bucket, dut, inst.get_title(), inst.get_read_val())
        logging.debug('debug step')
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

# IV    Br    N   channels[4] ADRmu107 +
# IV    BrW   P   channels[4] ADRmu107 -
# IV    Or    N   channels[5] 
# IV    OrW   P   channels[5] 
# IV    Bl    N   channels[6] 3458A +
# IV    BlW   P   channels[6] 3458A -
# IV    Gr    N   channels[7] 3458B +
# IV    GrW   P   channels[7] 3458B -

    switch_delay = 10
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
    
    scanner_sources = [(channels[0], "ADRmu1"), (channels[1], "ADRmu2"), (channels[2], "ADRmu3"), (channels[3], "ADRmu4"), (channels[4], "ADRmu107")]
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
            sch.enter(seconds, 10, read_inst_scanner, argument=(perm[1][1], perm[0][1]))
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
    #sch.enter(10, 11, recursive_read_inst, argument=(sch, 10, 11, instruments["temp_long"]))
    #sch.enter(1, 11, recursive_read_inst, argument=(sch, 1, 11, instruments["temp_ADRmu1"]))
    #sch.enter(1, 11, recursive_read_inst, argument=(sch, 1, 11, instruments["temp_ADRmu2"]))
    #sch.enter(61*10, 9, recursive_read_inst, argument=(sch, 61*10, 9, HP3458A_temperature))
    #sch.enter(61*10, 9, recursive_read_inst, argument=(sch, 61*10, 9, HP3458B_temperature))
    sch.run()
    
def scanner_once():

# III   Br    N   channels[0] ADRmu1 +
# III   BrW   P   channels[0] ADRmu1 -
# III   Or    N   channels[1] F731B +
# III   OrW   P   channels[1] F731B -
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
# II    Or    N   channels[11]  3458A +
# II    OrW   P   channels[11]  3458A -

# I     Br    N   channels[12]  
# I     BrW   P   channels[12]  
# I     Or    N   channels[13]  
# I     OrW   P   channels[13]  
# I     Bl    N   channels[14]  
# I     BlW   P   channels[14]  
# I     Gr    N   channels[15]  
# I     GrW   P   channels[15]  

    switch_delay = 60
    NPLC = 100
    nmeasurements = 20
    
    instruments["3458A"]=HP3458A(ip=vxi_ip, gpib_address=22, lock=gpiblock, title="3458A")
    instruments["3458A"].config_DCV(10)
    instruments["3458A"].config_NDIG(9)
    instruments["3458A"].config_NPLC(NPLC)
    instruments["3458A"].config_trigger_hold()

    
    instruments["3458B"]=HP3458A(ip=vxi_ip, gpib_address=23, lock=gpiblock, title="3458B")
    instruments["3458B"].config_DCV(10)
    instruments["3458B"].config_NDIG(9)
    instruments["3458B"].config_NPLC(NPLC)
    instruments["3458B"].config_trigger_hold()

    #scanner_sources = [(channels[0], "ADRmu1"), (channels[1], "ADRmu2"), (channels[2], "ADRmu3"), (channels[3], "ADRmu15"), (channels[4], "ADRmu9"), (channels[6], "ADRmu11"), (channels[7], "ADRmu12"), (channels[8], "F731B"), (channels[12], "ADRmu6"), ]
    scanner_sources = [(channels[0], "ADRmu1"), (channels[2], "ADRmu3"), (channels[3], "ADRmu15"), (channels[4], "ADRmu9"), (channels[6], "ADRmu11"), (channels[7], "ADRmu12"), (channels[5], "ADRmu6"), (channels[1], "F731B"), ]
    scanner_meters = [(channels[11], instruments["3458A"]),  (channels[8], instruments["3458B"]), ]

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
        
    
    #sch.enter(1, 11, recursive_read_inst, argument=(sch, 1, 11, instruments["temp_short"]))
    #sch.enter(10, 11, recursive_read_inst, argument=(sch, 10, 11, instruments["long_tmp117"], "Ambient Temp", "lab_sensors"))
    #sch.enter(1, 11, recursive_read_inst, argument=(sch, 1, 11, instruments["temp_ADRmu1"]))
    #sch.enter(1, 11, recursive_read_inst, argument=(sch, 1, 11, instruments["temp_ADRmu2"]))
    #sch.enter(61*10, 9, recursive_read_inst, argument=(sch, 61*10, 9, HP3458A_temperature))
    #sch.enter(61*10, 9, recursive_read_inst, argument=(sch, 61*10, 9, HP3458B_temperature))
    logging.info("This round will take "+str(datetime.timedelta(seconds=seconds)))
    sch.run()
    instruments["3458A"].blank_display()
    instruments["3458B"].blank_display()
  
def recursive_read_inst(sch, interval, priority, inst, name, bucket="Temperature sweep"):
    sch.enter(interval, priority, recursive_read_inst, argument=(sch, interval, priority, inst, name, bucket))
    if inst.is_readable():
        time.sleep(1)
        writer.write(bucket, name, inst.get_title(), inst.get_read_val())
        
        
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

def k182():
    instruments["k182"]=K182(ip=vxi_ip, gpib_address=8, lock=gpiblock)
    instruments["k182"].default()
    while True:
        writer.write("PPMhub", str(sys.argv[1]), instruments["k182"].get_title(), instruments["k182"].get_data())
        #writer.write("lab_sensors", "Ambient Temp", instruments["long_tmp117"].get_title(), instruments["long_tmp117"].get_read_val())
        
def hp3458A_diff():
    NPLC = 100
    instruments["3458A"]=HP3458A(ip=vxi_ip, gpib_address=22, lock=gpiblock, title="3458A")
    instruments["3458A"].config_NDIG(9)
    instruments["3458A"].config_NPLC(NPLC)
    instruments["3458A"].config_trigger_auto()
    
    while True:
        if instruments["3458A"].is_readable():
                t=[["wiring", "direct"],["guard","open"], ["meter","3458A"]]
                writer.write("PPMhub", str(sys.argv[1]), instruments["3458A"].get_title(), instruments["3458A"].get_read_val(), tags=t)
        writer.write("lab_sensors", "Ambient Temp", instruments["long_tmp117"].get_title(), instruments["long_tmp117"].get_read_val())
        time.sleep(1)
        
    
def log_cal_params():
    
    instruments["3458A"]=HP3458A(ip=vxi_ip, gpib_address=22, lock=gpiblock, title="3458A")
    instruments["3458A"].config_trigger_hold()
    instruments["3458A"].blank_display()
    
    instruments["3458B"]=HP3458A(ip=vxi_ip, gpib_address=23, lock=gpiblock, title="3458B")
    instruments["3458B"].config_trigger_hold()
    instruments["3458B"].blank_display()
    
    read_cal_params(instruments["3458A"])
    read_cal_params(instruments["3458B"])
 



if __name__ == '__main__':
    try:
        #test_3458A()
        #test_W4950()
        #INL_3458A()
        temperature_sweep()
        #scanner2()
        #scanner_once()
        #auto_ACAL_3458A()
        #noise_3458A()
        #pt100_scanner()
        #readstb_test()
        #k182()
        #hp3458A_diff()
        #log_cal_params()
        #nplc_3458A()


        
    except (KeyboardInterrupt, SystemExit) as exErr:
        logging.info("kthxbye")
        sys.exit(0)
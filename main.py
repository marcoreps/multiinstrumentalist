#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyvisa
import csv
import logging
from time import time
from datetime import datetime, timedelta
import numpy
import sys
import sched
import itertools
import configparser
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
    instruments["3458B"]=HP3458A(rm, 'TCPIP::192.168.0.5::gpib0,23', title='3458B')
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


def read_inst_scanner(inst, dut, bucket="PPMhub"):
    logging.debug("Reading inst with title %s after a measurement of %s" % (inst.get_title(), dut))
    val=0.0
    #for i in range(10):
     #   val+=float(inst.get_read_val())
    writer.write(bucket, dut, inst.get_title(), inst.get_read_val())
    #logging.info("%s read %s = %s" % (inst.get_title(), dut, str(val)))



        
    
def scanner_once():

# III   Br    N   channels[0] ADRmu1 +
# III   BrW   P   channels[0] ADRmu1 -
# III   Or    N   channels[1] 3458P / W4950 +
# III   OrW   P   channels[1] 3458P / W4950 -
# III   Bl    N   channels[2] ADRmu3 +
# III   BlW   P   channels[2] ADRmu3 -
# III   Gr    N   channels[3] ADRmu15 +
# III   GrW   P   channels[3] ADRmu15 -

# IV    Br    N   channels[4]
# IV    BrW   P   channels[4]
# IV    Or    N   channels[5]
# IV    OrW   P   channels[5]
# IV    Bl    N   channels[6]
# IV    BlW   P   channels[6]
# IV    Gr    N   channels[7]
# IV    GrW   P   channels[7]

# II    Br    N   channels[8]   3458B +
# II    BrW   P   channels[8]   3458B -
# II    Or    N   channels[9]   
# II    OrW   P   channels[9]   
# II    Bl    N   channels[10]  ADRmu4 +
# II    BlW   P   channels[10]  ADRmu4 +
# II    Gr    N   channels[11]  ADRmu20 +
# II    GrW   P   channels[11]  ADRmu20 -

# I     Br    N   channels[12] ADRmu9 +
# I     BrW   P   channels[12] ADRmu9 -
# I     Or    N   channels[13]
# I     OrW   P   channels[13]
# I     Bl    N   channels[14] ADRmu11 +
# I     BlW   P   channels[14] ADRmu11 -
# I     Gr    N   channels[15] ADRmu12 +
# I     GrW   P   channels[15] ADRmu12 -

    switch_delay = 120
    NPLC = 100
    nmeasurements = 20
    
    
    instruments["3458B"]=HP3458A(rm, 'TCPIP::192.168.0.5::gpib0,23', title='3458B')
    instruments["3458B"].config_DCV(10)
    instruments["3458B"].config_NDIG(9)
    instruments["3458B"].config_NPLC(NPLC)
    instruments["3458B"].config_trigger_hold()
    
    instruments["3458P"]=HP3458A(rm, 'TCPIP::192.168.0.5::gpib0,22', title='3458P')
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

    
    scanner_sources = [(channels[0], "ADRmu1"), (channels[2], "ADRmu3"), (channels[3], "ADRmu15"), (channels[12], "ADRmu9"), (channels[14], "ADRmu11"), (channels[15], "ADRmu12"), (channels[10], "ADRmu4"), (channels[11], "ADRmu20"), ]
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
    val=0.0
    for i in range(10):
        val+=float(inst.get_read_val())
    writer.write(bucket, name, inst.get_title(), val/10)
    logging.info("%s was not ready for read_cal_params." % (inst.get_title()))
    
              


        
        
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
    instruments["K34420A"]=HP34420A(rm, 'TCPIP::192.168.0.5::gpib0,8', title='Keysight 34420A')
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
        #scanner_sources = [(1, "ADRmu6"), (2, "ADRmu3"), (3, "ADRmu20"), (4, "ADRmu11"),  (5, "ADRmu15"),]
        #scanner_sources = [(1, "ADRmu4"), (2, "ADRmu3"), (3, "ADRmu1"), (4, "ADRmu20"),  (5, "ADRmu11"),]
        #scanner_sources = [(1, "ADRmu9"), (2, "ADRmu12"), (3, "ADRmu15"), (4, "ADRmu20"),  (5, "ADRmu1"),]
        #scanner_sources = [(1, "ADRmu9"), (2, "ADRmu12"), (3, "ADRmu11"), (4, "ADRmu3"),  (5, "ADRmu1"),]

        
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
                logging.info("Looking at "+perm[0][1]+" and "+perm[1][1])
                
                if(perm[0][1]>perm[1][1]): # We don't need both V1-V2 and V2-V1
                    logging.info("swappy")
                    perm=[perm[1],perm[0]] # so we use alphabetically sorted pairs
            
                logging.debug("error_counter "+str(error_counter))
                
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



    nsamples = 100
    switch_delay = 60
    error_counter = 0
    
    tmin = 18
    tmax = 28
    tstep = 0.1
    measurements_per_tstep = 20
    
    instruments["2182a"]=K2182A(rm, 'gpib0::4::INSTR', title='Keithley 2182a')
    instruments["2182a"].config_DCV()
    
    instruments["arroyo"]=Arroyo(dev='/dev/ttyUSB0', baud=38400, title='Arroyo TECSource')
    
    instruments["1281"]=D1281(rm, 'gpib0::16::INSTR', title='1281')
    
    i2c_address = 0x4a
    instruments["tmp117"] = Tmp117(i2c_address)
    instruments["tmp117"].init()
    instruments["tmp117"].setConversionMode(0x11)
    instruments["tmp117"].oneShotMode()
    
    switch=takovsky_scanner()

    
    polarity_1_samples = numpy.tile(0.0,nsamples)
    polarity_2_samples = numpy.tile(0.0,nsamples)
    
    from itertools import chain
    temperatures = chain(numpy.arange(23, tmax+0.01, tstep), numpy.flip(numpy.arange(23, tmax+0.01, tstep)), numpy.flip(numpy.arange(tmin-0.01, 23, tstep)), numpy.arange(tmin-0.01, 23, tstep))
    #temperatures = chain([28.0,28.0], numpy.flip(numpy.arange(23.0, 28.00001, tstep)), [23.0,23.0,23.0])
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
                    logging.debug("polarity 1 read "+str(reading))
                    
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
                


        
def measure(instruments, switch):
    instruments["tmp117"].oneShotMode()
    while not instruments["tmp117"].dataReady():
        time.sleep(1)
    tmp117 = instruments["tmp117"].readTempC()
    writer.write("Temperature sweep", "Ambient_Temp", "TMP117_on_calibratorpi", tmp117)
    logging.info("ambient tmp117="+str(tmp117))
    
    
    arroyo=instruments["arroyo"].get_read_val()
    writer.write("Temperature sweep", "Chamber Temp", instruments["arroyo"].get_title(), arroyo)
    logging.info("arroyo chamber="+str(arroyo))
    
    
    switch.switchingCloseRelay(channels[13])
    switch.switchingCloseRelay(channels[1])
    instruments["8508A"].config_pt100()
    time.sleep(60)
    pt100=instruments["8508A"].get_read_val()
    writer.write("Temperature sweep", "Thermometer Well PT100", instruments["8508A"].get_title(), pt100)
    logging.info("thermometer well pt100="+str(pt100))
    switch.switchingOpenRelay(channels[13])
    switch.switchingOpenRelay(channels[1])
    
    
    switch.switchingCloseRelay(channels[12])
    switch.switchingCloseRelay(channels[0])
    instruments["8508A"].config_TRUE_OHMS(10000)
    time.sleep(60)
    sr104=instruments["8508A"].get_read_val()
    writer.write("Temperature sweep", "SR104", instruments["8508A"].get_title(), sr104)
    logging.info("SR104="+str(sr104))
    switch.switchingOpenRelay(channels[12])
    switch.switchingOpenRelay(channels[0])
    
    
    switch.switchingCloseRelay(channels[15])
    switch.switchingCloseRelay(channels[3])
    instruments["8508A"].config_TRUE_OHMS(10000)
    time.sleep(60)
    F742A=instruments["8508A"].get_read_val()
    writer.write("Temperature sweep", "F742A", instruments["8508A"].get_title(), F742A)
    logging.info("F742A="+str(F742A))
    switch.switchingOpenRelay(channels[15])
    switch.switchingOpenRelay(channels[3])
    
    
    switch.switchingCloseRelay(channels[8])
    switch.switchingCloseRelay(channels[4])
    instruments["8508A"].config_TRUE_OHMS(10000)
    time.sleep(60)
    sr104therm=instruments["8508A"].get_read_val()
    writer.write("Temperature sweep", "SR104 Thermistor", instruments["8508A"].get_title(), sr104therm)
    logging.info("SR104 Thermistor="+str(sr104therm))
    switch.switchingOpenRelay(channels[8])
    switch.switchingOpenRelay(channels[4])
    
    
    switch.switchingCloseRelay(channels[14])
    switch.switchingCloseRelay(channels[2])
    instruments["8508A"].config_TRUE_OHMS(10000)
    time.sleep(60)
    VHP10k=instruments["8508A"].get_read_val()
    writer.write("Temperature sweep", "VHP10k", instruments["8508A"].get_title(), VHP10k)
    logging.info("VHP10k="+str(VHP10k))
    switch.switchingOpenRelay(channels[14])
    switch.switchingOpenRelay(channels[2])
    


def ratio_8508a():

    logging.info("Welcome to ratio_8508a()")

    tstart = 23.0
    tmin = 18.0
    tmax = 28.0
    k_per_hour = 0.07
    dwell_seconds = 60.0*60.0*20
    measurement_every_seconds = 60*20
    

    dt_object = datetime(2025, 4, 29, 10, 39, 27)
    start_time = datetime(2025, 5, 13, 13, 00)
    start_time = time.mktime(start_time.timetuple())
    #start_time = time.time()
    last_measurement = time.time()
    logging.info("first temperature = "+str(get_target_temperature(
            start_time=start_time,
            start_temp=tstart,
            rise_rate=k_per_hour,
            max_temp=tmax,
            dwell=dwell_seconds,
            min_temp=tmin
        )))

    
    i2c_address = 0x4a
    instruments["tmp117"] = Tmp117(i2c_address)
    instruments["tmp117"].init()
    instruments["tmp117"].setConversionMode(0x11)


    instruments["arroyo"]=Arroyo(dev='/dev/ttyUSB0', baud=38400, title='Arroyo TECSource')

    instruments["8508A"]=F8508A(rm, 'gpib0::9::INSTR', title='Fluke 8508A')
    instruments["8508A"].config_TRUE_OHMS(10000)
    instruments["8508A"].config_trigger_hold()
    
    switch=takovsky_scanner()
    switch.switchingSet4Wire(True)
    
    # C     OrW    CHA_P                    I+ DMM
    # C     Bl     CHA_N                    I- DMM
    # C     BlW    CHB_P                    Sense+ DMM  
    # C     Or     CHB_N                    Sense- DMM
    
    # I     Br     CHA_N   channels[12]     SR104 I- Terminal 1
    # I     BrW    CHA_P   channels[12]     SR104 I+ Terminal 4
    # I     Or     CHA_N   channels[13]     PT100 I-
    # I     OrW    CHA_P   channels[13]     PT100 I+
    # I     Bl     CHA_N   channels[14]     VHP10k I-
    # I     BlW    CHA_P   channels[14]     VHP10k I+
    # I     Gr     CHA_N   channels[15]     742A I-
    # I     GrW    CHA_P   channels[15]     742A I+
    
    # II    Br     CHA_N   channels[8]      SR104 Thermistor I- Terminal 4
    # II    BrW    CHA_P   channels[8]      SR104 Thermistor I+ Terminal 1
    
    # III   Br     CHB_N   channels[0]      SR104 Sense- Terminal 2
    # III   BrW    CHB_P   channels[0]      SR104 Sense+ Terminal 3
    # III   Or     CHB_N   channels[1]      PT100 Sense-
    # III   OrW    CHB_P   channels[1]      PT100 Sense+
    # III   Bl     CHB_N   channels[2]      VHP10k Sense-
    # III   BlW    CHB_P   channels[2]      VHP10k Sense+
    # III   Gr     CHB_N   channels[3]      742A Sense-
    # III   GrW    CHB_P   channels[3]      742A Sense+
    
    # IV    Br     CHB_N   channels[4]      SR104 Thermistor Sense-
    # IV    BrW    CHB_P   channels[4]      SR104 Thermistor Sense-
    
    triggered = 0
    
    while True:
        
        if time.time()-last_measurement >= measurement_every_seconds:
            logging.debug("measurement triggered")
            measure(instruments, switch)
        
        new_setpoint=get_target_temperature(
            start_time=start_time,
            start_temp=tstart,
            rise_rate=k_per_hour,
            max_temp=tmax,
            dwell=dwell_seconds,
            min_temp=tmin
        )
        instruments["arroyo"].out(new_setpoint)
        
        time.sleep(10)

        
        
        
def tmp():
    i2c_address = 0x4a
    instruments["tmp117"] = Tmp117(i2c_address)
    instruments["tmp117"].init()
    instruments["tmp117"].setConversionMode(0x11)
    
    while True:
        instruments["tmp117"].oneShotMode()
        while not instruments["tmp117"].dataReady():
            time.sleep(1)
        tmp117 = instruments["tmp117"].readTempC()
        writer.write("Temperature sweep", "Ambient_Temp", "TMP117_on_calibratorpi", tmp117)
        logging.info("ambient tmp117="+str(tmp117))
        time.sleep(30)

def get_target_temperature(
    start_time: datetime,
    start_temp: float,
    rise_rate: float,  # °C per hour
    max_temp: float,
    dwell: timedelta,
    min_temp: float
) -> float:
    """
    Calculates the target temperature at a given time (in seconds since the epoch)
    based on the defined temperature sweep plan.

    Args:
        start_time: The time object representing the start of the temperature sweep.
        start_temp: The initial temperature (°C).
        rise_rate: The rate of temperature increase (°C per hour).
        max_temp: The maximum temperature (°C).
        dwell: Seconds to hold at the maximum temperature.
        min_temp: The minimum temperature (°C).

    Returns:
        The target temperature (°C) at the time.
    """
    current_time = time.time()
    seconds_elapsed = current_time - start_time
    logging.debug("seconds_elapsed ="+str(seconds_elapsed))


    # Phase 1: Dwell at start_temp
    if seconds_elapsed < dwell:
        return start_temp
        
    # Phase 2: Rise to max_temp
    phase_2_seconds = dwell+(max_temp - start_temp) / rise_rate * 3600
    if seconds_elapsed < phase_2_seconds:
        return start_temp + rise_rate * ((seconds_elapsed-dwell) / 3600)

    # Phase 3: Dwell at max_temp
    phase_3_seconds = dwell+phase_2_seconds
    if seconds_elapsed < phase_3_seconds:
        return max_temp

    # Phase 4: Fall to start_temp
    phase_4_seconds = phase_3_seconds+(max_temp - start_temp) / rise_rate * 3600
    if seconds_elapsed < phase_4_seconds:
        return max_temp - rise_rate * ((seconds_elapsed-phase_3_seconds) / 3600)
        
    # Phase 5: Dwell at start_temp
    phase_5_seconds = dwell+phase_4_seconds
    if seconds_elapsed < phase_5_seconds:
        return start_temp

    # Phase 6: Fall to min_temp
    phase_6_seconds = phase_5_seconds+(start_temp - min_temp) / rise_rate * 3600
    if seconds_elapsed < phase_6_seconds:
        return start_temp - rise_rate * ((seconds_elapsed-phase_5_seconds) / 3600)
        
    # Phase 7: Dwell at min_temp
    phase_7_seconds = dwell+phase_6_seconds
    if seconds_elapsed < phase_7_seconds:
        return min_temp
        
    # Phase 8: Rise to start_temp
    phase_8_seconds = phase_7_seconds+(start_temp - min_temp) / rise_rate * 3600
    if seconds_elapsed < phase_8_seconds:
        return min_temp + rise_rate * ((seconds_elapsed-phase_7_seconds) / 3600)
        
    # Phase 9: Remain at start_temp
    return start_temp 
    
    
def get_target_temperature_min_first(
    start_time: datetime,
    start_temp: float,
    rise_rate: float,  # °C per hour
    max_temp: float,
    dwell: timedelta,
    min_temp: float
) -> float:
    """
    Calculates the target temperature at a given time (in seconds since the epoch)
    based on the defined temperature sweep plan.

    Args:
        start_time: The time object representing the start of the temperature sweep.
        start_temp: The initial temperature (°C).
        rise_rate: The rate of temperature increase (°C per hour).
        max_temp: The maximum temperature (°C).
        dwell: Seconds to hold at the maximum temperature.
        min_temp: The minimum temperature (°C).

    Returns:
        The target temperature (°C) at the time.
    """
    current_time = time.time()
    seconds_elapsed = current_time - start_time
    logging.debug("seconds_elapsed ="+str(seconds_elapsed))

    # Phase 1: Dwell at start_temp
    if seconds_elapsed < dwell:
        return start_temp
        
    # Phase 2: Fall to min_temp
    phase_2_seconds = dwell+(start_temp - min_temp) / rise_rate * 3600
    if seconds_elapsed < phase_2_seconds:
        return start_temp - rise_rate * ((seconds_elapsed-dwell) / 3600)
        
    # Phase 3: Dwell at min_temp
    phase_3_seconds = dwell+phase_2_seconds
    if seconds_elapsed < phase_3_seconds:
        return min_temp
        
    # Phase 4: Rise to start_temp
    phase_4_seconds = phase_3_seconds+(start_temp - min_temp) / rise_rate * 3600
    if seconds_elapsed < phase_4_seconds:
        return min_temp + rise_rate * ((seconds_elapsed-phase_3_seconds) / 3600)
        
    # Phase 5: Dwell at start_temp
    phase_5_seconds = dwell+phase_4_seconds
    if seconds_elapsed < phase_5_seconds:
        return start_temp
        
    # Phase 6: Rise to max_temp
    phase_6_seconds = phase_5_seconds+(max_temp - start_temp) / rise_rate * 3600
    if seconds_elapsed < phase_6_seconds:
        return start_temp + rise_rate * ((seconds_elapsed-phase_5_seconds) / 3600)

    # Phase 7: Dwell at max_temp
    phase_7_seconds = dwell+phase_6_seconds
    if seconds_elapsed < phase_7_seconds:
        return max_temp

    # Phase 8: Fall to start_temp
    phase_8_seconds = phase_7_seconds+(max_temp - start_temp) / rise_rate * 3600
    if seconds_elapsed < phase_8_seconds:
        return max_temp - rise_rate * ((seconds_elapsed-phase_7_seconds) / 3600)

    # Phase 9: Remain at start_temp
    return start_temp 
    

def smu_tec_perhaps():

    from simple_pid import PID
    
    tstart = 23.0
    tmin = 18.0
    tmax = 28.0
    k_per_hour = 0.3
    dwell_seconds = 60.0*60*2
    measurement_every_seconds = 60
    
    start_time = time.time()
    last_measurement = time.time()


    i2c_address = 0x4a
    instruments["tmp117"] = Tmp117(i2c_address)
    instruments["tmp117"].init()
    instruments["tmp117"].setConversionMode(0x11)
    
    instruments["2400"]=K2400(rm, 'TCPIP::192.168.0.5::gpib0,24', title='Keithley 2400')
    instruments["2400"].set_source_type("CURRENT")
    instruments["2400"].set_source_current_range(1)
    instruments["2400"].set_source_current(0)
    instruments["2400"].set_output_on()
    instruments["2400"].enable_display_upper_text()
    
    
    instruments["K34420A"]=HP34420A(rm, 'TCPIP::192.168.0.5::gpib0,8', title='Keysight 34420A')
    instruments["K34420A"].config_DCV("0")
    instruments["K34420A"].config_trigger_hold()
    
    
    instruments["3458B"]=HP3458A(rm, 'TCPIP::192.168.0.5::gpib0,23', title='3458B')
    instruments["3458B"].config_pt100()
    #instruments["3458B"].config_NDIG(9)
    #instruments["3458B"].config_NPLC(100)
    instruments["3458B"].config_trigger_hold()
    
    
    instruments["tmp119"]=tmp119_mg24()

    
    
    #pid = PID(0.7, 0.01, 4.00, setpoint=tstart)
    pid = PID(10, 0.001, 0.00, setpoint=tstart) # for L&N hamon
    pid.output_limits = (-1,1)
    
    triggered = 0
    last_pid_i = 0
    
    while True:
        #instruments["tmp117"].oneShotMode()
        #while not instruments["tmp117"].dataReady():
        #    time.sleep(0.2)
        #tmp117 = instruments["tmp117"].readTempC()
        
        instruments["3458B"].trigger_once()
        tmp117 = float(instruments["3458B"].get_read_val())
        
        instruments["2400"].set_display_upper_text(str(round(tmp117, 3))+" C")
        
        logging.debug("temperautre sensed="+str(tmp117))
        control = pid(tmp117)
        logging.debug("control="+str(control))
        
        if time.time()-last_measurement >= measurement_every_seconds and not triggered:
            logging.debug("nvm measurement triggered")
            logging.info("temperautre target="+str(pid.setpoint))
            instruments["K34420A"].trigger_once()
            triggered = 1
            writer.write("Temperature sweep", "reference resistor temp", instruments["tmp119"].get_title(), float(instruments["tmp119"].get_read_val()))

        if time.time()-last_measurement >= measurement_every_seconds+10:
            logging.debug("nvm is being read")
            nvm = float(instruments["K34420A"].get_read_val())
            writer.write("Small Temperature Sweep", "Bridge_voltage", instruments["K34420A"].get_title(), nvm)
            writer.write("Small Temperature Sweep", "DUT_Temperature", "Well PT100", tmp117)
            last_measurement=time.time()
            triggered = 0
        
        instruments["2400"].set_source_current(control)
        logging.debug("new TEC current:"+str(control))

        setpoint=get_target_temperature(
            start_time=start_time,
            start_temp=tstart,
            rise_rate=k_per_hour,
            max_temp=tmax,
            dwell=dwell_seconds,
            min_temp=tmin
        )
        logging.debug("temperautre target="+str(setpoint))
        
        pid.setpoint = setpoint
        
        print(pid.components)
        
        
        if abs(setpoint-tmp117)>11.0: #things are getting out of control
            instruments["2400"].set_output_off()
            logging.error("Thermal runaway")
            logging.error("This ends here")
            break

        
def tmp119_vs_pt100():
    instruments["3458B"]=HP3458A(rm, 'TCPIP::192.168.0.5::gpib0,23', title='3458B')
    instruments["3458B"].config_pt100()
    #instruments["3458B"].config_NDIG(9)
    #instruments["3458B"].config_NPLC(100)
    instruments["3458B"].config_trigger_hold()
    
    instruments["tmp119"]=tmp119_mg24()
    
    while(True):
        time.sleep(10)
        instruments["3458B"].trigger_once()
        writer.write("Temperature sweep", "Ambient_Temp", "pico SE012 PT100 3458A", float(instruments["3458B"].get_read_val()))
        writer.write("Temperature sweep", "Ambient_Temp", instruments["tmp119"].get_title(), float(instruments["tmp119"].get_read_val()))
        


    
try:
    #test_3458A()
    #test_W4950()
    #scanner_once()
    #resistance_bridge_temperature_sweep()
    #nbs430()
    #resistance_bridge()
    #f8508a_logger()
    #voltage_temperature_sweep()
    #resistance_bridge_reversal()
    #ratio_1281()
    #tmp()
    #ratio_8508a()
    smu_tec_perhaps()
    #tmp119_vs_pt100()


except (KeyboardInterrupt, SystemExit) as exErr:

    #for instrument in instruments:
    #    instruments[instrument].blank_display()
        
    logging.info("kthxbye")
    sys.exit(0)
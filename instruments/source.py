#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyvisa
import time
import logging
import re

class K237:


#define MODE_DC		                   writeToDevice("F0,0X");
#define MODE_SWEEP	                   writeToDevice("F0,1X");
#define DATA_FORMAT_OUTPUT_TICK        writeToDevice("G15,0,0X");
#define DATA_FORMAT_OUTPUT_SWEEP       writeToDevice("G4,2,2X");
#define TRIGGER_ACTION		           writeToDevice("H0X");

#define FILTER_DISABLE		           writeToDevice("P0X");
#define FILTER_2READINGS	           writeToDevice("P1X");
#define FILTER_4READINGS	           writeToDevice("P2X");
#define FILTER_8READINGS	           writeToDevice("P3X");
#define FILTER_16READINGS	           writeToDevice("P4X");
#define FILTER_32READINGS	           writeToDevice("P5X");


    read_val = 0.0
    
    def __init__(self, ip, gpib_address, lock, title='Keithley 237'):
        self.title = title
        logging.debug(self.title+' init started')
        self.lock = lock
        self.ip = ip
        self.gpib_address = gpib_address
        self.lock.acquire()
        try:
            self.instr =  vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
            self.instr.clear()
            self.instr.write("J0X") # Factory init
            self.instr.write("F0,0X") # Source V DC
            self.instr.write("H0X") # Immediate trigger
            self.instr.write("G4,2,0X") # Output measure value with no prefix, no suffix
            self.instr.write("S3X") # 20ms integration time
            self.instr.write("V1X") # Enable 1000V range
            self.instr.write("B7.1,0,0X") # Bias 7.1V autorange
            self.instr.write("L500E-6,4X") # 500µA compliance auto range
            self.instr.close()
        except:
            logging.error("Error in %s __init__" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
        
        
    def oper(self):
        self.connect()
        try:
            self.instr.write("N1X")
            self.instr.close()
        except:
            logging.error("Error in %s oper" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
            
    def stby(self):
        self.connect()
        try:
            self.instr.write("N0X")
            self.instr.close()
        except:
            logging.error("Error in %s stby" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
        
        
    def connect(self):
        logging.debug(self.title+' waiting for lock')
        self.lock.acquire()
        self.instr.open()
        
        
    def get_title(self):
        return self.title
        
        
    def get_read_val(self):
        logging.debug(self.title+' get_read_val started')
        self.lock.acquire()
        try:
            self.read_val = self.instr.read()
            self.instr.close()
        except:
            logging.error("Error in %s get_read_val" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
        
        logging.debug("%s reading %s" % (self.title, self.read_val))
        return self.read_val

        
    def is_ready_to_read(self):
        return True
        
        
    def is_measuring(self):
        return False       
        
    def measure(self):
        pass
        
        
        
        
        
    
    

class F5700A:

    readable = True
    read_val = 0
    
    def measure(self):
        logging.debug(self.title+' measure started')
        self.read_val = self.instr.query("OUT?")
    
    def is_readable(self):
        return self.readable

    def __init__(self, resource_manager, resource_name, title='FLuke 5700A'):
        self.title = title
        logging.debug(self.title+' init started')
        self.rm = resource_manager
        self.rn = resource_name
        self.instr = self.rm.open_resource(self.rn)
        self.instr.timeout = 60*1000
        self.instr.clear()
        self.instr.write("*RST")
        self.instr.write("STBY")
        self.instr.write("EXTGUARD OFF")
        logging.info("*IDN? -> "+self.instr.query("*IDN?"))
        
        
    def out(self,out_cmd):
        self.instr.write("OUT "+out_cmd)

    def oper(self):
        self.instr.write("OPER")

    def stby(self):
        self.instr.write("STBY")

    def get_title(self):
        return self.title
        
    def get_read_val(self):
        logging.debug(self.title+' get_read_val started')
        tokenized_read_val = re.split(',',self.read_val)
        logging.debug(self.title+' get_read_val returning '+tokenized_read_val[0])
        return tokenized_read_val[0]
        
    def rangelck(self):
        self.instr.write("RANGELCK ON")            
        
        
        
        
        
class K2400:
    def __init__(self, resource_manager, resource_name, title='Keithley 2400'):
        self.title = title
        logging.debug(self.title+' init started')
        self.rm = resource_manager
        self.rn = resource_name
        self.instr = self.rm.open_resource(self.rn)
        self.instr.timeout = 60*1000
        self.instr.clear()
        self.instr.write("*RST")
        logging.info("*IDN? -> "+self.instr.query("*IDN?"))
        self.instr.write(":SYST:BEEP:STAT OFF")
         
    def get_title(self):
        return self.title
        
    def set_output_on(self):
        self.instr.write(':OUTP ON')

    def set_output_off(self):
        self.instr.write(':OUTP OFF')
        
    def set_source_voltage(self, voltage):
        self.instr.write(':SOUR:VOLT %s' %voltage)
            
    def set_source_current(self, current):
        self.instr.write(':SOUR:CURR %s' %current)

    def set_sense_type(self, sense_type):
        self.instr.write(':SENS:FUNC '+sense_type)
        
    def set_source_type(self, source_type):
        self.instr.write(':SOUR:FUNC '+source_type)
        
    def set_source_current_range(self, source_range):
        self.instr.write(':SOUR:CURRent:RANGe '+str(source_range))

    def set_sense_voltage_range(self, rang):
        self.instr.write(':SENS:VOLT:RANG '+str(rang))

    def set_sense_current_range(self, rang):
        self.instr.write(':SENS:CURR:RANG '+str(rang))

    def set_voltage_compliance(self, compliance):
        self.instr.write(':SENS:VOLT:PROT '+str(compliance))

    def set_current_compliance(self, compliance):
        self.instr.write(':SENS:CURR:PROT '+str(compliance))
        
    def set_display_upper_text(self, text):
        self.instr.write(':DISPlay:WINDow1:TEXT:DATA "'+str(text)+'"')
        
    def enable_display_upper_text(self):
        self.instr.write(':DISPlay:WINDow1:TEXT:STATe 1')
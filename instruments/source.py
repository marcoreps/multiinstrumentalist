#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import vxi11
import time
import logging
import threading
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
            self.instr.timeout = 60*1000
            self.instr.clear()
            self.instr.write("J0X") # Factory init
            self.instr.write("F0,0X") # Source V DC
            self.instr.write("H0X") # Immediate trigger
            self.instr.write("G4,2,0X") # Output measure value with no prefix, no suffix
            self.instr.write("S3X") # 20ms integration time
            self.instr.write("V1X") # Enable 1000V range
            self.instr.write("B7.1,0,0X") # Bias 7.1V autorange
            self.instr.write("L1E-6,4X") # 1µA compliance 1µA range
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

    lock = threading.Lock()
    readable = True
    read_val = 0
    
    def measure(self):
        logging.debug(self.title+' measure started')
        self.connect()
        try:
            self.read_val = self.instr.ask("OUT?")
            self.instr.close()
        except:
            logging.error("Error in %s measure" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
    
    def is_readable(self):
        return self.readable

    def connect(self):
        logging.debug(self.title+' waiting for lock')
        self.lock.acquire()
        self.instr.open()

    def __init__(self, ip, gpib_address, lock, title='Fluke 5700A'):
        self.title = title
        self.lock = lock
        logging.debug(self.title+' init started')
        self.ip = ip
        self.gpib_address = gpib_address
        self.lock.acquire()
        try:
            self.instr =  vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
            self.instr.timeout = 60*1000
            self.instr.clear()
            self.instr.write("*RST")
            self.instr.write("STBY")
            self.instr.write("EXTGUARD OFF")
            logging.debug("*IDN? -> "+self.instr.ask("*IDN?"))
            self.instr.close()
        except:
            logging.error("Error in %s __init__" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
        
        
    def out(self,out_cmd):
        self.connect()
        try:
            self.instr.write("OUT "+out_cmd)
            self.instr.close()
        except:
            logging.error("Error in %s out" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
        
    def oper(self):
        self.connect()
        try:
            self.instr.write("OPER")
            self.instr.close()
        except:
            logging.error("Error in %s oper" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()

    def stby(self):
        self.connect()
        try:
            self.instr.write("STBY")
            self.instr.close()
        except:
            logging.error("Error in %s stby" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
        
    def get_title(self):
        return self.title
        
    def get_read_val(self):
        logging.debug(self.title+' get_read_val started')
        tokenized_read_val = re.split(',',self.read_val)
        return tokenized_read_val[0]
        

    def rangelck(self):
        self.connect()
        try:
            self.instr.write("RANGELCK ON")
            self.instr.close()
        except:
            logging.error("Error in %s rangelck" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
        
    def is_ready_to_read(self):
        logging.debug(self.title+' is ready to read')
        return True
        
        
    def is_measuring(self):
        return False
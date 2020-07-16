#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import vxi11
import time
import logging
import threading
import re



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
            logger.error("Error in %s measure" % self.title, exc_info=True)
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
            logger.error("Error in %s __init__" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
        
        
    def out(self,out_cmd):
        self.connect()
        try:
            self.instr.write("OUT "+out_cmd)
            self.instr.close()
        except:
            logger.error("Error in %s out" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
        
    def oper(self):
        self.connect()
        try:
            self.instr.write("OPER")
            self.instr.close()
        except:
            logger.error("Error in %s oper" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()

    def stby(self):
        self.connect()
        try:
            self.instr.write("STBY")
            self.instr.close()
        except:
            logger.error("Error in %s stby" % self.title, exc_info=True)
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
            logger.error("Error in %s rangelck" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
        
    def is_ready_to_read(self):
        logging.debug(self.title+' is ready to read')
        return True
        
        
    def is_measuring(self):
        return False
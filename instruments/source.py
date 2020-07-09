#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import vxi11
import time
import logging

class F5700A:

    def __init__(self, ip, gpib_address, title='Fluke 5700A'):
        self.title = title
        logging.debug(self.title+' init started')
        self.ip = ip
        self.gpib_address = gpib_address
        self.instr =  vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
        time.sleep(10)
        self.instr.timeout = 60*1000
        self.instr.clear()
        self.instr.write("*RST")
        self.instr.write("STBY")
        self.instr.write("EXTGUARD OFF")
        logging.debug("*IDN? -> "+self.instr.ask("*IDN?"))
        
    def out(self,out_cmd):
        self.instr.write("OUT "+out_cmd)
        
    def oper(self):
        self.instr.write("OPER")

    def stby(self):
        self.instr.write("STBY")
        
    def get_title(self):
        return self.title
        
    def get_read_val(self):
        return self.read_val

    def rangelck(self):
        self.instr.write("RANGELCK ON")

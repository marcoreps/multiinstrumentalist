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
        self.instr.timeout = 60*1000
        self.instr.clear()
        self.instr.write("*RST")
        self.instr.write("STBY")
        self.instr.write("EXTGUARD OFF")
        logging.debug("*IDN? -> "+self.instr.ask("*IDN?"))
        self.instr.close()
        
        
    def out(self,out_cmd):
        vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
        self.instr.write("OUT "+out_cmd)
        self.instr.close()
        
    def oper(self):
        vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
        self.instr.write("OPER")
        self.instr.close()

    def stby(self):
        vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
        self.instr.write("STBY")
        self.instr.close()
        
    def get_title(self):
        return self.title
        
    def get_read_val(self):
        return self.read_val

    def rangelck(self):
        vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
        self.instr.write("RANGELCK ON")
        self.instr.close()

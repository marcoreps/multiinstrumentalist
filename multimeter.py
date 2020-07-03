#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import vxi11
import time



class S7081:
    
    vxi_ip = "192.168.178.88"
    address = 2
    
    def __init__(self, address):   
        self.gpib_address = address
        self.instr =  vxi11.Instrument(self.vxi_ip, "gpib0,"+str(self.address))
        self.instr.timeout = 60*1000
        self.instr.write("INITIALISE")
        time.sleep(3)
        self.instr.write("BEEp")
        #self.instr.write("OUTPUT, GP-IB, ON: FORMAT = ENGINEERING,EXPANDED")
        #self.instr.write("MODe=VDC: RANge=Auto: NInes=6")
        #print(self.instr.ask("MEASURE, SINGLE"))

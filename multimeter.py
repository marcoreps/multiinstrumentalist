#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import vxi11
import time



class S7081:
    
    vxi_ip = "192.168.178.88"
    address = 0
    
    def __init__(self, address):   
        self.address = address
        self.instr =  vxi11.Instrument(self.vxi_ip, "gpib0,"+str(self.address))
        self.instr.timeout = 60*1000
        self.instr.clear()
        self.instr.write("INItialise")
        time.sleep(3)
        self.instr.write("BEEp")
        self.instr.write("DELIMITER=END")
        self.instr.write("OUTPUT,GP-IB=ON")
        self.instr.write("FORMAT=DVM,COMPRESSED")
        self.instr.write("DRIFT,OFF")
        self.instr.write("MODe=VDC: RANge=Auto: NInes=7")

    def read(self):
        self.instr.write("MEAsure, SIGLE")
        return self.instr.read()
            
        




class K2001:
    
    vxi_ip = "192.168.178.88"
    address = 0
    
    def __init__(self, address):   
        self.address = address
        self.instr =  vxi11.Instrument(self.vxi_ip, "gpib0,"+str(self.address))
        self.instr.clear()
        self.instr.write("*RST")
        self.instr.write(":SYST:AZER:TYPE SYNC")
        self.instr.write(":SYST:LSYN:STAT ON")
        self.instr.write(":SENS:FUNC 'VOLT:DC'")
        #self.instr.write(":SENS:VOLT:DC:DIG 8; NPLC 10; AVER:COUN 5; TCON REP")
        self.instr.write(":SENS:VOLT:DC:DIG 8; NPLC 10; TCON REP")
        self.instr.write(":SENS:VOLT:DC:AVER:STAT ON")
        self.instr.write(":SENS:VOLT:DC:RANG 20")
        self.instr.write(":FORM:ELEM READ")
        
    def read(self):
        return self.instr.ask("READ?")

        

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import vxi11
import time



class S7081:

    def __init__(self, vxi_ip, address):
        self.vxi_ip = vxi_ip
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
        self.instr.write("MODe=VDC: RANge=Auto: NInes=8")

    def read(self):
        self.instr.write("MEAsure, SIGLE")
        return self.instr.read()


class K2001:

    def __init__(self, vxi_ip, address):
        self.vxi_ip = vxi_ip
        self.address = address
        self.instr =  vxi11.Instrument(self.vxi_ip, "gpib0,"+str(self.address))
        self.instr.timeout = 60*1000
        self.instr.clear()
        
    def config_DCV_9digit(self):
        self.instr.write("*RST")
        self.instr.write(":SYST:AZER:TYPE SYNC")
        self.instr.write(":SYST:LSYN:STAT ON")
        self.instr.write(":SENS:FUNC 'VOLT:DC'")
        self.instr.write(":SENS:VOLT:DC:DIG 9; NPLC 10; TCON REP")
        self.instr.write(":SENS:VOLT:DC:AVER:STAT ON")
        self.instr.write(":SENS:VOLT:DC:RANG 20")
        self.instr.write(":FORM:ELEM READ")
        
    def config_DCV_9digit_1000(self): #Max filtering
        self.instr.write("*RST")
        self.instr.write(":SYST:AZER:TYPE SYNC")
        self.instr.write(":SYST:LSYN:STAT ON")
        self.instr.write(":SENS:FUNC 'VOLT:DC'")
        self.instr.write(":SENS:VOLT:DC:DIG 9; NPLC 10")
        self.instr.write(":SENS:VOLT:DC:AVER:STAT ON")
        self.instr.write(":SENS:VOLT:DC:AVER:COUN 100")
        self.instr.write(":SENS:VOLT:DC:AVER:TCON REP")
        self.instr.write(":SENS:VOLT:DC:AVER:STAT ON")
        self.instr.write(":SENS:VOLT:DC:FILT:LPAS:STAT ON")
        self.instr.write(":FORM:ELEM READ")

    def read(self):
        return self.instr.ask("READ?")


class A6581T:

    def __init__(self, vxi_ip, address):
        self.vxi_ip = vxi_ip
        self.address = address
        self.instr =  vxi11.Instrument(self.vxi_ip, "gpib0,"+str(self.address))
        self.instr.timeout = 60*1000
        self.instr.clear()
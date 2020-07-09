#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import vxi11
import time
import logging


class S7081:

    def __init__(self, ip, gpib_address, title='Solartron 7081'):
        self.title = title
        logging.debug(self.title+' init started')
        self.ip = ip
        self.gpib_address = gpib_address
        self.instr =  vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
        self.instr.timeout = 60*1000
        self.instr.clear()
        self.instr.write("INItialise")
        time.sleep(5)
        #self.instr.write("BEEp")
        self.instr.write("DELIMITER=END")
        self.instr.write("OUTPUT,GP-IB=ON")
        self.instr.write("FORMAT=ENGINEERING")
        #self.instr.write("DRIFT,OFF")
        self.instr.write("MODe=VDC: RANge=10: NInes=8")
        self.instr.close()

    def read(self):
        self.instr =  vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
        self.instr.write("MEAsure, SIGLE")
        self.instr.close()
        
    def get_title(self):
        return self.title
        
    def get_read_val(self):
        self.instr =  vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
        self.read_val = self.instr.read()
        self.instr.close()
        return self.read_val
        


class K2001:

    def __init__(self, ip, gpib_address, title='Keithley 200X'):
        self.title = title
        logging.debug(self.title+' init started')
        self.ip = ip
        self.gpib_address = gpib_address
        self.instr =  vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
        self.instr.clear()
        logging.debug("*IDN? -> "+self.instr.ask("*IDN?"))
        self.instr.close()
        
    def config_20DCV_9digit_fast(self):
        self.instr =  vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
        self.instr.write("*RST")
        self.instr.write(":SYST:AZER:TYPE SYNC")
        self.instr.write(":SYST:LSYN:STAT ON")
        self.instr.write(":SENS:FUNC 'VOLT:DC'")
        self.instr.write(":SENS:VOLT:DC:DIG 9; NPLC 10; TCON REP")
        self.instr.write(":SENS:VOLT:DC:AVER:STAT ON")
        self.instr.write(":SENS:VOLT:DC:RANG 20")
        self.instr.write(":FORM:ELEM READ")
        self.instr.close()
        
    def config_20DCV_9digit_filtered(self):
        self.instr =  vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
        self.instr.write("*RST")
        self.instr.write(":SYST:AZER:TYPE SYNC")
        self.instr.write(":SYST:LSYN:STAT ON")
        self.instr.write(":SENS:FUNC 'VOLT:DC'")
        self.instr.write(":SENS:VOLT:DC:DIG 9; NPLC 10")
        self.instr.write(":SENS:VOLT:DC:AVER:STAT ON")
        self.instr.write(":SENS:VOLT:DC:AVER:COUN 50")
        self.instr.write(":SENS:VOLT:DC:AVER:TCON REP")
        self.instr.write(":SENS:VOLT:DC:AVER:STAT ON")
        self.instr.write(":SENS:VOLT:DC:RANG 20")
        #self.instr.write(":SENS:VOLT:DC:FILT:LPAS:STAT ON")
        self.instr.write(":FORM:ELEM READ")
        self.instr.close()

    def read(self):
        self.instr =  vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
        self.read_val = self.instr.write("READ?")
        self.instr.close()
        
    def get_title(self):
        return self.title
        
    def get_read_val(self):
        self.instr =  vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
        self.read_val = self.instr.read()
        self.instr.close()
        return self.read_val
        
        
        
class K2002(K2001):
    pass
    

class R6581T:

    def __init__(self, ip, gpib_address, title='Advantest R6581T'):
        self.title = title
        logging.debug(self.title+' init started')
        self.ip = ip
        self.gpib_address = gpib_address
        self.instr =  vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
        self.instr.timeout = 60*1000
        self.instr.clear()
        logging.debug("*IDN? -> "+self.instr.ask("*IDN?"))
        self.int_temp = 0
        self.instr.close()
        
    def config_10DCV_9digit_fast(self):
        self.instr =  vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
        logging.debug(self.title+' config_10DCV_9digit_fast started')
        self.instr.write("*RST")
        self.instr.ask("*OPC?")
        self.instr.write("CONFigure:VOLTage:DC")
        self.instr.write(":SENSe:VOLTage:DC:RANGe:1.00E+01")
        #self.instr.write(":SENSe:VOLTage:DC:RANGe:AUTO ON")
        self.instr.write(":SENSe:VOLTage:DC:DIGits MAXimum")
        self.instr.write(":SENSe:VOLTage:DC:NPLCycles MAXimum")
        self.instr.write(":SENSe:VOLTage:DC:RANGe 10")
        
        #self.instr.write(":SENSe:VOLTage:DC:PROTection OFF")
        #self.instr.write(":SENSe:ZERO:AUTO OFF")
        self.instr.close()
        
    def config_10DCV_9digit_filtered(self):
        self.instr =  vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
        logging.debug(self.title+' config_10DCV_9digit_filtered started')
        self.instr.write("*RST")
        self.instr.ask("*OPC?")
        self.instr.write("CONFigure:VOLTage:DC")
        self.instr.write(":SENSe:VOLTage:DC:RANGe:1.00E+01")
        self.instr.write(":SENSe:VOLTage:DC:DIGits MAXimum")
        self.instr.write(":SENSe:VOLTage:DC:NPLCycles MAXimum")
        self.instr.write(":SENSe:VOLTage:DC:RANGe 10")
        
        #self.instr.write(":SENSe:VOLTage:DC:PROTection OFF")
        #self.instr.write(":SENSe:ZERO:AUTO OFF")
        
        self.instr.write(":CALCulate:DFILter:STATe ON")
        self.instr.write(":CALCulate:DFILter AVERage")
        self.instr.write(":CALCulate:DFILter:AVERage 15")
        self.instr.close()
        
    def read(self):
        self.instr =  vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
        self.instr.write("READ?")
        self.instr.close()
        
    def get_title(self):
        return self.title
        
    def get_read_val(self):
        self.instr =  vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
        self.read_val = self.instr.read()
        self.instr.close()
        return self.read_val
        
    def get_int_temp(self):
        self.instr =  vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
        self.int_temp = self.instr.ask(":SENSe:ITEMperature?")
        self.instr.close()
        return self.int_temp

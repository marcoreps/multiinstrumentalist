#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyvisa
import time
import logging
import serial
import numpy as np
import math
import signal


class multimeter:
        
    def get_title(self):
        return self.title
        
    def get_read_val(self):
        logging.debug("get_read_val() connected, reading ... ")
        read_val = self.instr.read()
        logging.debug("get_read_val() reading "+str(read_val))
        return read_val
        
    def read_stb(self):
        logging.debug("read_stb() reading status")
        self.stb = self.instr.read_stb()
        
    def blank_display(self):
        logging.debug("blank_display not implemented for this instrument")

class HP3458A(multimeter):

    def __init__(self, resource_manager, resource_name, title='3458A'):
        self.title = title
        logging.debug(self.title+' init started')
        self.rm = resource_manager
        self.rn = resource_name
        self.instr =  self.rm.open_resource(self.rn)
        self.instr.timeout = 2000000
        self.instr.clear()
        self.instr.write("RESET")
        self.instr.write("END ALWAYS")
        self.instr.write("OFORMAT ASCII")
        self.instr.write("BEEP")
        logging.info("ID? -> "+self.instr.query("ID?"))
        
    def config_NPLC(self, NPLC):
        logging.debug(self.title+" config_NPLC")
        self.instr.write("NPLC "+str(NPLC))
        
    def config_NDIG(self, NDIG):
        logging.debug(self.title+" config_NDIG")
        self.instr.write("NDIG "+str(NDIG))
        
    def config_DCV(self, RANG):
        logging.debug(self.title+" config_DCV")
        self.instr.write("DCV "+str(RANG))
        
    def blank_display(self):
        logging.debug(self.title+" blank_display")
        self.instr.write("ARANGE ON")
        self.instr.write("DISP MSG,\"                 \"")
        #self.instr.visalib.sessions[self.instr.session].interface.ibloc()
        
    def config_trigger_auto(self):
        logging.debug(self.title+" config_trigger_auto")
        self.instr.write("TARM AUTO")
        
    def config_trigger_hold(self):
        logging.debug(self.title+" config_trigger_hold")
        self.instr.write("TARM HOLD")
        
    def trigger_once(self):
        logging.debug(self.title+' triggered once')
        self.instr.write("TARM SGL")
        
    def acal_DCV(self):
        logging.debug(self.title+' ACAL DCV started')
        timout_memory = self.instr.timeout
        self.instr.timeout = 2
        try:
            self.instr.write("ACAL DCV")
        except Exception:
            pass
        self.instr.timeout = timout_memory        
        
        
    def acal_ALL(self):
        logging.debug(self.title+' ACAL ALL started')
        timout_memory = self.instr.timeout
        self.instr.timeout = 2000
        try:
            self.instr.write("ACAL")
        except Exception:
            pass
        self.instr.timeout = timout_memory     
        
    def is_readable(self):
        logging.debug(self.title+' is_readable() started')
        self.read_stb()
        logging.debug(self.title+' stb is '+str(self.stb))
        readable = self.stb & 0b10000000
        return readable
        
    def is_ready(self):
        self.read_stb()
        ready = self.stb & 0b00010000
        return ready
            
    def get_int_temp(self):
        temp = self.instr.query("TEMP?")
        return temp
        
    def get_cal_param(self, number):
        logging.debug(self.title+' get_cal_param() called')
        param = self.instr.query("CAL? "+str(number))
        return param
        
    def config_pt100(self):
        logging.debug(self.title+' config_pt100 called')
        self.instr.write("OHMF 100")
        self.instr.write("MATH CRTD85")
        
        



class W4950(multimeter):

    def __init__(self, resource_manager, resource_name, title='Wavetek 4950'):
        self.title = title
        logging.debug(self.title+' init started')
        self.rm = resource_manager
        self.rn = resource_name
        self.instr =  self.rm.open_resource(self.rn)
        self.instr.timeout = 20000
        self.instr.clear()
        self.instr.write("*RST")
        time.sleep(2)
        self.instr.write("TRIG_SRCE EXT")
        self.instr.write("ACCURACY HIGH")
        self.instr.write("CORRECTN CERTIFIED")
        self.instr.write("BAND OFF")
        self.instr.write("LCL_GUARD")
        #self.instr.write("LEAD_NO '0123456789'")
        logging.info("*IDN? -> "+self.instr.query("*IDN?"))
        logging.info("*OPT? -> "+self.instr.query("*OPT?"))
        logging.info("DATE? CERTIFIED -> "+self.instr.query("DATE? CERTIFIED"))
        logging.info("DATE? BASE -> "+self.instr.query("DATE? BASE"))
        
    def trigger_once(self):
        logging.debug(self.title+' triggered once')
        self.instr.write("*TRG;GET;RDG?")
        
        
    def config_trigger_auto(self):
        logging.debug(self.title+" config_trigger_auto")
        self.instr.write("TRIG_SRCE INT")
        
    def config_trigger_hold(self):
        logging.debug(self.title+" config_trigger_hold")
        self.instr.write("TRIG_SRCE EXT")
        
    def config_accuracy(self, acc):
        logging.debug(self.title+" ACCURACY")
        if acc == "HIGH":
            self.instr.write("ACCURACY HIGH")
        else:
            self.instr.write("ACCURACY LOW")
        
    def config_DCV(self, RANG):
        logging.debug(self.title+" config_DCV")
        self.instr.write("DCV "+str(RANG)+",PCENT_100")
        
    def is_readable(self):
        logging.debug(self.title+' is_readable() started')
        mese = int(self.instr.query("MESR?"))
        logging.debug(self.title+' MESR is '+str(mese))
        readable = mese & 0b10000000
        if (readable):
            logging.debug(self.title+' is readable')
        return readable
        
    def get_read_val(self):
        logging.debug("get_read_val() connected, reading ... ")
        read_val = self.instr.query("GET;RDG?")
        logging.debug("get_read_val() reading "+str(read_val))
        return read_val
            
class HP34420A(multimeter):

    def __init__(self, resource_manager, resource_name, title='34420A'):
        self.title = title
        logging.debug(self.title+' init started')
        self.rm = resource_manager
        self.rn = resource_name
        self.instr = self.rm.open_resource(self.rn)
        del self.instr.timeout
        logging.info("*IDN? -> "+self.instr.query("*IDN?"))
        logging.info("Last ERR -> "+self.instr.query('SYSTem:ERRor?'))
        self.instr.clear()
        self.instr.write("*RST")
        self.instr.write("*CLS")
        logging.info("SYSTem:VERSion? -> "+self.instr.query("SYSTem:VERSion?"))

        
    def config_DCV(self, RANG):
        logging.debug(self.title+" config_DCV")
        self.instr.write("CONFigure:VOLTage:DC "+str(RANG)+", MAX, (@FRONt1)")
        self.instr.write("ROUTe:TERMinals FRONt1")
        self.instr.write("SENSe:VOLTage:DC:NPLCycles 100")
        self.instr.write("TRIGger:DELay:AUTO ON")
        
    def blank_display(self):
        logging.debug(self.title+" blank_display")
        self.instr.write("DISPlay OFF")
        
    def get_read_val(self):
        logging.debug("get_read_val() connected, reading ... ")
        #read_val = self.instr.query("FETCH?") #for bus triggering
        read_val = self.instr.query("READ?") #for auto triggering
        logging.debug("get_read_val() reading "+str(read_val))
        return read_val
        
    def rel(self):
        logging.debug(self.title+' rel() started')
        self.instr.write("SENSe:VOLTage:DC:NULL:STATe OFF")
        average = 0
        for i in range(10):
            average += float(self.get_read_val())/10
        self.instr.write("SENSe:VOLTage:DC:NULL:STATe ON")
        self.instr.write("SENSe:VOLTage:DC:NULL:VALue "+str(average))        
        
    def rel_off(self):
        self.instr.write("SENSe:NULL OFF")
        
    def get_points(self):
        return self.instr.query("DATA:POINts?")
        
    def get_error(self):
        return self.instr.query("SYSTem:ERRor?")
        
    def config_trigger_hold(self):
        self.instr.write("TRIGger:SOURce BUS")
        #self.instr.write("TRIGger:COUNt INFinity") Insufficient memory??
        
    def trigger_once(self):
        logging.debug(self.title+' triggered once')
        self.instr.write("INITiate")
        self.instr.write("*TRG")
        
    def set_filter(self):
        self.instr.write("INPut:FILTer:STATe ON")
        self.instr.write("INPut:FILTer:TYPE DIGital")
        self.instr.write("INPut:FILTer:DIGital:RESPonse MEDium")
        
class F8508A(multimeter):

    def __init__(self, resource_manager, resource_name, title='Fluke 8508A'):
        self.title = title
        logging.debug(self.title+' init started')
        self.rm = resource_manager
        self.rn = resource_name
        self.instr =  self.rm.open_resource(self.rn)
        self.instr.timeout = 50000
        self.instr.clear()
        self.instr.write('*RST')
        self.instr.write('*CLS')
        time.sleep(2)
        logging.info("*IDN? -> "+self.instr.query("*IDN?"))
        
    def trigger_once(self):
        logging.debug(self.title+' triggered once')
        self.instr.write("*TRG;GET;RDG?")
        
        
    def config_trigger_auto(self):
        logging.debug(self.title+" config_trigger_auto")
        self.instr.write("TRIG_SRCE INT")
        
    def config_trigger_hold(self):
        logging.debug(self.title+" config_trigger_hold")
        self.instr.write("TRG_SRCE EXT")
        
    def config_DCV(self, RANG):
        logging.debug(self.title+" config_DCV")
        self.instr.write("DCV "+str(RANG)+",FILT_OFF,RESL8,FAST_OFF")
        
        
    def is_readable(self):
        logging.debug(self.title+' is_readable() started')
        mese = int(self.instr.query("MESR?"))
        logging.debug(self.title+' MESR is '+str(mese))
        readable = mese & 0b10000000
        if (readable):
            logging.debug(self.title+' is readable')
        return readable
        
    def get_read_val(self):
        logging.debug("get_read_val() connected, reading ... ")
        self.instr.write("*TRG;RDG?")
        read_val = self.instr.read()
        logging.debug("get_read_val() reading "+str(read_val))
        return read_val
        
    def config_pt100(self):
        logging.debug(self.title+" config_pt100")
        self.instr.write("PRT \"Default probe    \"")
        
        
class K2182A(multimeter):

    def __init__(self, resource_manager, resource_name, title='Keithley 2182A'):
        self.title = title
        logging.debug(self.title+' init started')
        self.rm = resource_manager
        self.rn = resource_name
        self.instr =  self.rm.open_resource(self.rn)
        self.instr.timeout = 30000
        self.instr.clear()
        self.instr.write('*RST')
        self.instr.write('*CLS')
        time.sleep(2)
        logging.info("*IDN? -> "+self.instr.query("*IDN?"))
        self.instr.write(":syst:pres")
        
        
    def config_DCV(self):
        logging.debug(self.title+" config_DCV")
        self.instr.write(":SENSe:VOLTage:CHANnel1:RANGe 0")        
        self.instr.write(":SENSe:VOLTage:CHANnel1:LPASs ON")
        self.instr.write(":SENSe:VOLTage:CHANnel1:DFILter:STATe ON")
        self.instr.write(":SENSe:VOLTage:CHANnel1:DFILter:COUNt 100")
        self.instr.write(":SYSTem:AZERo:STATe ON")
        self.instr.write(":SYSTem:FAZero:STATe ON")
        self.instr.write(":SYSTem:LSYNc:STATe ON")

        self.instr.write(":SENSe:VOLTage:CHANnel1:NPLCycles 1")
        


        
        
        
    def get_read_val(self):
        logging.debug("get_read_val() connected, reading ... ")
        read_val = self.instr.query(":FETCh?")
        logging.debug("get_read_val() reading "+str(read_val))
        return read_val
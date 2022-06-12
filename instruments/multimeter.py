#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import vxi11
import time
import logging
import serial
import numpy as np
import math


class multimeter:


    instr = 0
    read_val = 0
    title = ""

    readable = False
    
    def is_readable(self):
        return self.readable
    
    
    def connect(self):
        self.lock.acquire()
        logging.debug("connecting instr")
        time.sleep(0.1)
        self.instr.open()
        time.sleep(0.1)
        
        
    def get_title(self):
        return self.title
        
        
    def get_read_val(self):
        try:
            self.connect()
            self.read_val = self.instr.read()
            self.close_instr_conn()
        except:
            logging.error("Error in %s get_read_val" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
        logging.debug("%s reading %s" % (self.title, self.read_val))
        return self.read_val
        
    def close_instr_conn(self):
        try:
            logging.debug("Closing instr")
            self.instr.close()
        except:
            logging.error("Error in %s close_instr_conn" % self.title, exc_info=True)
            pass
        
        
    def read_stb(self):
        try:
            self.connect()
            self.stb = self.instr.read_stb()
            logging.debug("stb read")
            self.close_instr_conn()
        except:
            logging.error("Error in %s read_stb" % self.title, exc_info=True)
            pass
        finally:
            logging.debug("lock release")
            self.lock.release()
            

class S7081(multimeter):

    def __init__(self, ip, gpib_address, lock, title='Solartron 7081'):
        self.title = title
        self.lock = lock
        logging.debug(self.title+' init started')
        self.ip = ip
        self.gpib_address = gpib_address
        self.lock.acquire()
        try:
            self.instr =  vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
            self.instr.clear()
            self.instr.write("INItialise")
            time.sleep(5)
            self.instr.write("BEEp")
            self.instr.write("DELIMITER=END")
            self.instr.write("OUTPUT,GP-IB=ON")
            self.instr.write("FORMAT=ENGINEERING")
            self.close_instr_conn()
        except:
            logging.error("Error in %s __init__" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
    def config_10DCV_9digit(self):
        try:
            self.connect()
            self.instr.write("DRIFT,OFF")
            self.instr.write("MODe=VDC: RANge=10: NInes=8")
            self.close_instr_conn()
        except:
            logging.error("Error in %s __init__" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
    def config_10k_9digit(self):
        try:
            self.connect()
            #self.instr.write("DRIFT,ON")
            self.instr.write("DRIFT,OFF")
            self.instr.write("MODe=KOHM: RANge=10: NInes=8")
            self.close_instr_conn()
        except:
            logging.error("Error in %s __init__" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
        

    def measure(self):
        logging.debug(self.title+' measure started')
        try:
            self.connect()
            self.instr.write("MEAsure, SIGLE")
            self.close_instr_conn()
        except:
            logging.error("Error in %s measure" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
        
    def is_readable(self):
        self.read_stb()
        ready = self.stb == 24
        return ready
        
        
        
        
        


class K2001(multimeter):

    def __init__(self, ip, gpib_address, lock, title='Keithley 200X'):
        self.read_val = 0
        self.title = title
        self.lock = lock
        logging.debug(self.title+' init started')
        self.ip = ip
        self.gpib_address = gpib_address
        self.lock.acquire()
        try:
            self.instr =  vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
            self.instr.clear()
            logging.debug("*IDN? -> "+self.instr.ask("*IDN?"))
            self.close_instr_conn()
        except:
            logging.error("Error in %s __init__" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
        
        
    def config_20DCV_9digit_fast(self):
        try:
            self.connect()
            self.instr.write("*RST")
            self.instr.write(":SYST:AZER:TYPE SYNC")
            self.instr.write(":SYST:LSYN:STAT ON")
            self.instr.write(":SENS:FUNC 'VOLT:DC'")
            self.instr.write(":SENS:VOLT:DC:DIG 9; NPLC 10")
            self.instr.write(":SENS:VOLT:DC:AVER:STAT ON")
            self.instr.write(":SENS:VOLT:DC:RANG 20")
            self.instr.write(":FORM:ELEM READ")
            self.close_instr_conn()
        except:
            logging.error("Error in %s config_20DCV_9digit_fast" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
        
        
    def config_20DCV_9digit_filtered(self):
        try:
            self.connect()
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
            self.close_instr_conn()
        except:
            logging.error("Error in %s config_20DCV_9digit_filtered" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
    def config_2ADC_9digit_filtered(self):
        try:
            self.connect()
            self.instr.write("*RST")
            self.instr.write(":SYST:AZER:TYPE SYNC")
            self.instr.write(":SYST:LSYN:STAT ON")
            self.instr.write(":SENS:FUNC 'CURRent:DC'")
            self.instr.write(":SENSe:CURRent:DC:RANGe 2")
            self.instr.write(":SENS:CURRent:DC:DIG 9; NPLC 10")
            self.instr.write(":SENS:CURRent:DC:AVER:STAT ON")
            self.instr.write(":SENS:CURRent:DC:AVER:COUN 50")
            self.instr.write(":SENS:CURRent:DC:AVER:TCON REP")
            self.instr.write(":SENS:CURRent:DC:AVER:STAT ON")
            #self.instr.write(":SENS:CURRent:DC:FILT:LPAS:STAT ON")
            self.instr.write(":FORM:ELEM READ")
            self.close_instr_conn()
        except:
            logging.error("Error in %s config_2ADC_9digit_filtered" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()


    def measure(self):
        logging.debug(self.title+' measure started')
        try:
            self.connect()
            self.read_val = self.instr.write("READ?")
            self.close_instr_conn()
        except:
            logging.error("Error in %s measure" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
        
        
    def is_readable(self):
        self.read_stb()
        ready = self.stb & 0b00010000
        return ready
        
        
        
class K2002(K2001):
    pass
    
    

class R6581T(multimeter):

    def __init__(self, ip, gpib_address, lock, title='Advantest R6581T'):
        self.read_val = 0
        self.title = title
        self.lock = lock
        logging.debug(self.title+' init started')
        self.ip = ip
        self.int_temp = 0
        self.gpib_address = gpib_address
        self.lock.acquire()
        try:
            self.instr =  vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
            self.instr.clear()
            logging.debug("*IDN? -> "+self.instr.ask("*IDN?"))
            self.int_temp = 0
            self.close_instr_conn()
        except:
            logging.error("Error in %s __init__" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
        
        
    def config_10DCV_9digit_fast(self):
        try:
            self.connect()
            logging.debug(self.title+' config_10DCV_9digit_fast started')
            self.instr.write("*RST")
            #self.instr.ask("*OPC?")
            self.instr.write("CONFigure:VOLTage:DC")
            self.instr.write(":SENSe:VOLTage:DC:RANGe:1.00E+01")
            #self.instr.write(":SENSe:VOLTage:DC:RANGe:AUTO ON")
            self.instr.write(":SENSe:VOLTage:DC:DIGits MAXimum")
            self.instr.write(":SENSe:VOLTage:DC:NPLCycles 10")
            self.instr.write(":SENSe:VOLTage:DC:RANGe 10")
            
            #self.instr.write(":SENSe:VOLTage:DC:PROTection OFF")
            #self.instr.write(":SENSe:ZERO:AUTO OFF")
            self.close_instr_conn()
        except:
            logging.error("Error in %s config_10DCV_9digit_fast" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
        
        
    def config_10DCV_9digit_filtered(self):
        try:
            self.connect()
            logging.debug(self.title+' config_10DCV_9digit_filtered started')
            self.instr.write("*RST")
            #self.instr.ask("*OPC?")
            self.instr.write("CONFigure:VOLTage:DC")
            self.instr.write(":SENSe:VOLTage:DC:RANGe 10")
            self.instr.write(":SENSe:VOLTage:DC:DIGits MAXimum")
            self.instr.write(":SENSe:VOLTage:DC:NPLCycles 10")
            
            #self.instr.write(":SENSe:VOLTage:DC:PROTection OFF")
            #self.instr.write(":SENSe:ZERO:AUTO OFF")
            
            self.instr.write(":CALCulate:DFILter:STATe ON")
            self.instr.write(":CALCulate:DFILter AVERage")
            self.instr.write(":CALCulate:DFILter:AVERage 10")
            self.close_instr_conn()
        except:
            logging.error("Error in %s config_10DCV_9digit_filtered" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
            
    def config_100k4W_9digit_filtered(self):
        try:
            self.connect()
            logging.debug(self.title+' config_100k4W_9digit_filtered started')
            self.instr.write("*RST")
            #self.instr.ask("*OPC?")
            self.instr.write("CONFigure:FRESistance")
            self.instr.write(":SENSe:FRESistance:RANGe 1.00E+05")
            self.instr.write(":SENSe:FRESistance:DIGits MAXimum")
            self.instr.write(":SENSe:FRESistance:NPLCycles 10")
            self.instr.write(":SENSe:FRESistance:SOURce OCOMpensated")
            self.instr.write(":SENSe:FRESistance:POWer HI")
            
            #self.instr.write(":SENSe:VOLTage:DC:PROTection OFF")
            #self.instr.write(":SENSe:ZERO:AUTO OFF")
            
            self.instr.write(":CALCulate:DFILter:STATe ON")
            self.instr.write(":CALCulate:DFILter AVERage")
            self.instr.write(":CALCulate:DFILter:AVERage 10")
            self.close_instr_conn()
        except:
            logging.error("Error in %s config_10DCV_9digit_filtered" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
            
    def config_10k4W_9digit_filtered(self):
        try:
            self.connect()
            logging.debug(self.title+' config_10k4W_9digit_filtered started')
            self.instr.write("*RST")
            #self.instr.ask("*OPC?")
            self.instr.write("CONFigure:FRESistance")
            self.instr.write(":SENSe:FRESistance:RANGe 1.00E+04")
            self.instr.write(":SENSe:FRESistance:DIGits MAXimum")
            self.instr.write(":SENSe:FRESistance:NPLCycles 10")
            #self.instr.write(":SENSe:FRESistance:SOURce OCOMpensated")
            self.instr.write(":SENSe:FRESistance:POWer HI")
            
            #self.instr.write(":SENSe:VOLTage:DC:PROTection OFF")
            #self.instr.write(":SENSe:ZERO:AUTO OFF")
            
            self.instr.write(":CALCulate:DFILter:STATe ON")
            self.instr.write(":CALCulate:DFILter AVERage")
            self.instr.write(":CALCulate:DFILter:AVERage 10")
            self.close_instr_conn()
        except:
            logging.error("Error in %s config_10DCV_9digit_filtered" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
        
        
    def config_10R4W_9digit_filtered(self):
        try:
            self.connect()
            logging.debug(self.title+' config_10R4W_9digit_filtered started')
            self.instr.write("*RST")
            #self.instr.ask("*OPC?")
            self.instr.write("CONFigure:FRESistance")
            self.instr.write(":SENSe:FRESistance:RANGe 1.00E+01")
            self.instr.write(":SENSe:FRESistance:DIGits MAXimum")
            self.instr.write(":SENSe:FRESistance:NPLCycles 10")
            self.instr.write(":SENSe:FRESistance:SOURce OCOMpensated")
            self.instr.write(":SENSe:FRESistance:POWer HI")
            
            #self.instr.write(":SENSe:VOLTage:DC:PROTection OFF")
            #self.instr.write(":SENSe:ZERO:AUTO OFF")
            
            self.instr.write(":CALCulate:DFILter:STATe ON")
            self.instr.write(":CALCulate:DFILter AVERage")
            self.instr.write(":CALCulate:DFILter:AVERage 10")
            self.close_instr_conn()
        except:
            logging.error("Error in %s config_10DCV_9digit_filtered" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
        
    def measure(self):
        logging.debug(self.title+' measure started')
        try:
            self.connect()
            self.int_temp = self.instr.ask(":SENSe:ITEMperature?")
            self.instr.write("READ?")
            self.close_instr_conn()
        except:
            logging.error("Error in %s measure" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
        
        
    def get_int_temp(self):
        return self.int_temp
        
        
    def is_readable(self):
        self.read_stb()
        ready = self.stb == 16
        return ready
     

class HP34401A(multimeter):

    def __init__(self, ip, gpib_address, lock, title='HP 34401A'):
        self.read_val = 0
        self.title = title
        self.lock = lock
        logging.debug(self.title+' init started')
        self.ip = ip
        self.gpib_address = gpib_address
        self.lock.acquire()
        try:
            self.instr =  vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
            self.instr.clear()
            logging.debug("*IDN? -> "+self.instr.ask("*IDN?"))
            self.close_instr_conn()
        except:
            logging.error("Error in %s __init__" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
        
        
    def config_10DCV_6digit_fast(self):
        try:
            self.connect()
            self.instr.write("*RST")
            self.instr.write("SYSTem:BEEPer")
            self.instr.write("CONFigure:VOLTage:DC 10, MIN")
            self.close_instr_conn()
        except:
            logging.error("Error in %s config_20DCV_9digit_fast" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()


    def measure(self):
        logging.debug(self.title+' measure started')
        try:
            self.connect()
            self.read_val = self.instr.write("READ?")
            self.close_instr_conn()
        except:
            logging.error("Error in %s measure" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
    def is_readable(self):
        self.read_stb()
        ready = self.stb & 0b00010000
        return ready
        
        
class HP3458A(multimeter):

    def __init__(self, ip, gpib_address, lock, title='HP 3458A'):
        self.read_val = 0
        self.title = title
        self.lock = lock
        logging.debug(self.title+' init started')
        self.ip = ip
        self.gpib_address = gpib_address
        self.int_temp = 0
        self.lock.acquire()
        try:
            self.instr =  vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
            self.instr.timeout = 60
            self.instr.clear()
            self.instr.write("END ALWAYS")
            self.instr.write("OFORMAT ASCII")
            self.instr.write("BEEP")
            logging.debug("ID? -> "+self.instr.ask("ID?"))
            self.close_instr_conn()
        except:
            logging.error("Error in %s __init__" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
        
            
    def config_NPLC(self, NPLC):
        try:
            self.connect()
            logging.debug(self.title+" config_NPLC")
            self.instr.write("NPLC "+str(NPLC))
            self.close_instr_conn()
        except:
            logging.error("Error in %s config_NPLC" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
    def config_NDIG(self, NDIG):
        try:
            self.connect()
            logging.debug(self.title+" config_NDIG")
            self.instr.write("NDIG "+str(NDIG))
            self.close_instr_conn()
        except:
            logging.error("Error in %s config_NDIG" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
    def config_DCV(self, RANG):
        try:
            self.connect()
            logging.debug(self.title+" config_DCV")
            self.instr.write("DCV "+str(RANG))
            self.close_instr_conn()
        except:
            logging.error("Error in %s config_DCV" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
    def blank_display(self):
        try:
            self.connect()
            logging.debug(self.title+" blank_display")
            self.instr.write("DISP MSG,\"                 \"")
            self.instr.write("DISP ON")
            self.close_instr_conn()
        except:
            logging.error("Error in %s blank_display" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
        
    def config_trigger_auto(self):
        try:
            self.connect()
            logging.debug(self.title+" config_trigger_auto")
            self.instr.write("TARM AUTO")
            self.close_instr_conn()
        except:
            logging.error("Error in %s config_trigger_auto" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
    def config_trigger_hold(self):
        try:
            self.connect()
            logging.debug(self.title+" config_trigger_hold")
            self.instr.write("TARM HOLD")
            self.close_instr_conn()
        except:
            logging.error("Error in %s config_trigger_hold" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
    def trigger_once(self):
        try:
            logging.debug(self.title+' triggered once')
            if self.is_ready():
                self.connect()
                self.instr.write("TARM SGL")
                self.close_instr_conn()
            else:
                logging.info("%s was not ready for trigger_once." % (self.get_title()))
        except:
            logging.error("Error in %s trigger_once" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
    def measure(self):
        logging.debug(self.title+' measure started')
        try:
            self.connect()
            self.instr.write("TARM SGL,1")
            self.close_instr_conn()
        except:
            logging.error("Error in %s measure" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
    def acal_DCV(self):
        logging.debug(self.title+' ACAL DCV started')
        try:
            self.connect()
            self.instr.write("ACAL DCV")
            self.close_instr_conn()
        except:
            logging.error("Error in %s acal_DCV" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()

            
    def is_readable(self):
        self.read_stb()
        ready = self.stb & 0b10000000
        return ready
        
    def is_ready(self):
        self.read_stb()
        ready = self.stb & 0b00010000
        return ready
            
            
    def get_int_temp(self):
        temp = 0
        try:
            self.connect()
            temp = self.instr.ask("TEMP?")
            self.close_instr_conn()
        except:
            logging.error("Error in %s get_int_temp" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            return temp
        
    def get_cal_72(self):
        cal72 = 0
        try:
            self.connect()
            cal72 = self.instr.ask("CAL? 72")
            self.close_instr_conn()
        except:
            logging.error("Error in %s get_cal_72" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            return cal72
        
    def get_cal_73(self):
        cal73 = 0
        try:
            self.connect()
            cal73 = self.instr.ask("CAL? 73")
            self.close_instr_conn()
        except:
            logging.error("Error in %s get_cal_73" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            return cal73
            
    def get_cal_175(self):
        cal175 = 0
        try:
            self.connect()
            cal175 = self.instr.ask("CAL? 175")
            self.close_instr_conn()
        except:
            logging.error("Error in %s get_cal_175" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            return cal175
            
    def get_cal_59(self):
        cal59 = 0
        try:
            self.connect()
            cal59 = self.instr.ask("CAL? 59")
            self.close_instr_conn()
        except:
            logging.error("Error in %s get_cal_59" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            return cal59
            
    def get_cal_2_1(self):
        cal_2_1 = 0
        try:
            self.connect()
            cal_2_1 = self.instr.ask("CAL? 2,1")
            self.close_instr_conn()
        except:
            logging.error("Error in %s get_cal_2_1" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            return cal_2_1

    def get_cal_1_1(self):
        cal_1_1 = 0
        try:
            self.connect()
            cal_1_1 = self.instr.ask("CAL? 1,1")
            self.close_instr_conn()
        except:
            logging.error("Error in %s get_cal_1_1" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            return cal_1_1
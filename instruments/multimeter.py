#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import vxi11
import time
import logging
import serial
import statistics
from multiprocessing import Process, Queue
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
        logging.debug("connecting")
        self.lock.acquire()
        logging.debug("lock acquired")
        
        self.instr.open()
        time.sleep(0.1)
        logging.debug("instr opened")
        
        
    def get_title(self):
        return self.title
        
        
    def get_read_val(self):
        try:
            self.connect()
            self.read_val = self.instr.read()
            self.instr.close()
        except:
            logging.error("Error in %s get_read_val" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
        logging.debug("%s reading %s" % (self.title, self.read_val))
        return self.read_val
        
        
    def read_stb(self):
        try:
            self.connect()
            self.stb = self.instr.read_stb()
            logging.debug("stb read")
            self.instr.close()
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
            self.instr.close()
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
            self.instr.close()
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
            self.instr.close()
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
            self.instr.close()
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
            self.instr.close()
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
            self.instr.close()
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
            self.instr.close()
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
            self.instr.close()
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
            self.instr.close()
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
            self.instr.close()
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
            self.instr.close()
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
            self.instr.close()
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
            self.instr.close()
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
            self.instr.close()
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
            self.instr.close()
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
            self.instr.close()
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




class HPM7177(multimeter):

    def __init__(self, seriallock, polyterms, dev='/dev/ttyUSB0', baud=921600, nfilter=10000, title='HPM7177'):
        self.title = title
        logging.debug(self.title+' init started')
        self.seriallock = seriallock
        self.polyfunc = np.poly1d(polyterms)
        self.dev = dev
        self.baud = baud
        self.nfilter = nfilter
        self.serial_q = Queue(maxsize=2)
        self.output_q = Queue(maxsize=1)
        
        self.serial_process = Process(target=self.readserial, args=(self.serial_q,))
        self.serial_process.daemon = True
        self.serial_process.start()
        
        self.convert_process = Process(target=self.convert, args=(self.serial_q,self.output_q,))
        self.convert_process.daemon = True
        self.convert_process.start()
        
        
    def readserial(self, q,):
        s = serial.Serial(self.dev, self.baud)
        while True:
            if not q.full():
                #self.seriallock.acquire()
                q.put(s.read(100000))
                #self.seriallock.release()
            else:
                time.sleep(0.2)
        
        
    def convert(self,serial_q,output_q):
        readings = []
        while True:
            if not output_q.full() and not serial_q.empty():
                chunk=serial_q.get()
                i=chunk.find(b'\xa0\r')
                while (len(readings)<self.nfilter):
                    i=i+chunk[i:].find(b'\xa0\r')
                    j=i+1+chunk[i+1:].find(b'\xa0\r')
                    if(j-i == 6):
                        number = int.from_bytes(chunk[i+2:j], byteorder='big', signed=False)
                        readings.append(number)
                    else:
                        logging.debug(self.title+' wrong length line')
                    i=j
                    if len(chunk[i:])<10:
                        chunk=serial_q.get()
                        i=0

                mean=statistics.mean(readings)
                output_q.put(mean)
                readings.clear()
            else:
                time.sleep(0.2)
        
        
    def is_readable(self):
        return self.output_q.full()


    def get_read_val(self):
        return self.polyfunc(self.output_q.get())
        return self.output_q.get()
        #x1=self.output_q.get()
        #HMP1_fit1=6.763004812273380e-09*x1-1.452321344215639e+01
        #HMP1_fit2=1.02782955913447e-6+3.04254972897816e-6*math.sin(0.00322438501023585*x1)-2.54617098552864e-6*math.cos(2.41476535668804+0.00322438496390789*x1+1.47267948257617*math.sin(0.0211347361227292+0.00322438501023585*x1))
        #return HMP1_fit1+HMP1_fit2

        
    def measure(self):
        self.serial_q.get()
        self.output_q.get()
        

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
            self.instr.close()
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
            self.instr.close()
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
            self.instr.close()
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
            self.instr.close()
        except:
            logging.error("Error in %s __init__" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
        
        
    def config_10DCV_9digit(self):
        try:
            self.connect()
            self.instr.write("PRESET NORM")
            self.instr.write("DCV 10")
            self.instr.write("TARM HOLD")
            self.instr.write("TRIG AUTO")
            self.instr.write("NRDGS 1,AUTO")
            self.instr.write("MEM OFF")
            self.instr.write("NDIG 9")
            self.instr.close()
        except:
            logging.error("Error in %s config_10DCV_9digit" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
    def config_100DCV_9digit(self):
        try:
            self.connect()
            self.instr.write("PRESET NORM")
            self.instr.write("DCV 100")
            self.instr.write("TARM HOLD")
            self.instr.write("TRIG AUTO")
            self.instr.write("NRDGS 1,AUTO")
            self.instr.write("MEM OFF")
            self.instr.write("NDIG 9")
            self.instr.close()
        except:
            logging.error("Error in %s config_10DCV_9digit" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
    def config_NPLC(self, NPLC):
        try:
            self.connect()
            self.instr.write("NPLC "+str(NPLC))
            self.instr.close()
        except:
            logging.error("Error in %s config_NPLC10" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
    def blank_display(self):
        try:
            self.connect()
            self.instr.write("DISP MSG,\"                 \"")
            self.instr.write("DISP ON")
            self.instr.close()
        except:
            logging.error("Error in %s blank_display" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
    def config_10kOHMF_9digit(self):
        try:
            self.connect()
            self.instr.write("PRESET NORM")
            self.instr.write("OHMF 1E4")
            self.instr.write("OCOMP ON")
            self.instr.write("DELAY 1")
            self.instr.write("TARM HOLD")
            self.instr.write("TRIG AUTO")
            self.instr.write("NRDGS 1,AUTO")
            self.instr.write("MEM OFF")
            self.instr.write("NDIG 9")
            self.instr.close()
        except:
            logging.error("Error in %s config_10kOHMF_9digit" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
    def config_10OHMF_9digit(self):
        try:
            self.connect()
            self.instr.write("PRESET NORM")
            self.instr.write("OHMF 10")
            self.instr.write("DELAY 1")
            self.instr.write("OCOMP ON")
            self.instr.write("TARM HOLD")
            self.instr.write("TRIG AUTO")
            self.instr.write("NRDGS 1,AUTO")
            self.instr.write("MEM OFF")
            self.instr.write("NDIG 9")
            self.instr.close()
        except:
            logging.error("Error in %s config_10OHMF_9digit" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
    def config_PT100_2W(self):
        try:
            self.connect()
            self.instr.write("PRESET NORM")
            self.instr.write("OHM 100")
            self.instr.write("MATH CRTD85")
            self.instr.write("DELAY 1")
            self.instr.write("OCOMP ON")
            self.instr.write("TARM HOLD")
            self.instr.write("TRIG AUTO")
            self.instr.write("NRDGS 1,AUTO")
            self.instr.write("MEM OFF")
            self.instr.write("NDIG 9")
            self.instr.close()
        except:
            logging.error("Error in %s config_PT1002W" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
    def config_1mA_9digit(self):
        try:
            self.connect()
            self.instr.write("PRESET NORM")
            self.instr.write("DCI 1E-3")
            self.instr.write("TARM HOLD")
            self.instr.write("TRIG AUTO")
            self.instr.write("NRDGS 1,AUTO")
            self.instr.write("MEM OFF")
            self.instr.write("NDIG 9")
            self.instr.close()
        except:
            logging.error("Error in %s config_10DCV_9digit" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
    def config_trigger_auto(self):
        try:
            self.connect()
            self.instr.write("TARM AUTO")
            self.instr.close()
        except:
            logging.error("Error in %s config_trigger_auto" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            
    def config_trigger_hold(self):
        try:
            self.connect()
            self.instr.write("TARM HOLD")
            self.instr.close()
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
            else:
                self.connect()
                logging.info("%s was not ready for trigger_once." % (self.get_title()))
                
            self.instr.close()
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
            self.instr.close()
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
            self.instr.close()
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
            self.instr.close()
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
            self.instr.close()
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
            self.instr.close()
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
            self.instr.close()
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
            self.instr.close()
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
            self.instr.close()
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
            self.instr.close()
        except:
            logging.error("Error in %s get_cal_1_1" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
            return cal_1_1
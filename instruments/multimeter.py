#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import vxi11
import time
import logging
import serial
import numpy as np
import math
import signal


class multimeter:

    title="Multimeter"

    def is_readable(self):
        return self.readable
    
    def connect(self):
        logging.debug("connect() acquiring lock")
        self.lock.acquire()
        logging.debug("connect() connecting instr")
        self.instr.open()
        
    def get_title(self):
        return self.title
        
    def get_read_val(self):
        self.connect()
        read_val = self.instr.read()
        logging.debug("get_read_val() reading "+str(read_val))
        self.close_instr_conn()
        return read_val
        
    def close_instr_conn(self):
        logging.debug("close_instr_conn() Closing instr")
        self.instr.close()
        logging.debug("close_instr_conn() regular lock release")
        time.sleep(0.5)
        self.lock.release()
        
        
    def read_stb(self):
        self.connect()
        logging.debug("read_stb() reading status")
        self.stb = self.instr.read_stb()
        logging.debug("stb read")
        self.close_instr_conn()


   
        
class HP3458A(multimeter):

    def __init__(self, ip, gpib_address, lock, title='HP 3458A'):
        logging.debug(self.title+' init started')
        self.title = title
        self.lock = lock
        self.ip = ip
        self.gpib_address = gpib_address
        self.lock.acquire()
        self.instr =  vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
        self.instr.timeout = 600
        self.instr.clear()
        self.instr.write("RESET")
        self.instr.write("END ALWAYS")
        self.instr.write("OFORMAT ASCII")
        self.instr.write("BEEP")
        logging.info("ID? -> "+self.instr.ask("ID?"))
        self.close_instr_conn()

        
            
    def config_NPLC(self, NPLC):
        self.connect()
        logging.debug(self.title+" config_NPLC")
        self.instr.write("NPLC "+str(NPLC))
        self.close_instr_conn()


            
    def config_NDIG(self, NDIG):
        self.connect()
        logging.debug(self.title+" config_NDIG")
        self.instr.write("NDIG "+str(NDIG))
        self.close_instr_conn()

            
    def config_DCV(self, RANG):
        self.connect()
        logging.debug(self.title+" config_DCV")
        self.instr.write("DCV "+str(RANG))
        self.close_instr_conn()

            
    def blank_display(self):
        self.connect()
        logging.debug(self.title+" blank_display")
        self.instr.write("DISP MSG,\"                 \"")
        self.instr.write("DISP ON")
        self.close_instr_conn()


        
    def config_trigger_auto(self):
        self.connect()
        logging.debug(self.title+" config_trigger_auto")
        self.instr.write("TARM AUTO")
        self.close_instr_conn()

            
    def config_trigger_hold(self):
        self.connect()
        logging.debug(self.title+" config_trigger_hold")
        self.instr.write("TARM HOLD")
        self.close_instr_conn()


            
    def trigger_once(self):
        logging.debug(self.title+' triggered once')
        self.connect()
        self.instr.write("TARM SGL")
        self.close_instr_conn()
          
    def acal_DCV(self):
        logging.debug(self.title+' ACAL DCV started')
        self.connect()
        self.instr.write("ACAL DCV")
        self.close_instr_conn()
        
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
        self.connect()
        temp = self.instr.ask("TEMP?")
        self.close_instr_conn()
        return temp
        
    def get_cal_72(self):
        logging.debug(self.title+' get_cal_72() called')
        self.connect()
        logging.debug(self.title+' connected')
        cal72 = self.instr.ask("CAL? 72")
        logging.debug(self.title+' CAL? 72 = '+str(cal72))
        self.close_instr_conn()
        return cal72

    def get_cal_175(self):
        self.connect()
        cal175 = self.instr.ask("CAL? 175")
        self.close_instr_conn()
        return cal175


class Timeout():
  """Timeout class using ALARM signal"""
  class Timeout(Exception): pass

  def __init__(self, sec):
    self.sec = sec

  def __enter__(self):
    signal.signal(signal.SIGALRM, self.raise_timeout)
    signal.alarm(self.sec)

  def __exit__(self, *args):
    signal.alarm(0) # disable alarm

  def raise_timeout(self, *args):
    raise Timeout.Timeout()
    

class K182_xdevs(multimeter):

    def __init__(self, ip, gpib_address, lock, title='Keithley 182'):
        logging.debug(self.title+' init started')
        self.title = title
        self.lock = lock
        self.ip = ip
        self.gpib_address = gpib_address
        self.lock.acquire()
        self.instr =  vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
        self.instr.timeout = 60
        #self.instr.clear()
        self.close_instr_conn()
        
    def default(self):
        self.instr.write("B1X")     # 6.5 digit resolution
        self.instr.write("F0G0X")   # Latest A/D reading, reading without prefix
        self.instr.write("O1P0N1X") # Enabled analog filter, disabled dig filter
        self.instr.write("R0X")     # Autorange
        self.instr.write("S2X")     # 100msec integration
        self.instr.write("T4X")     # Trigger on X multiple
        
    def read_data(self,cmd):
        data_float = 0.0
        data_str = ""
        self.instr.write(cmd)
        try:
            with Timeout(20):
                data_str = self.instr.read()
        except Timeout.Timeout:
            print ("Timeout exception from dmm %s on read_data() instr.read()\n" % self.name)
            return (0,float(0))
        #print ("Reading from dmm %s = %s" % (self.name,data_str))
        try:
            data_float = float(data_str)
        except ValueError:
            print("Exception thrown by dmm %s on read_data() - ValueError = %s\n" % (self.name,data_str))
            return (0,float(0)) # Exception on float conversion, 0 = error
        return (1,data_float) # Good read, 1 = converted to float w/o exception

    def get_data(self):
        self.status_flag,data = self.read_data("X")
        time.sleep(0.1)
        self.status_flag,data = self.read_data("X")
        time.sleep(0.1)
        if (self.status_flag):
            self.data = data
        return self.data


        


class W4950(multimeter):

    def __init__(self, ip, gpib_address, lock, title='Wavetek 4950'):
        logging.debug(self.title+' init started')
        self.title = title
        self.lock = lock
        self.ip = ip
        self.gpib_address = gpib_address
        self.lock.acquire()
        self.instr =  vxi11.Instrument(self.ip, "gpib0,"+str(self.gpib_address))
        self.instr.timeout = 600
        self.instr.clear()
        self.instr.write("*RST")
        time.sleep(2)
        self.instr.write("DCV 10,PCENT_100,LCL_GUARD")
        self.instr.write("TRIG_SRCE EXT")    
        self.instr.write("ACCURACY HIGH")
        self.instr.write("CORRECTN CERTIFIED")
        self.instr.write("BAND OFF")
        self.instr.write("LCL_GUARD")
        #self.instr.write("LEAD_NO '0123456789'")
        logging.info("*IDN? -> "+self.instr.ask("*IDN?"))
        logging.info("*OPT? -> "+self.instr.ask("*OPT?"))
        logging.info("DATE? CERTIFIED -> "+self.instr.ask("DATE? CERTIFIED"))
        logging.info("DATE? BASE -> "+self.instr.ask("DATE? BASE"))
        self.close_instr_conn()
        
    def trigger_once(self):
        logging.debug(self.title+' triggered once')
        self.connect()
        self.instr.write("*TRG;GET;RDG?")
        self.close_instr_conn()

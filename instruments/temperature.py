#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import smbus
import logging
import serial
from w1thermsensor import W1ThermSensor, Sensor
from multiprocessing import Process, Queue
import time


    
class TMP117:
    
    i2c_ch = 1
    reg_temp = 0x00
    reg_config = 0x01
    bus = smbus.SMBus(i2c_ch)
    readable = True
    read_val = 0.0
    
    def is_readable(self):
        return self.readable
    
    def __init__(self, address, title):
        self.title = title
        logging.debug(self.title+' init started')
        self.i2c_address = address
        val = self.bus.read_i2c_block_data(self.i2c_address, self.reg_config, 2)
        val[1] = val[1] & 0b00111111
        val[1] = val[1] | (0b10 << 6)
        self.bus.write_i2c_block_data(self.i2c_address, self.reg_config, val)
        val = self.bus.read_i2c_block_data(self.i2c_address, self.reg_config, 2)
        
        
    def measure(self):
        pass
        
        
    def get_title(self):
        return self.title
        
    def get_read_val(self):
        val = self.bus.read_i2c_block_data(self.i2c_address, self.reg_temp, 2)
        temp_c = (val[0] << 8) | (val[1] )
        temp_c = temp_c * 0.0078125
        return temp_c
        
    def is_ready_to_read(self):
        return True

        
    def is_measuring(self):
        return False
        
        
        
class R6581T_temp:
    
    def __init__(self, r6581t, title='R6581T Int Temp Sensor'):
        self.title = title
        self.r6581t = r6581t
        
        
    def get_title(self):
        logging.debug(self.title+' get_title started')
        return self.title
        
    def get_read_val(self):
        return self.r6581t.get_int_temp()
        
    def is_ready_to_read(self):
        return True
        
    def is_measuring(self):
        return False
        
    def measure(self):
        pass
        
        
        
class Arroyo:

    ready_to_read = False
    
    def __init__(self, dev='/dev/ttyUSB0', baud=38400, title='Arroyo TECSource'):
        self.dev = dev
        self.baud = baud
        self.title = title
        try:
            self.serial = serial.Serial(self.dev, self.baud)
            self.serial.write('CLS\r'.encode())
            self.serial.write('*IDN?\r'.encode())
            logging.debug(self.serial.readline().rstrip())
            self.serial.close()
        except:
            logging.error("Error in %s __init__" % self.title, exc_info=True)
            pass
        
        
    def get_title(self):
        logging.debug(self.title+' get_title started')
        return self.title
        
    def get_read_val(self):
        logging.debug(self.title+' get_read_val started')
        val = 0.0
        try:
            self.serial.open()
            self.serial.write('TEC:T?\r'.encode())
            val = float(self.serial.readline().rstrip())
            self.serial.close()
        except:
            logging.error("Error in %s __init__" % self.title, exc_info=True)
            pass
        logging.debug(self.title+' read '+str(val))
        return val
        
    def out(self, temp):
        logging.debug(self.title+' out started: '+str(temp))
        try:
            self.serial.open()
            command = 'TEC:T '+str(temp)+'\r'
            self.serial.write(command.encode())
            self.serial.close()
        except:
            logging.error("Error in %s out" % self.title, exc_info=True)
            pass

        
    def is_ready_to_read(self):
        return True
        
    def is_measuring(self):
        return False
        
    def measure(self):
        pass
        
        
        
class HPM7177_temp:
    
    def __init__(self, sn, title='HPM7177 Int Temp Sensor'):
        self.title = title
        self.sn = sn
        self.sensor = W1ThermSensor(Sensor.DS18B20, sn)
        
        
        self.ready_to_read = False
        self.measuring = False
        self.read_val = 0
        
        self.serial_process = Process(target=self.read_temperature)
        self.serial_process.daemon = True
        self.serial_process.start()
        
    def read_temperature(self):
        while True:
            if not self.measuring:
                self.measure()
            else:
                time.sleep(0.2)
        
    def get_title(self):
        logging.debug(self.title+' get_title started')
        return self.title
        
    def get_read_val(self):
        logging.debug(self.title+' get_read_val() '+str(self.ready_to_read))
        self.measuring = False
        #self.ready_to_read = False
        logging.debug(self.title+' returning '+self.read_val)
        return self.read_val
        
    def is_readable(self):
        logging.debug(self.title+' is_readable(self) '+str(self.ready_to_read))
        if self.ready_to_read:
            logging.debug(self.title+' is ready to read')
        else:
            logging.debug(self.title+' is not ready to read')
        return self.ready_to_read
        
    def is_measuring(self):
        return self.measuring
        
    def measure(self):
        logging.debug(self.title+' measuring now')
        self.measuring = True
        self.read_val = self.sensor.get_temperature()
        logging.debug(self.title+' measured '+str(self.read_val))
        self.ready_to_read = True
        logging.debug(self.title+' '+str(self.ready_to_read))
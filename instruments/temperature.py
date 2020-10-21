#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import smbus
import logging
import serial
#import io

    
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
        self.i2c_address = address
        # Read the CONFIG register (2 bytes)
        val = self.bus.read_i2c_block_data(self.i2c_address, self.reg_config, 2)
        #print("Old CONFIG:", val)
        #val2 = bus.read_i2c_block_data(i2c_address2, reg_config2, 2)
        # Set to 4 Hz sampling (CR1, CR0 = 0b10)
        val[1] = val[1] & 0b00111111
        val[1] = val[1] | (0b10 << 6)

        # Write 4 Hz sampling back to CONFIG
        self.bus.write_i2c_block_data(self.i2c_address, self.reg_config, val)

        # Read CONFIG to verify that we changed it
        val = self.bus.read_i2c_block_data(self.i2c_address, self.reg_config, 2)
        #print("New CONFIG:", val)
        logging.debug(self.title+' inited')
        
    # Read temperature registers and calculate Celsius from the TMP117 sensor
    def measure(self):
        logging.debug(self.title+' reading started')
        # Read temperature registers
        val = self.bus.read_i2c_block_data(self.i2c_address, self.reg_temp, 2)
        temp_c = (val[0] << 8) | (val[1] )
        # Convert registers value to temperature (C)
        temp_c = temp_c * 0.0078125

        self.read_val = temp_c

        
    def get_title(self):
        logging.debug(self.title+' get_title started')
        return self.title
        
    def get_read_val(self):
        logging.debug(self.title+' returning '+str(self.read_val))
        return self.read_val
        
    def is_ready_to_read(self):
        return True

        
    def is_measuring(self):
        return False
        
        
        
class R6581T_temp:

    ready_to_read = False
    
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
        val = 0.0
        try:
            self.serial.open()
            self.serial.write('TEC:T?\r'.encode())
            val = float(self.serial.readline().rstrip())
            self.serial.close()
        except:
            logging.error("Error in %s __init__" % self.title, exc_info=True)
            pass
        return val
        
    def out(self, temp):
        try:
            self.serial.open()
            self.serial.write('TEC:SET:T '+str(temp)+'\r'.encode())
        except:
            logging.error("Error in %s out" % self.title, exc_info=True)
            pass
        finally:
            self.lock.release()
        
    def is_ready_to_read(self):
        return True
        
    def is_measuring(self):
        return False
        
    def measure(self):
        pass
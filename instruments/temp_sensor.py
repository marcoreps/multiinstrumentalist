#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import smbus
import logging

    
class TMP117:
    
    i2c_ch = 1
    reg_temp = 0x00
    reg_config = 0x01
    bus = smbus.SMBus(i2c_ch)
    ready_to_read = False
    
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
        
        self.ready_to_read = True
        
        
    def get_title(self):
        logging.debug(self.title+' get_title started')
        return self.title
        
    def get_read_val(self):
        logging.debug(self.title+' returning '+str(self.read_val))
        return self.read_val
        
    def is_ready_to_read(self):
        if self.ready_to_read:
            self.ready_to_read = False
            return True
        else:
            return False
        
    def is_measuring(self):
        return False
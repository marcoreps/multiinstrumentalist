#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import smbus
    
class TMP117:
    
    i2c_ch = 1
    reg_temp = 0x00
    reg_config = 0x01
    bus = smbus.SMBus(i2c_ch)
    
    def __init__(self, address):   
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
        print("TMP117 sensor init")
        
    # Read temperature registers and calculate Celsius from the TMP117 sensor
    def read_temperature(self):
        # Read temperature registers
        val = self.bus.read_i2c_block_data(self.i2c_address, self.reg_temp, 2)
        temp_c = (val[0] << 8) | (val[1] )
        # Convert registers value to temperature (C)
        temp_c = temp_c * 0.0078125

        return temp_c
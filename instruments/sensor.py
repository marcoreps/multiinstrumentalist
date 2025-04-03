#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from smbus2 import SMBus
import logging
import serial
from multiprocessing import Process, Queue
import time
import qwiic_ccs811
import qwiic_i2c





class CCS811:

    readable = True
    
    def is_readable(self):
        return self.sensor.data_available()

    def __init__(self, title, co2_tvoc="co2"):
        self.title = title
        self.co2_tvoc = co2_tvoc
        logging.debug(self.title+' init started')
        self.sensor = qwiic_ccs811.QwiicCcs811()


        self.sensor.begin()
        
    def measure(self):
        pass
        
        
    def get_title(self):
        return self.title
        
    def get_read_val(self):
        self.sensor.read_algorithm_results()
        if self.co2_tvoc == "co2":
            return self.sensor.CO2
        else:
            return self.sensor.TVOC

        
    def is_measuring(self):
        return False
        
MODE_CONTINUOUS_CONVERSION_MODE = 0b00
MODE_ONE_SHOT = 0b11
MODE_SHUTDOWN = 0b01

MODE_AVG_0  = 0b00
MODE_AVG_8  = 0b01
MODE_AVG_32 = 0b10
MODE_AVG_64 = 0x11

# Knonwn Addresses.
I2C_ADDRESSES = [0x48, 0x49, 0x4a, 0x4b]

class Tmp117(object):
  REG_TEMP_RESULT   = 0X00
  REG_CONFIGURATION = 0x01
  REG_T_HIGH_LIMIT  = 0X02
  REG_T_LOW_LIMIT   = 0X03
  REG_EEPROM_UL     = 0X04
  REG_EEPROM1       = 0X05
  REG_EEPROM2       = 0X06
  REG_TEMP_OFFSET   = 0X07
  REG_EEPROM3       = 0X08
  REG_DEVICE_ID     = 0X0F

  DEVICE_ID_VALUE = 0x0117
  TEMP_RESOLUTION = 0.0078125
    
  def __init__(self, address=None, i2c_driver=None):
    self.address = I2C_ADDRESSES[0] if address is None else address

    self._i2c = i2c_driver or qwiic_i2c.getI2CDriver()
    if self._i2c is None:
      raise RuntimeError("Unable to load I2C driver.")

  def init(self):
    if not qwiic_i2c.isDeviceConnected(self.address):
      raise RuntimeError(
          'Device is not connected at address: 0x{:X}'
          .format(self.address))
    chip_id = self.getDeviceId()
    if chip_id != self.DEVICE_ID_VALUE:
      raise ValueError('Wrong chip id at address: 0x{:X}'.format(chip_id))
        
  def readRegister(self, register):
    data = self._i2c.readWord(self.address, register)

    return (data >> 8) & 0xff | (data & 0xff) << 8

  def writeRegister(self, register, data):
    data = (data >> 8) & 0xff | (data & 0xff) << 8
    self._i2c.writeWord(self.address, register, data)
    
  def readTempC(self):
    reg_value = self.readRegister(self.REG_TEMP_RESULT)
    return reg_value * self.TEMP_RESOLUTION

  def getConfigurationRegister(self):
    return self.readRegister(self.REG_CONFIGURATION)

  def writeConfiguration(self, config):
    self.writeRegister(self.REG_CONFIGURATION, config)
    
  def setConversionMode(self, mode):
    if mode not in (MODE_AVG_0, MODE_AVG_8, MODE_AVG_32, MODE_AVG_64):
      return
    config = self.getConfigurationRegister()
    config &= ~(0x3 << 5)
    config |= (mode << 5)
    self.writeConfiguration(config)


  def setMode(self, mode):
    config = self.getConfigurationRegister()
    config &= ~(0x03 << 10)
    config |= (mode << 10)
    self.writeConfiguration(config)
        
        
  def oneShotMode(self):
    self.setMode(MODE_ONE_SHOT)



  def getDeviceId(self):
    return self.readRegister(self.REG_DEVICE_ID)
    
  def dataReady(self):
    config = self.getConfigurationRegister()
    return config & (1 << 13)


        
        
        
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
            #self.serial.write('CLS\r'.encode())
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

        
    def is_readable(self):
        return True
        
    def is_measuring(self):
        return False
        
    def measure(self):
        pass
        
    def enable_output(self, state):
        logging.debug(self.title+' out enable_output: '+str(state))
        try:
            self.serial.open()
            command = 'TEC:OUTput '+str(state)+'\r'
            self.serial.write(command.encode())
            self.serial.close()
        except:
            logging.error("Error in %s out" % self.title, exc_info=True)
            pass
        

class HP3458A_temp:
    
    def __init__(self, HP3458A, title='HP3458A Int Temp Sensor'):
        self.title = title
        self.HP3458A = HP3458A
        
    def get_title(self):
        logging.debug(self.title+' get_title started')
        return self.title
        
    def get_read_val(self):
        return self.HP3458A.get_int_temp()
        
    def is_readable(self):
        return self.HP3458A.is_readable()
        
    def is_measuring(self):
        return False
        
    def measure(self):
        pass
        
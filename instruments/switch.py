import smbus
import time



EXPANDER_REG_OUTPUT0 = 0x2
EXPANDER_REG_OUTPUT1 = 0x3
EXPANDER_REG_CONFIG0 = 0x6
EXPANDER_REG_CONFIG1 = 0x7

SWITCHING_TIME = 4
DEBOUNCE_TIME = 3


channels = [
     {"chip" : 0x4, "port" : 0, "pin" : 1 << 0, "compin" : 1 << 4, "pcbIndex" : 9},
     {"chip" : 0x4, "port" : 0, "pin" : 1 << 1, "compin" : 1 << 4, "pcbIndex" : 10},
     {"chip" : 0x4, "port" : 0, "pin" : 1 << 2, "compin" : 1 << 4, "pcbIndex" : 11},
     {"chip" : 0x4, "port" : 0, "pin" : 1 << 3, "compin" : 1 << 4, "pcbIndex" : 12},
     {"chip" : 0x4, "port" : 1, "pin" : 1 << 4, "compin" : 1 << 3, "pcbIndex" : 13},
     {"chip" : 0x4, "port" : 1, "pin" : 1 << 5, "compin" : 1 << 3, "pcbIndex" : 14},
     {"chip" : 0x4, "port" : 1, "pin" : 1 << 6, "compin" : 1 << 3, "pcbIndex" : 15},
     {"chip" : 0x4, "port" : 1, "pin" : 1 << 7, "compin" : 1 << 3, "pcbIndex" : 16},
     {"chip" : 0x0, "port" : 0, "pin" : 1 << 0, "compin" : 1 << 4, "pcbIndex" : 5},
     {"chip" : 0x0, "port" : 0, "pin" : 1 << 1, "compin" : 1 << 4, "pcbIndex" : 6},
     {"chip" : 0x0, "port" : 0, "pin" : 1 << 2, "compin" : 1 << 4, "pcbIndex" : 7},
     {"chip" : 0x0, "port" : 0, "pin" : 1 << 3, "compin" : 1 << 4, "pcbIndex" : 8},
     {"chip" : 0x0, "port" : 1, "pin" : 1 << 4, "compin" : 1 << 3, "pcbIndex" : 1},
     {"chip" : 0x0, "port" : 1, "pin" : 1 << 5, "compin" : 1 << 3, "pcbIndex" : 2},
     {"chip" : 0x0, "port" : 1, "pin" : 1 << 6, "compin" : 1 << 3, "pcbIndex" : 3},
     {"chip" : 0x0, "port" : 1, "pin" : 1 << 7, "compin" : 1 << 3, "pcbIndex" : 4}]


combineSwitch = {"chip" : 0x4, "port" : 1, "pin" : 2, "comPin" : 1, "pcbIndex" : 0}


class takovsky_scanner:
    i2c   =  smbus.SMBus(1)
    def __init__(self, title="Scanner"):
        for port in range(2):
            self.switchingGpioSetOutput(0x00, port, 0x00)
            self.switchingGpioSetOutput(0x04, port, 0x00)
            self.switchingGpioSetMode(0x00, port, 0x00)
            self.switchingGpioSetMode(0x04, port, 0x00)

        # Reset relay state
        self.switchingOpenRelay(combineSwitch)
        time.sleep(DEBOUNCE_TIME/1000)

        for i in range(16):
            self.switchingOpenRelay(channels[i])

        g_closedChannel = 0
        g_fwireEnabled = 0
        
        
    def switchingGpioSetOutput(self, subaddress, port, pins):
        if port:
            reg = EXPANDER_REG_OUTPUT1
        else:
            reg = EXPANDER_REG_OUTPUT0
        address = subaddress|0x20
        self.i2c.Write_byte_data(address,reg,pins)

    def switchingGpioSetMode(self, subaddress, port, inputPins):
        if port:
            reg = EXPANDER_REG_CONFIG1
        else:
            reg = EXPANDER_REG_CONFIG0
        address = subaddress|0x20
        self.i2c.Write_byte_data(address,reg,pins)
        
    def switchingOpenRelay(self, relay):
        switchingGpioSetOutput(relay["chip"], relay["port"], 0xFF & relay["pin"])
        time.sleep(SWITCHING_TIME/1000)
        switchingGpioSetOutput(relay["chip"], relay["port"], 0)
        
        
scanner=takovsky_scanner()
import smbus
import time



EXPANDER_REG_OUTPUT0 = 0x2
EXPANDER_REG_OUTPUT1 = 0x3
EXPANDER_REG_CONFIG0 = 0x6
EXPANDER_REG_CONFIG1 = 0x7

SWITCHING_TIME = 4
DEBOUNCE_TIME = 3


channels = [
     {"chip" : 0x4, "port" : 0, "pin" : 1 << 0, "compin" : 1 << 4, "pcbIndex" : 9, "index" : 0},
     {"chip" : 0x4, "port" : 0, "pin" : 1 << 1, "compin" : 1 << 4, "pcbIndex" : 10, "index" : 1},
     {"chip" : 0x4, "port" : 0, "pin" : 1 << 2, "compin" : 1 << 4, "pcbIndex" : 11, "index" : 2},
     {"chip" : 0x4, "port" : 0, "pin" : 1 << 3, "compin" : 1 << 4, "pcbIndex" : 12, "index" : 3},
     {"chip" : 0x4, "port" : 1, "pin" : 1 << 4, "compin" : 1 << 3, "pcbIndex" : 13, "index" : 4},
     {"chip" : 0x4, "port" : 1, "pin" : 1 << 5, "compin" : 1 << 3, "pcbIndex" : 14, "index" : 5},
     {"chip" : 0x4, "port" : 1, "pin" : 1 << 6, "compin" : 1 << 3, "pcbIndex" : 15, "index" : 6},
     {"chip" : 0x4, "port" : 1, "pin" : 1 << 7, "compin" : 1 << 3, "pcbIndex" : 16, "index" : 7},
     {"chip" : 0x0, "port" : 0, "pin" : 1 << 0, "compin" : 1 << 4, "pcbIndex" : 5, "index" : 8},
     {"chip" : 0x0, "port" : 0, "pin" : 1 << 1, "compin" : 1 << 4, "pcbIndex" : 6, "index" : 9},
     {"chip" : 0x0, "port" : 0, "pin" : 1 << 2, "compin" : 1 << 4, "pcbIndex" : 7, "index" : 10},
     {"chip" : 0x0, "port" : 0, "pin" : 1 << 3, "compin" : 1 << 4, "pcbIndex" : 8, "index" : 11},
     {"chip" : 0x0, "port" : 1, "pin" : 1 << 4, "compin" : 1 << 3, "pcbIndex" : 1, "index" : 12},
     {"chip" : 0x0, "port" : 1, "pin" : 1 << 5, "compin" : 1 << 3, "pcbIndex" : 2, "index" : 13},
     {"chip" : 0x0, "port" : 1, "pin" : 1 << 6, "compin" : 1 << 3, "pcbIndex" : 3, "index" : 14},
     {"chip" : 0x0, "port" : 1, "pin" : 1 << 7, "compin" : 1 << 3, "pcbIndex" : 4, "index" : 15}]


combineSwitch = {"chip" : 0x4, "port" : 1, "pin" : 2, "comPin" : 1, "pcbIndex" : 0}


class takovsky_scanner:
    i2c   =  smbus.SMBus(1)
    g_closedChannel = 0
    g_fwireEnabled = 0
    g_mbbEnabled = 0;
    g_closedChannel = 0;
    
    def __init__(self, title="Scanner"):
        for port in range(2):
            self.switchingGpioSetOutput(0x00, port, 0x00)
            self.switchingGpioSetOutput(0x04, port, 0x00)
            self.switchingGpioSetMode(0x00, port, 0x00)
            self.switchingGpioSetMode(0x04, port, 0x00)

        # Reset relay state
        self.switchingOpenRelay(combineSwitch)
        time.sleep(DEBOUNCE_TIME/1000)

        while(True):
            for i in range(16):
                self.switchingOpenRelay(channels[i])
                
            time.sleep(0.5)
            
            for i in range(16):
                self.switchingCloseRelay(channels[i])
                
            time.sleep(0.5)
        
        
    def switchingGpioSetOutput(self, subaddress, port, pins):
        if port:
            reg = EXPANDER_REG_OUTPUT1
        else:
            reg = EXPANDER_REG_OUTPUT0
        address = subaddress|0x20
        self.i2c.write_byte_data(address,reg,pins)

    def switchingGpioSetMode(self, subaddress, port, pins):
        if port:
            reg = EXPANDER_REG_CONFIG1
        else:
            reg = EXPANDER_REG_CONFIG0
        address = subaddress|0x20
        self.i2c.write_byte_data(address,reg,pins)
        
    def switchingOpenRelay(self, relay):
        self.switchingGpioSetOutput(relay["chip"], relay["port"], 0xFF & ~relay["pin"])
        time.sleep(SWITCHING_TIME/1000)
        self.switchingGpioSetOutput(relay["chip"], relay["port"], 0)
        
    def switchingCloseRelay(self, relay):
        self.switchingGpioSetOutput(relay["chip"], relay["port"], relay["pin"])
        time.sleep(SWITCHING_TIME/1000)
        self.switchingGpioSetOutput(relay["chip"], relay["port"], 0)
        
    def switchingSwitchChannel(self, channelId):
        if(channelId >= 16):
            return
        
        if(self.g_fwireEnabled && channelId >= 16 / 2):
            channelId = channelId / 2

        if(self.g_closedChannel && self.g_closedChannel["index"] == channelId):
            return

        if(!self.g_mbbEnabled):
            self.switchingOpenCurrent()
            time.sleep(DEBOUNCE_TIME/1000)

        if(self.g_fwireEnabled):
            self.switchingCloseRelay(channels[channelId + 8])

        self.switchingCloseRelay(channels[channelId])

        if(self.g_mbbEnabled):
            time.sleep(DEBOUNCE_TIME)
            self.switchingOpenCurrent()

        self.g_closedChannel = channels[channelId]
    }
        
        
scanner=takovsky_scanner()

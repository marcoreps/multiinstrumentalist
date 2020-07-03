#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import vxi11


class S7081:
    
    vxi_ip = "192.168.178.88"
    address = 16
    
    def __init__(self, address):   
        self.gpib_address = address
        instr =  vxi11.Instrument(self.vxi_ip, "gpib0,"+str(self.address))
        print(instr.ask("*IDN?"))

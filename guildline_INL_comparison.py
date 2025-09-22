#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyvisa
import csv
import logging
from time import time
from datetime import datetime, timedelta
import sys
import random
import statistics
from decimal import Decimal

from instruments.multimeter import *

def perform_linearity_test():

    # test parameters
    num_points = 21
    min_voltage = Decimal('-1.0')
    max_voltage = Decimal('1.0')
    nreadings_per_point = 4
    NPLC = 100

    test_points = [min_voltage + i * (max_voltage - min_voltage) / (num_points - 1) for i in range(num_points)]
    results = []
    
    try:
        rm = pyvisa.ResourceManager('@py')
        instruments = {}
        instruments["3458B"] = HP3458A(rm, 'TCPIP::192.168.0.5::gpib0,22', title='3458B')
        instruments["3458B"].config_DCV(10)
        instruments["3458B"].config_NDIG(9)
    except Exception as e:
        print(f"Error configuring multimeter: {e}")
        return

    print("Starting linearity test.")
    
    for i, set_voltage in enumerate(test_points):
        # Exercise the integrator while waiting
        instruments["3458B"].config_NPLC(10)
        instruments["3458B"].config_trigger_auto()
        # Prompt the user to set the voltage and wait for confirmation
        print(f"\n[{i+1}/{num_points}] Set source to {set_voltage:.4f} V.")
        input("Press Enter to trigger the DMM measurement...")
        # Actual settings for measurement
        instruments["3458B"].config_NPLC(NPLC)
        instruments["3458B"].config_trigger_hold()
        dmm_reading = 0
        for j in range(nreadings_per_point):
            # Trigger the DMM to take a reading
            instruments["3458B"].trigger_once()
            dmm_reading += float(instruments["3458B"].get_read_val())/nreadings_per_point
        instruments["3458B"].beep()
        results.append((set_voltage, dmm_reading))
        print(f"DMM reading: {dmm_reading:.6f} V")
        
    print("\nDone, saving data to CSV file.")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"linearity_test_3458A_guildline9930_{timestamp}.csv"
    
    try:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Set Test Voltage (V)', 'DMM Reading (V)'])
            writer.writerows(results)
        print(f"Successfully saved test results to '{filename}'")
    except IOError as e:
        print(f"Error writing to file '{filename}': {e}")
    finally:
        pass

if __name__ == "__main__":
    perform_linearity_test()
import serial
import pyvisa
import csv
from instruments.multimeter import *
import random
import time
import datetime

rm = pyvisa.ResourceManager()

# Reference : ±10V
# DAC Counts: 20000
# Resolution: 1mV
# Note: only outputs between ±9V are valid, see 'modern-calibrator-design.pdf'

start =  9900
stop  = 10100
step  =    10

runs = 10

# Generate the input list
inputList = [i for i in range(start, stop + step, step)]
sortedInputList = sorted(inputList)  # Keep a sorted copy for reference

NPLC = 100
soak = 10 # measurement soak time, DAC settles to 0.02% within 1us
samples_per_meter_per_step = 5

instr=HP3458A(rm, 'GPIB0::22::INSTR', title='3458A')
instr.config_DCV(10)
instr.config_NDIG(9)
instr.config_NPLC(NPLC)
instr.config_trigger_hold()

serial = serial.Serial("/dev/ttyACM0", 9600) # DAC serial port goes here
now = datetime.datetime.now()
timestr = now.strftime("%Y%m%d-%H%M%S_")

fileName = "csv/"+timestr+"WoodwardSynchronousDAC.csv"

for run in range(runs):
    # Shuffle input list for this run
    random.shuffle(inputList)
    # Temporary dictionary to store readings
    readings = {}
    
    for value in inputList:
        print(f"Setting DAC to {value} and reading measurement...")
        command = str(value) + "\n"
        serial.write(command.encode())
        time.sleep(0.5)
        # write 3458A reading for respective col 0 value
        instr.trigger_once()
        reading = instr.get_read_val()
        if reading is not None:
            readings[value] = reading.rstrip()
            
    # Write readings to the CSV file in the correct order
    with open(fileName, "a") as f:
        row = ", ".join(readings.get(key, "N/A") for key in sortedInputList) + "\n"
        f.write(row)
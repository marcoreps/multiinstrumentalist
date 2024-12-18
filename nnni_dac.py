import serial
import pyvisa
import csv
from instruments.multimeter import *
from time import sleep
from datetime import datetime

# Initialize the resource manager and instrument
rm = pyvisa.ResourceManager()
instr = HP3458A(rm, 'GPIB0::22::INSTR', title='3458A')

# Configure the 3458A multimeter
instr.config_DCV(10)
instr.config_NDIG(9)
instr.config_NPLC(25)  # Set NPLC to 25 for better accuracy
instr.config_trigger_hold()

# Serial port for DAC
serial_port = serial.Serial("/dev/ttyACM0", 9600)  # Replace with your DAC's serial port

# DAC value to set
dac_value = 15000
command = f"{dac_value}\n"

# File to store the readings
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
file_name = f"DAC_Readings_{timestamp}.csv"

# Set the DAC
print(f"Setting DAC to {dac_value}...")
serial_port.write(command.encode())
sleep(1)  # Allow time for DAC to settle

# Open the CSV file and write the header
with open(file_name, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Reading Number", "Measurement (V)"])  # Header

    # Take 1000 readings
    print(f"Starting measurements... Logging to {file_name}")
    for i in range(1, 1001):
        instr.trigger_once()
        reading = instr.get_read_val()

        if reading is not None:
            writer.writerow([i, reading])
            print(f"Reading {i}: {reading} V")
        else:
            writer.writerow([i, "Error"])
            print(f"Reading {i}: Error")

print("Measurement completed.")

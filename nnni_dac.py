import serial
import pyvisa
import csv
from instruments.multimeter import *
from datetime import datetime

import smbus2
import bme280
port = 1
address = 0x77
bus = smbus2.SMBus(port)
calibration_params = bme280.load_calibration_params(bus, address)



rm = pyvisa.ResourceManager()

start = 0b00000000000000000000
stop  = 0b11111111111111111111
#step  = 0b00000100000000000000 # 64 MSBs
step  = 0b00000000010000000000 # step size 1024, use for fine sweep

NPLC = 100
soak = 5 # measurement soak time, DAC settles to 0.02% within 1us
samples_per_meter_per_step = 5

a=HP3458A(rm, 'GPIB0::22::INSTR', title='3458A')
a.config_DCV(10)
a.config_NDIG(9)
a.config_NPLC(NPLC)
a.config_trigger_hold()

b=HP3458A(rm, 'GPIB0::23::INSTR', title='3458B')
b.config_DCV(10)
b.config_NDIG(9)
b.config_NPLC(NPLC)
b.config_trigger_hold()

serial = serial.Serial("/dev/ttyACM0", 9600)
timestr = time.strftime("%Y%m%d-%H%M%S_")

with open('csv/'+timestr+'NNNIDAC_HP3458AB_INL.csv', mode='w') as csv_file:

    csv_file.write("# INL run")
    csv_file.write("# soak = "+str(soak))
    csv_file.write("# samples_per_meter_per_step = "+str(samples_per_meter_per_step))
    csv_file.write("# NPLC = "+str(NPLC))

    fieldnames = ['dac_counts', '3458A_volt', '3458B_volt', 'ambient_temp']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    
    clock=datetime.now()
    
    for u in range(start, stop+1, step):
        command=str(u)+'\r'
        serial.write(command.encode())
        time.sleep(soak)
    
        for n in range(samples_per_meter_per_step):
            a.trigger_once()
            temperature_sensor_data = bme280.sample(bus, address, calibration_params)
            b.trigger_once()
            writer.writerow({'dac_counts': u, '3458A_volt': float(a.get_read_val()), '3458B_volt': float(b.get_read_val()), 'ambient_temp': temperature_sensor_data.temperature})
            
        print( "Time left: "+str((datetime.now()-clock)*((stop-u)/step)))
        clock=datetime.now()
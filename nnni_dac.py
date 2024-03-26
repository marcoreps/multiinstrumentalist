import serial
import pyvisa
import csv
from time import time

from instruments.multimeter import *
from instruments.sensor import *
from datetime import datetime

start = 0b00000000000000000000
stop  = 0b11111100000000000000
step  = 0b00000100000000000000 # 64 MSBs
# step  = 0b00000111111111111111 # 64 MSBs plus R2R

tempStart = 20
tempStop  = 40
tempStep  = 5

tempSoak = 6 # 600

rm = pyvisa.ResourceManager()

NPLC = 1 #100
soak = 1 #10
samples_per_meter_per_step = 1 #5

instr=HP3458A(rm, 'GPIB0::22::INSTR', title='3458A')
instr.config_DCV(10)
instr.config_NDIG(9)
instr.config_NPLC(NPLC)
instr.config_trigger_hold()

dac = serial.Serial("/dev/ttyACM0", 9600)

arroyo=Arroyo(dev='/dev/ttyUSB0', baud=38400, title='Arroyo TECSource')

timestr = time.strftime("%Y%m%d-%H%M%S_")
with open('csv/'+timestr+'NNNIDAC_HP3458A_INL_temperature.csv', mode='w') as csv_file:
    
    for t in range(tempStart, tempStop + tempStep, tempStep):
        arroyo.out(t)
        time.sleep(tempSoak)
        
        csv_file.write("# INL run")
        csv_file.write("# soak = "+str(soak))
        csv_file.write("# samples_per_meter_per_step = "+str(samples_per_meter_per_step))
        csv_file.write("# NPLC = "+str(NPLC))
        csv_file.write("# Temp = " + str(t))

        fieldnames = ['dac_counts', '3458A_volt', 'arroyo_temperature']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(start, stop, step):
            command=str(i)+'\n'
            dac.write(command.encode())
            time.sleep(soak)
            clock = datetime.now()
            for n in range(samples_per_meter_per_step):
                instr.trigger_once()
                writer.writerow({'dac_counts': i, '3458A_volt': float(instr.get_read_val()), 'arroyo_temperature': arroyo.get_read_val()})
                clock = clock-datetime.now()
                t_steps_left = (tempStop + tempStep - t)/tempStep
                i_steps_left = (stop - i)/step
                i_steps_per_t = (stop - start)/step
                print("Time left: "+str(clock*i_steps_left + clock*i_steps_per_t*t_steps_left))
                clock = datetime.now()

import serial
import pyvisa
import csv
from time import time

from instruments.multimeter import *
from instruments.sensor import *
from datetime import datetime

values = [
    0, 53248, 104448, 159744, 212992,
    263168, 315392, 365568, 421888, 472064,
    524288, 574464, 626688, 671744, 737280,
    786432, 851968, 885760, 951296, 1048575
]

tempStart = 20
tempStop  = 40
tempStep  = 5

tempSoak = 1000 # 600

rm = pyvisa.ResourceManager()

NPLC = 100 #100
soak = 10 #10
samples_per_meter_per_step = 5 #5

instr=HP3458A(rm, 'GPIB0::22::INSTR', title='3458A')
instr.config_DCV(10)
instr.config_NDIG(9)
instr.config_NPLC(NPLC)
instr.config_trigger_hold()

dac = serial.Serial("/dev/ttyACM0", 9600)

arroyo=Arroyo(dev='/dev/ttyUSB0', baud=38400, title='Arroyo TECSource')

timestr = time.strftime("%Y%m%d-%H%M%S_")
with open('csv/'+timestr+'NNNIDAC_HP3458A_INL_temperature.csv', mode='w') as csv_file:
    
    clock = datetime.now()
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

        for i in values:
            command=str(i)+'\n'
            dac.write(command.encode())
            time.sleep(soak)
            
            for n in range(samples_per_meter_per_step):
                instr.trigger_once()
                writer.writerow({'dac_counts': i, '3458A_volt': float(instr.get_read_val()), 'arroyo_temperature': arroyo.get_read_val()})
                
        runtime = datetime.now()-clock
        t_steps_left = (tempStop + tempStep - t)/tempStep
        print("Time left: "+str(runtime*t_steps_left ))
        clock = datetime.now()
        
arroyo.out(20)
arroyo.enable_output(0)
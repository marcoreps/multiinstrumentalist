import serial
import pyvisa
import csv
from instruments.multimeter import *
from datetime import datetime

rm = pyvisa.ResourceManager()

start = 0b00000000000000000000
stop  = 0b11111111111111111111
#step  = 0b00000100000000000000 # 64 MSBs
step  = 0b00000000010000000000 # step size 1024, use for fine sweep

NPLC = 100
soak = 10 # measurement soak time, DAC settles to 0.02% within 1us
samples_per_meter_per_step = 5

instr=HP3458A(rm, 'GPIB0::22::INSTR', title='3458A')
instr.config_DCV(10)
instr.config_NDIG(9)
instr.config_NPLC(NPLC)
instr.config_trigger_hold()

serial = serial.Serial("/dev/ttyACM0", 9600)
timestr = time.strftime("%Y%m%d-%H%M%S_")

with open('csv/'+timestr+'NNNIDAC_HP3458A_INL.csv', mode='w') as csv_file:

    csv_file.write("# INL run")
    csv_file.write("# soak = "+str(soak))
    csv_file.write("# samples_per_meter_per_step = "+str(samples_per_meter_per_step))
    csv_file.write("# NPLC = "+str(NPLC))

    fieldnames = ['dac_counts', '3458A_volt']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    
    clock=datetime.now()
    
    for u in range(start, stop+1024, step):
        command=str(u)+'\r'
        serial.write(command.encode())
        time.sleep(soak)
    
        for n in range(samples_per_meter_per_step):
            instr.trigger_once()
            writer.writerow({'dac_counts': u, '3458A_volt': float(instr.get_read_val())})
        print( "Time left: "+str((datetime.now()-clock)*((stop-u)/step)))
        clock=datetime.now()
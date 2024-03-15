import serial
import pyvisa
import csv
from instruments.multimeter import *

rm = pyvisa.ResourceManager()

start = 0b00000000000000000000
stop  = 0b11111100000000000000
step  = 0b00000100000000000000 # 64 MSBs
# step  = 0b00000000010000000000 # step size 1024, use for fine sweep
NPLC = 10
soak = 1 # measurement soak time, DAC settles to 0.02% within 1us
samples_per_meter_per_step = 1

instruments["3458A"]=HP3458A(rm, 'GPIB0::22::INSTR', title='3458A')
instruments["3458A"].config_DCV(10)
instruments["3458A"].config_NDIG(9)
instruments["3458A"].config_NPLC(NPLC)
instruments["3458A"].config_trigger_hold()

serial = serial.Serial("/dev/ttyACM0", 9600)
timestr = time.strftime("%Y%m%d-%H%M%S_")

with open('csv/'+timestr+'NNNIDAC_HP3458A_INL.csv', mode='w') as csv_file:
    fieldnames = ['dac_counts', '3458A_volt']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    
    for u in range(start, stop+1, step):
        serial.write(str(u)+'\r'.encode())
        time.sleep(soak)
    
        for n in range(samples_per_meter_per_step):
            instr.write("TARM SGL")
            writer.writerow({'dac_counts': u, '3458A_volt': instr.read()})
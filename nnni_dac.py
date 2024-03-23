import serial
import pyvisa
import csv
from instruments.multimeter import *
from datetime import datetime

rm = pyvisa.ResourceManager()

values = [
    0, 53248, 104448, 159744, 212992,
    263168, 315392, 365568, 421888, 472064,
    524288, 574464, 626688, 671744, 737280,
    786432, 851968, 885760, 951296, 1048575
]

NPLC = 100
soak = 10 # measurement soak time, DAC settles to 0.02% within 1us
samples_per_meter_per_step = 5
number_of_runs = 10

instr=HP3458A(rm, 'GPIB0::22::INSTR', title='3458A')
instr.config_DCV(10)
instr.config_NDIG(9)
instr.config_NPLC(NPLC)
instr.config_trigger_hold()

serial = serial.Serial("/dev/ttyACM0", 9600)

for n in range(number_of_runs):
    print(n)
    timestr = time.strftime("%Y%m%d-%H%M%S_")
    with open('csv/'+timestr+'NNNIDAC_HP3458A_INL.csv', mode='w') as csv_file:

        csv_file.write("# INL run")
        csv_file.write("# soak = "+str(soak))
        csv_file.write("# samples_per_meter_per_step = "+str(samples_per_meter_per_step))
        csv_file.write("# NPLC = "+str(NPLC))

        fieldnames = ['dac_counts', '3458A_volt']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        
        for v in values:
            command=str(v)+'\n'
            serial.write(command.encode())
            time.sleep(soak)
        
            for n in range(samples_per_meter_per_step):
                instr.trigger_once()
                writer.writerow({'dac_counts': v, '3458A_volt': float(instr.get_read_val())})
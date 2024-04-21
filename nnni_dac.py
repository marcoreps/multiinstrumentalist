import serial
import pyvisa
import csv
from instruments.multimeter import *
from datetime import datetime

rm = pyvisa.ResourceManager()

start = 0b00000000000000000000
stop  = 0b11111111111111111111
step  = 0b00000000010000000000

# temporary container for data
data = [[],[],[],[],[],[]]

# generates DAC input codes and writes to column 0
for i in range(start, stop, step):
    data[0].append(i)

# append extra zeroes to the end to pad number of rows
data[0].append(0)
data[0].append(0)

# m and c values for endpoint-fit INL
m = 0.0
c = 0.0

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

# outer loop writes to columns 1 through 5
for i in range(1, 6, 1):
    
    # step one - calculate m and c values for each columm (i.e. one run)
    # write 0 value to DAC
    command = str(data[0][0]) + '\r'
    serial.write(command.encode())
    # read 0 value from 3458A
    instr.trigger_once()
    startVolt = float(instr.get_read_val())
    # write stop value to DAC
    command = str(data[0][1023]) + '\r'
    serial.write(command.encode())
    # read stop value from 3458A
    instr.trigger_once()
    stopVolt = float(instr.get_read_val())
    
    #calculate m and c values, they will be stored later
    m = (stopVolt - startVolt)/(data[0][1023] - data[0][0])
    c = stopVolt - (m * data[0][1023])

    # inner loop for 1024 DAC values (indices 0 to 1023)
    for j in range(1024):
        # send DAC values from column 0
        command = str(data[0][j]) + '\r'
        serial.write(command.encode())
        # write 3458A reading for respective col 0 value
        instr.trigger_once()
        data[i].append(float(instr.get_read_val()))
    
    # append m and c to column at the end of each run
    data[i].append(m)
    data[i].append(c)

with open('csv/'+timestr+'NNNIDAC_HP3458A_INL.csv', mode='w') as csv_file:

    csv_file.write("# INL run")
    csv_file.write("# soak = "+str(soak))
    csv_file.write("# samples_per_meter_per_step = "+str(samples_per_meter_per_step))
    csv_file.write("# NPLC = "+str(NPLC))

    fieldnames = ['dac_counts', 'Run 1', 'Run 2', 'Run 3', 'Run 4', 'Run 5']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    
    clock=datetime.now()
    
    # 1026 here because of added m and c values in each column
    for i in range(1026):
        writer.writerow({'dac_counts': data[0][i], 'Run 1': data[1][i], 'Run 2': data[2][i], 'Run 3': data[3][i], 'Run 4': data[4][i], 'Run 5': data[5][i]})
        print( "Time left: "+str((datetime.now()-clock)*((stop-u)/step)))
        clock=datetime.now()
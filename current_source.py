import numpy as np
import csv
import logging
import pyvisa
import random
from datetime import datetime, timedelta


from instruments.sensor import *
from instruments.multimeter import *
from instruments.source import *
from instruments.switch import *

rm = pyvisa.ResourceManager()
instruments = dict()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s')
logging.info("Starting ...")

def current_source_output_impedance_test():

    name = "Current_Source"

    runs = 5
    settling_time = 1.0  # seconds

    start = -10.0
    stop  = +1.0
    step  = 1.0

    setpoints = list(np.arange(start, stop + step, step))
    measurements = {v: [] for v in setpoints}

    instruments["2400"] = K2400(
        rm,
        'TCPIP::192.168.0.5::gpib0,24',
        title='Keithley 2400'
    )

    smu = instruments["2400"]
    smu.set_source_type("VOLT")
    smu.instr.write(":SENSe:CURRent:NPLCycles 10")
    smu.set_voltage_compliance(0.1)
    smu.set_source_current_range(0.001)
    smu.set_current_compliance(0.0006)
    smu.set_output_on()
    time.sleep(10)

    for run in range(runs):
        logging.info(f"Run {run + 1} of {runs}")
        randomized_setpoints = setpoints.copy()
        random.shuffle(randomized_setpoints)

        for counter, voltage in enumerate(randomized_setpoints, start=1):

            smu.set_source_voltage(voltage)
            time.sleep(settling_time)
            reply = smu.instr.query(":READ?").split(',') # returns string voltage,current,....
            current = float(reply[1])
            measurements[voltage].append(current)

            logging.info(
                f"{counter:02}/{len(setpoints)} "
                f"Vset={voltage:+e} V "
                f"Imeas={current:+e} A"
            )

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{name}_{timestamp}.csv"

    num_runs = max(len(v) for v in measurements.values())
    header = ["Setpoint_V"] + [f"Run {i + 1}" for i in range(num_runs)]

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for setpoint in sorted(measurements.keys()):
            row = [float(setpoint)] + measurements[setpoint]
            writer.writerow(row)
    smu.set_output_off()
    
current_source_output_impedance_test()
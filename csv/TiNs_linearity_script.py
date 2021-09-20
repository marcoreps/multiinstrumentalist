#!/usr/bin/python
import sys
import vxi11
import time
import numpy as np

log_name = "dcl_10vdc_5720_3458ab_abe26_nplc100_soak5_aug2021.csv"

fluke = vxi11.Instrument("192.168.178.88", "gpib0,1")
fluke.timeout = 30*1000
#fluke.clear()
fluke.write("*IDN?")
print ("Source detected = %s" % fluke.read())

dmm = vxi11.Instrument("192.168.178.88", "gpib0,22")# Keysight 3458A, GPIB Address = 22
dmm = timeout = 30*1000
dmm2 = vxi11.Instrument("192.168.178.88", "gpib0,23")# Keysight 3458A, GPIB Address = 22
dmm2 = timeout = 30*1000
dmm.clear()
dmm.write("ID?")
print ("DUT1 detected = %s" % dmm.read())

fluke.write("STBY")
fluke.write("RANGELCK OFF")
fluke.write("OUT 10 V, 0 Hz")
fluke.write("RANGELCK ON")
fluke.write("STBY")
fluke.write("OUT 0.0 V, 0 Hz")
fluke.write("EXTGUARD OFF")
fluke.write("OPER")
time.sleep(2)
print ("SRC configured")
dmm.write("BEEP")
dmm.write("END ALWAYS")
dmm.write("DCV 10")
dmm.write("NPLC 100")
dmm.write("NDIG 8")
dmm.write("TRIG AUTO")
dmm.write("MATH OFF")
print ("DUT configured, starting ACAL")
dmm2.write("BEEP")
dmm2.write("END ALWAYS")
dmm2.write("DCV 10")
dmm2.write("NPLC 100")
dmm2.write("NDIG 8")
dmm2.write("TRIG AUTO")
dmm2.write("MATH OFF")
print ("DUT configured, starting ACAL")

dmm.write("TARM SGL")
dmm.read()
dmm.write("MATH NULL")
dmm.write("TARM SGL") # Get reading
dmm.read()
dmm2.write("TARM SGL")
dmm2.read()
dmm2.write("MATH NULL")
dmm2.write("TARM SGL") # Get reading
dmm2.read()
print ("DUTs is nulled to MFC zero")

with open(log_name, 'a') as dile:
    dile.write ("date;source;duta;dutb;dutc;dutd;sdev;sdev2;sdev3;sdev4;temp;temp2\r\n")
dile.close()

vcnt = 0 # temporary counter
print ("Log into %s started" % log_name)

for i in range(-109,110,1):
    median = 0.0
    rrsdev = 0.0
    array = []
    median2 = 0.0
    sdev2 = 0.0
    array2 = []
    median3 = 0.0
    sdev3 = 0.0
    array3 = []
    median4 = 0.0
    sdev4 = 0.0
    array4 = []
    set_value = (float(i) / 10)
    fluke.write("OUT %.7f;OPER" % set_value)
    fluke.write("OPER")
    time.sleep(5)
    for ix in range (0,4): #take more samples
        dmm.write("TARM SGL")
        dmm2.write("TARM SGL")
        val = float(dmm.read())
        val2 = float(dmm2.read())
        array.extend([val])
        array2.extend([val2])
        array3.extend([val3])
        array4.extend([val4])
        if abs(set_value) >= 0.0005:
            print("\033[33;1mA %.8f, ppm %.4f \033[35;1mB %.8f, ppm %.4f \033[37;1mC %.8f, ppm %.4f \033[32;1mD %.8f, ppm %.4f\033[39;0m" % (val, ((val / set_value - 1) * 1e6), val2,((val2 /set_value - 1) * 1e6), val3,((val3 / set_value - 1) * 1e6),val4,((val4 / set_value - 1) * 1e6) ))
            if (abs(val) >= 9.9e36) or (abs(val2) >= 9.9e36):
                print ("Smoke escaped, check connections")
                fluke.write("OUT 0 V")
                fluke.write("STBY")
                quit()
    sdev = np.std(array[1:])
    median = np.median(array[1:])
    sdev2 = np.std(array2[1:])
    median2 = np.median(array2[1:])
    sdev3 = np.std(array3[1:])
    median3 = np.median(array3[1:])
    sdev4 = np.std(array4[1:])
    median4 = np.median(array4[1:])
    if abs(float(i) / 10) >= 0.0005:
        dev1 = ((median / set_value - 1) * 1e6)
        dev2 = ((median2 /set_value - 1) * 1e6)
        dev3 = ((median3 /set_value - 1) * 1e6)
        dev4 = ((median4 /set_value - 1) * 1e6)
        print("\033[32;1mSRC %.4f \033[33;1mA %.9f, sdev5 = %.3f uV, med5 = %.8f\033[35;1mB %.9f, sdev5 = %.3f uV, med5 = %.8f \033[34;1m Delta %.4f ppm \033[37;1mC %.9f, sdev5 = %.3f uV, med5 = %.8f\033[32;1m D %.9f, sdev5 = %.3f uV, med5 = %.8f\033[39;0m" % (set_value, val, sdev*1e6, median, val2,sdev2*1e6, median2, (dev1 - dev2),  val3,sdev3*1e6, median3, val4,sdev4*1e6, median4 ))
        dmm.write("DISP MSG,'%5.3f %2.1fV" % (dev1,set_value ))
        dmm2.write("DISP MSG,'%5.3f %2.1fV" % (dev2,set_value ))
    dmm.write("TEMP?")
    temp = float(dmm.read())
    dmm2.write("TEMP?")
    temp2 = float(dmm2.read())
    with open(log_name, 'a') as dile:
        dile.write (time.strftime("%m%d%Y-%H:%M:%S;") + ("%.9f;%.9f;%.9f;%.9f;%.9f;%.6g;%.6g;%.6g;%.6g;%.1f;%.1f\r\n" % (set_value, median, median2, median3, median4, sdev, sdev2, sdev3, sdev4, temp, temp2)))
    dile.close()

fluke.write("OUT 0 V")
fluke.write("STBY")
fluke.write("RANGELCK OFF")
dmm.write("RESET")
dmm2.write("RESET")

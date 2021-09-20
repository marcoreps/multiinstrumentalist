import numpy as np
import matplotlib.pyplot as plt

# Array from .csv
arra=np.genfromtxt('https://raw.githubusercontent.com/marcoreps/multiinstrumentalist/master/csv/20210920-105659_3458A_INL.csv',delimiter=',',skip_header=1)

# Columns to lists
F5700A = [row[0] for row in arra]
HP3458A = [row[1] for row in arra]
PPMdeviationa = [(F5700A[x]-HP3458A[x])/(10/1000000) for x in range(len(HP3458A))]

figa, axa = plt.subplots()
axa.plot(F5700A, PPMdeviationa, label='absolute')
axa.set_xlabel('Calibrator Vout')
axa.set_ylabel('PPM of 10V range')
axa.set_title("3458A INL test")
figa.set_size_inches(16, 9)


# Fit a polynomial function of degree 1
termsa = np.polyfit(F5700A, PPMdeviationa, 1)

# Create a function with the terms we just generated
polyfunctiona = np.poly1d(termsa)

bestfita = [PPMdeviationa[x]-polyfunctiona(F5700A[x]) for x in range(len(HP3458A))]

# Plot a little test
axa.plot(F5700A, bestfita, label='best fit')
axa.legend()







# Array from .csv
arrb=np.genfromtxt('https://raw.githubusercontent.com/marcoreps/multiinstrumentalist/master/csv/20210920-112122_3458B_INL.csv',delimiter=',',skip_header=1)

# Columns to lists
F5700B = [row[0] for row in arrb]
HP3458B = [row[1] for row in arrb]
PPMdeviationb = [(F5700A[x]-HP3458B[x])/(10/1000000) for x in range(len(HP3458B))]

figb, axb = plt.subplots()
axb.plot(F5700A, PPMdeviationb, label='absolute')
axb.set_xlabel('Calibrator Vout')
axb.set_ylabel('PPM of 10V range')
axb.set_title("3458B INL test")
figb.set_size_inches(16, 9)

print("3458B best fit:")
# Fit a polynomial function of degree 1
termsb = np.polyfit(F5700B, PPMdeviationb, 1)

# Create a function with the terms we just generated
polyfunctionb = np.poly1d(termsb)

bestfitb = [PPMdeviationb[x]-polyfunctionb(F5700B[x]) for x in range(len(HP3458B))]

# Plot a little test
axb.plot(F5700B, bestfitb, label='best fit')
axb.legend()


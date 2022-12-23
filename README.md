# multiinstrumentalist
Multi instrument datalogging platform

Not yet cleaned up for external use, good luck!

sudo apt-get update

( sudo raspi-config to enable i2c )

sudo apt-get install python3-pip i2c-tools git

pip install python-vxi11 numpy smbus2 sparkfun-qwiic-ccs811 influxdb-client

git clone https://github.com/marcoreps/multiinstrumentalist.git

cd multiinstrumentalist/

python3 main.py

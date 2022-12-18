#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser

from influxdb_client import InfluxDBClient

config = configparser.ConfigParser()
config.read('influx_login.ini')

# create someting like this as influx_login.ini
# [DEFAULT]
# url = http://localhost:8086
# bucket = PPMhub
# org = RPG
# token = changemechangemechangemechangeme


client = InfluxDBClient(url=config['DEFAULT']['url'], token=config['DEFAULT']['token'], org=config['DEFAULT']['org'])


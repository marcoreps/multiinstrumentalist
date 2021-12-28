#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

from influxdb import InfluxDBClient
from influxdb import SeriesHelper


host = 'localhost'
port = 8086
user = 'grafana'
password = 'grafana'
dbname = 'home'

myclient = InfluxDBClient(host, port, user, password, dbname)

class MySeriesHelper(SeriesHelper):
    """Instantiate SeriesHelper to write points to the backend."""

    class Meta:
        """Meta class stores time series helper configuration."""

        # The client should be an instance of InfluxDBClient.
        client = myclient

        # The series name must be a string. Add dependent fields/tags
        # in curly brackets.
        series_name = '{instrument_name}'

        # Defines all the fields in this time series.
        fields = ['value']

        # Defines all the tags for the series.
        tags = ['instrument_name']

        # Defines the number of data points to store prior to writing
        # on the wire.
        bulk_size = 10

        # autocommit must be set to True when using bulk_size
        autocommit = True
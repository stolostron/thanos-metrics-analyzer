#!/bin/bash
export TOLERANCE=3
export METRIC_DAYS=10
export RESOLUTION=20m
export LOGROOT=./logs
export BATCH_SIZE=4
export GRAFANA_DASHBOARD_UID="85a562078cdf77779eaa1add43ccec1e"
rm -rf ./logs
python start.py 

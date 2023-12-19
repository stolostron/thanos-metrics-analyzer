#!/bin/bash
export TOLERANCE=10
export METRIC_DAYS=1
export RESOLUTION=20m
export LOGROOT=./logs
export BATCH_SIZE=1
export RECOMMENDER_TYPE=workload
export GRAFANA_DASHBOARD_UID="85a562078cdf77779eaa1add43ccec1e"
rm -rf ./logs
python start.py 

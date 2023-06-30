#!/bin/bash
export TOLERANCE=3
export METRIC_DAYS=10
export RESOLUTION=20m
export LOGROOT=./logs
export BATCH_SIZE=4
rm -rf ./logs
python start.py 

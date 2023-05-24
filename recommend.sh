#!/bin/bash
export TOLERANCE=3
export METRIC_DAYS=10
export RESOLUTION=20m
rm -rf ./logs
python start.py 

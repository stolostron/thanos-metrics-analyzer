import json
import os
from promethus import *
from logger import *
from Worker2 import *
from datetime import datetime, timedelta


import warnings
warnings.filterwarnings("ignore")

end_date = datetime.now()
days_delta = int(os.environ.get('METRIC_DAYS','1'))

start_date = end_date - timedelta(days=days_delta - 1)
print("Metrics from " ,start_date-timedelta(days=1), "is used to compute recommendation")
tolerance=int(os.environ.get('TOLERANCE', '0'))

def process_input():
    MainLogger.info("Starting processing of input file ")
    input_file='thanos.json'
    file_present=os.path.isfile(input_file)
    assert file_present ,f"Input file not found {input_file}"
    MainLogger.info("Found input file "+input_file)
    f=open(input_file)  
    thanos_endpoints = json.load(f)
    endpoint_list=thanos_endpoints['thanos_endpoints']
    # Iterating through each thanos end point
    for idx,item in enumerate(endpoint_list):
        MainLogger.info("Connecting to thanos server number %s : url:  %s",idx+1 ,item['url'])
        conn = PromClient(item['url'],item['token']).get_thanos_client()
        if conn is None:
            MainLogger.error("Connection to Thanos server failed, url : %s",item['url'])
        else:
            MainLogger.info("Connection to Thanos server success, url : %s",item['url'])
            worker=Worker2(conn,idx+1,item)
            worker.process_metric_data(start_date, end_date, tolerance)
  
    # Close file
    f.close()
    return

    
def main():
    process_input()

if __name__ == '__main__':
     main()

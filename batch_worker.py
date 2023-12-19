from prometheus_api_client import *
import csv
from constant import *
from logger import *
from namespace_recommender import NamespaceRecommender
from queries import *
from pandas import DataFrame,concat,date_range
from timeit import default_timer as timer
from datetime import datetime

from workload_recommender import WorkloadRecommender

GB_FACTOR = 1e9


class batch_worker(object):
    def __init__(self, prom_conn, name, recommender_type, endpoint, grafana_dashboard_uid, start_date, end_date, tolerance, batch_size):
        self.p_client=prom_conn
        self.name=name
        self.recommender_type = recommender_type
        self.endpoint=endpoint
        self.grafana_dashboard_uid=grafana_dashboard_uid
        self.endpointLogger = Logger("endpoint"+name,formatter,logPath).get_logger(name+".log",logging.INFO)
        self.start_date = start_date 
        self.end_date = end_date 
        self.tolerance = tolerance 
        self.batch_size = batch_size

    def start_process_metric_data(self):
        if self.recommender_type == WORKLOAD_RECOMMENDER_TYPE:
            recommender = WorkloadRecommender(self.name, self.p_client, self.endpoint, self.grafana_dashboard_uid, self.start_date, self.end_date, self.tolerance, self.batch_size)
        else:
            recommender = NamespaceRecommender(self.name, self.p_client, self.endpoint, self.grafana_dashboard_uid, self.start_date, self.end_date, self.tolerance, self.batch_size)

        recommender.recommend()

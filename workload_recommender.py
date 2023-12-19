

from recommender import Recommender
from queries import *


class WorkloadRecommender(Recommender):

    key = ["cluster", "namespace", "workload"]
    requestQuery = RESOURCE_REQUEST_WORKLOAD
    cpuMaxQuery = CPU_USAGE_MAX_WORKLOAD
    memoryMaxQuery = MEMORY_USAGE_MAX_WORKLOAD


    def __init__(self, name, prometheus_connection, endpoint, grafana_dashboard_uid, start_date, end_date, tolerance, batch_size) -> None:
        super().__init__(name, prometheus_connection, endpoint, grafana_dashboard_uid, start_date, end_date, tolerance, batch_size)

    def recommend(self):
        return super().recommend()
    

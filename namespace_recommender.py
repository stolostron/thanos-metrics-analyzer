from recommender import Recommender
from queries import *

class NamespaceRecommender(Recommender):

    key = ["cluster", "namespace"]
    requestQuery = RESOURCE_REQUEST_NAMESPACE
    cpuMaxQuery = CPU_USAGE_MAX_NAMESPACE
    memoryMaxQuery = MEMORY_USAGE_MAX_NAMESPACE

    def __init__(self, name, prometheus_connection, endpoint, grafana_dashboard_uid, start_date, end_date, tolerance, batch_size) -> None:
        super().__init__(name, prometheus_connection, endpoint, grafana_dashboard_uid, start_date, end_date, tolerance, batch_size)

    def recommend(self):
        return super().recommend() 

    
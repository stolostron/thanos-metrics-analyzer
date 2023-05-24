from prometheus_api_client import *
from urllib3.util import Retry
from logger import *


class PromClient(object):
    def __init__(self,url,token):
        self.url=url
        self.token=token
    def get_thanos_client(self):
        MainLogger.info("Creating client for url %s",self.url)
        try:
            pc = PrometheusConnect(url=self.url, headers={"Authorization": "Bearer {}".format(self.token)}, disable_ssl=True)
            q="cluster_version{}" 
            metrics = pc.custom_query(query=q)
        except Exception as e:
            MainLogger.info("Error creating connection for %s",self.url)
            return None
        return pc
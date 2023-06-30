from prometheus_api_client import *
import csv
from logger import *
from queries import *
from pandas import DataFrame,concat,date_range
from timeit import default_timer as timer
from datetime import datetime

GB_FACTOR = 1e9
class batch_worker(object):
    def __init__(self,prom_conn,name,endpoint):
        self.p_client=prom_conn
        self.name=name
        self.endpoint=endpoint
        self.endpointLogger = Logger("endpoint"+name,formatter,logPath).get_logger(name+".log",logging.INFO)

    def get_metric_data(self,query,batch_ids, epoch: int = None):
        self.endpointLogger.info("--------------Begin------------------")
        print("Querying Metric for clusters : " + batch_ids)
        parameters = {"query": query}
        if epoch:
            # For range date, values before epoch is considered for aggregation
            parameters.update({"params": {"time": epoch}})
        start = timer()
        metric_data = self.p_client.custom_query(**parameters)
        end = timer()
        self.endpointLogger.info("finished running quey: %s" , str(parameters["query"]))
        if epoch:
            date_time = datetime.fromtimestamp(int(epoch))
            self.endpointLogger.info("metrics queried for one day with time %s" , date_time)

        self.endpointLogger.info("time to run query: %s", end-start)
        if end-start > 250:
            self.endpointLogger.info("Warning ,query taking more than 250s: %s", end-start)

        self.endpointLogger.info("---------------End-------------------")
        df= DataFrame(
            [
                {**item["metric"], "value": float(item["value"][1])}
                for item in metric_data
            ]
        )
        return df

    def get_grouped_aggregation(self,df_data_list, agg_func: str = "max"):
        return concat(df_data_list).groupby(
            [ID_LABEL, "namespace"]
        ).agg(agg_func).reset_index()

    def get_merged_data(self,df_data1, df_data2):
        return df_data1.merge(df_data2, on=[ID_LABEL, "namespace"], how="left")
    
    def get_request_data_batch(self,end_date, cluster_ids_filter):
        df_request_data = self.process_metrics_batch(
            RESOURCE_REQUEST, cluster_ids_filter, end_date.strftime("%s")
        )
        
        df_request_data = df_request_data.pivot(
            index=[ID_LABEL, "namespace"],
            columns="resource",
        ).swaplevel(1, 0, axis=1)
        df_request_data.columns = ["_".join(col) for col in df_request_data.columns]
        df_request_data.memory_value = df_request_data.memory_value / GB_FACTOR

        return df_request_data
    
    def get_usage_data_batch(self,start_date, end_date, cluster_ids_filter):
        cpu_usage_max = []
        memory_usage_max = []

        for dt in date_range(start_date, end_date):
            epoch = dt.strftime("%s")
            print("Getting usage metrics from date  ", dt.strftime("%d-%m-%Y"))
            cpu_usage_max.append(
                self.process_metrics_batch(CPU_USAGE_MAX, cluster_ids_filter, epoch)
            )
            memory_usage_max.append(
                self.process_metrics_batch(MEMORY_USAGE_MAX, cluster_ids_filter, epoch)
            )

        df_cpu_usage_max = self.get_grouped_aggregation(cpu_usage_max, "max")
        df_memory_usage_max = self.get_grouped_aggregation(memory_usage_max, "max")

        df_memory_usage_max.value = df_memory_usage_max.value / GB_FACTOR
        
        return df_cpu_usage_max, df_memory_usage_max

    
    def process_metrics_batch(self,query, cluster_ids, end_date):
        return concat(
            [
                self.get_metric_data(
                    query.replace("CLUSTER_FILTER", batch_ids),
                    batch_ids,
                    end_date
                )
                for batch_ids in cluster_ids
            ]
        )
    
    def get_cluster_id_batch(self,end_date, batch_size):
        cluster_ids = self.get_metric_data(CLUSTER_IDS, end_date.strftime("%s"))[ID_LABEL].unique()
        print("Reading clusters of batch size : "+ str(batch_size))
        result = [
            "|".join(cluster_ids[pos:pos + batch_size])
            for pos in range(0, len(cluster_ids), batch_size)
        ]
        return result
    
    def process_metric_data(self,start_date, end_date, tolerance,batch_size):
        MainLogger.info("Working on endpoint %s " , self.endpoint) 
        cluster_ids_batch = self.get_cluster_id_batch(end_date, batch_size)
        df_request_data = self.get_request_data_batch(end_date, cluster_ids_batch)
        (
            df_cpu_usage_max,
            df_memory_usage_max
        ) = self.get_usage_data_batch(start_date, end_date,cluster_ids_batch)

        # Rename columns
        df_request_data.rename(
            columns={"cpu_value": "cpu_request", "memory_value": "memory_request"},
            inplace=True
        )
        df_cpu_usage_max.rename(columns={"value": "cpu_usage_max"}, inplace=True)
        df_memory_usage_max.rename(columns={"value": "memory_usage_max"}, inplace=True)

        # Merge dataframe
        df_merged = self.get_merged_data(df_request_data, df_cpu_usage_max)
        df_merged = self.get_merged_data(df_merged, df_memory_usage_max)


        df_merged["cpu_ratio"] = df_merged.cpu_usage_max / df_merged.cpu_request
        df_merged["memory_ratio"] = df_merged.memory_usage_max / df_merged.memory_request
        df_merged["cpu_delta"] =  df_merged.cpu_request - df_merged.cpu_usage_max
        df_merged["memory_delta"] = df_merged.memory_request - df_merged.memory_usage_max
        df_merged["cpu_recommendation"] =  df_merged.cpu_usage_max * (1 + tolerance / 100)
        df_merged["memory_recommendation"] = df_merged.memory_usage_max * (1 + tolerance / 100)
        
        
        self.endpointLogger.info("Output for endpoint %s : %s",self.name,self.endpoint)
        # Sort By Delta
        df_merged.drop(columns=['ephemeral_storage_value'],errors='ignore',inplace=True)
        df_merged.sort_values(by=['cpu_delta','memory_delta'],ascending=False,na_position="last",inplace=True)
        df_merged['grafana_url'] = self.endpoint['url'].replace("rbac-query-proxy","grafana")
        print("Top 5 recommendations for clusters in:",self.endpoint['url'])
        print(df_merged.head(5))
        print("Processed metrics from ",df_merged.cluster.nunique(),"clusters ")
        outFile=logPath+self.name+'.csv'
        MainLogger.info("Started writing output csv : %s ", outFile)
        df_merged.to_csv(outFile)
        MainLogger.info("Completed writing output csv : %s ", outFile)     
        #return df_merged
  



   
    

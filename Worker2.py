from prometheus_api_client import *
import csv
from logger import *
from queries import *
from pandas import DataFrame,concat,date_range
GB_FACTOR = 1e9
class Worker2(object):
    def __init__(self,prom_conn,idx,endpoint):
        self.p_client=prom_conn
        self.idx=idx
        self.endpoint=endpoint
        self.endpointLogger = Logger("endpoint"+str(idx),formatter,logPath).get_logger(str(idx)+".log",logging.INFO)

    def get_metric_data(self,query, epoch: int = None):
        parameters = {"query": query}
        if epoch:
            # For range date, values before epoch is considered for aggregation
            parameters.update({"params": {"time": epoch}})
        metric_data = self.p_client.custom_query(**parameters)
        self.endpointLogger.info("get_metric_data %s" , str(parameters))
        metric_data = self.p_client.custom_query(**parameters)
        return DataFrame(
            [
                {**item["metric"], "value": float(item["value"][1])}
                for item in metric_data
            ]
        )
    def get_grouped_aggregation(self,df_data_list, agg_func: str = "max"):
        return concat(df_data_list).groupby(
            [ID_LABEL, "namespace"]
        ).agg(agg_func).reset_index()

    def get_merged_data(self,df_data1, df_data2):
        return df_data1.merge(df_data2, on=[ID_LABEL, "namespace"], how="left")

    def get_request_data(self,end_date):
        df_request_data = self.get_metric_data(RESOURCE_REQUEST, end_date.strftime("%s"))

        df_request_data = df_request_data.pivot(
        index=[ID_LABEL, "namespace"],
        columns="resource",
        ).swaplevel(1, 0, axis=1)

        df_request_data.columns = ["_".join(col) for col in df_request_data.columns]
        df_request_data.memory_value = df_request_data.memory_value / GB_FACTOR

        return df_request_data

    def get_usage_data(self,start_date, end_date):
        cpu_usage_max = []
        memory_usage_max = []
        cpu_usage_avg = []
        memory_usage_avg = []

        for dt in date_range(start_date, end_date):
            epoch = dt.strftime("%s")
            #print("dt",dt)
            #print("epoch" ,epoch)

            cpu_usage_max.append(self.get_metric_data(CPU_USAGE_MAX, epoch))
            memory_usage_max.append(self.get_metric_data(MEMORY_USAGE_MAX, epoch))
            cpu_usage_avg.append(self.get_metric_data(CPU_USAGE_AVG, epoch))
            memory_usage_avg.append(self.get_metric_data(MEMORY_USAGE_AVG, epoch))

        df_cpu_usage_max = self.get_grouped_aggregation(cpu_usage_max, "max")
        df_memory_usage_max = self.get_grouped_aggregation(memory_usage_max, "max")
        df_cpu_usage_avg = self.get_grouped_aggregation(cpu_usage_avg, "mean")
        df_memory_usage_avg = self.get_grouped_aggregation(memory_usage_avg, "mean")

        df_memory_usage_max.value = df_memory_usage_max.value / GB_FACTOR
        df_memory_usage_avg.value = df_memory_usage_avg.value / GB_FACTOR
        
        return df_cpu_usage_max, df_memory_usage_max, df_cpu_usage_avg, df_memory_usage_avg

    def process_metric_data(self,start_date, end_date, tolerance):
        MainLogger.info("Working on endpoint %s " , self.endpoint) 
        df_request_data = self.get_request_data(end_date)
        (
            df_cpu_usage_max,
            df_memory_usage_max,
            df_cpu_usage_avg,
            df_memory_usage_avg
        ) = self.get_usage_data(start_date, end_date)

        # Rename columns
        df_request_data.rename(
            columns={"cpu_value": "cpu_request", "memory_value": "memory_request"},
            inplace=True
        )
        df_cpu_usage_max.rename(columns={"value": "cpu_usage_max"}, inplace=True)
        df_memory_usage_max.rename(columns={"value": "memory_usage_max"}, inplace=True)
        df_cpu_usage_avg.rename(columns={"value": "cpu_usage_avg"}, inplace=True)
        df_memory_usage_avg.rename(columns={"value": "memory_usage_avg"}, inplace=True)

        # Merge dataframe
        df_merged = self.get_merged_data(df_request_data, df_cpu_usage_max)
        df_merged = self.get_merged_data(df_merged, df_memory_usage_max)
        df_merged = self.get_merged_data(df_merged, df_cpu_usage_avg)
        df_merged = self.get_merged_data(df_merged, df_memory_usage_avg)

        df_merged["cpu_ratio"] = df_merged.cpu_usage_max / df_merged.cpu_request
        df_merged["memory_ratio"] = df_merged.memory_usage_max / df_merged.memory_request
        df_merged["cpu_delta"] =  df_merged.cpu_request - df_merged.cpu_usage_max
        df_merged["memory_delta"] = df_merged.memory_request - df_merged.memory_usage_max
        df_merged["cpu_recommendation"] =  df_merged.cpu_usage_max * (1 + tolerance / 100)
        df_merged["memory_recommendation"] = df_merged.memory_usage_max * (1 + tolerance / 100)
        
        
        self.endpointLogger.info("Output for endpoint %s : %s",self.idx,self.endpoint)
        # Sort By Delta
        df_merged.drop(columns=['ephemeral_storage_value'],errors='ignore',inplace=True)
        df_merged.sort_values(by=['cpu_delta','memory_delta'],ascending=False,na_position="last",inplace=True)
        df_merged['grafana_url'] = self.endpoint['url'].replace("rbac-query-proxy","grafana")
        print("Top 5 recommendations for clusters in:",self.endpoint['url'])
        print(df_merged.head(5))
        outFile=logPath+str(self.idx)+'.csv'
        MainLogger.info("Started writing output csv : %s ", outFile)
        df_merged.to_csv(outFile)
        MainLogger.info("Completed writing output csv : %s ", outFile)     
        #return df_merged
  



   
    

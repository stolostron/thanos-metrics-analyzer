from prometheus_api_client import *
import csv
from logger import *
from queries import *
from pandas import DataFrame,concat,date_range
from timeit import default_timer as timer
from datetime import datetime

GB_FACTOR = 1e9


class batch_worker(object):
    def __init__(self,prom_conn,name,endpoint,grafana_dashboard_uid):
        self.p_client=prom_conn
        self.name=name
        self.endpoint=endpoint
        self.grafana_dashboard_uid=grafana_dashboard_uid
        self.endpointLogger = Logger("endpoint"+name,formatter,logPath).get_logger(name+".log",logging.INFO)
        self._namespace_filter = self._get_namespace_filter()

    def _get_namespace_filter(self):
        """Get update namespace filter condition required for the query."""
        namespace_filter_str = "namespace!=''"
        namespace_filter = self.endpoint.get("namespace_filter", None)

        label_filter = self.endpoint.get("label_filter", None)

        namespaces = []
        #Default to use namespace label filter if available.
        if label_filter != None:
            
            # Get action for filter (either exclude or include)
            filter_action = label_filter.get("action", "value")
            if filter_action == "exclude":
                action = "!~"
            elif filter_action == "include":
                action = "=~"
            else:
                self.endpointLogger.error(
                    "Only exclude/include actions are allowed for label filter."
                    f" Using filter {label_filter}"
                )

            #Access labels from endpoint:
            for name, value in label_filter.get("labels", "values").items():
                if isinstance(value, list):
                    concatenate_value = "|".join(value)
                    label_filter_prom = f'label_{name}{action}"{concatenate_value}"'
                    namespaces.append(self.get_namespace_from_labels(label_filter_prom))
                else:
                    label_filter_prom = f'label_{name}{action}"{value}"'
                    namespaces.append(self.get_namespace_from_labels(label_filter_prom))


            namespaces = "|".join(namespaces)
            namespace_filter_str = f'namespace{action}"{namespaces}"'


        # If namespace labels not available, check for namespace filter
        elif namespace_filter !=None:
            namespaces = "|".join(namespace_filter.get("namespaces", []))
            filter_action = namespace_filter.get("action", "exclude")
            if filter_action == "exclude":
                namespace_filter_str = f"namespace!~'{namespaces}'"
            elif filter_action == "include":
                namespace_filter_str = f"namespace=~'{namespaces}'"
            else:
                self.endpointLogger.error(
                    "Only exclude/include actions are allowed for namespace filter."
                    f" Using filter {namespace_filter_str}"
                )

        return namespace_filter_str
        
    # Function to query prom with label filters obtained from user to get the namespaces associated with labels:
    def get_namespace_from_labels(self, label_filter_prom):
            label_query = NAMESPACE_LABELS.replace("LABEL_FILTER", label_filter_prom)
            result = self.p_client.custom_query(label_query)
            for data in result:
                return f"{data['metric']['namespace']}"
        
    
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

        self.endpointLogger.info("time to run query: %s seconds", end-start)
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
        ).agg({"value": agg_func, "dummy_counter": "sum"}).reset_index()

    def get_merged_data(self,df_data1, df_data2):
        return df_data1.merge(df_data2, on=[ID_LABEL, "namespace"], how="left")
    
    def get_request_data_batch(self,end_date, cluster_ids_filter):
        resource_req_query = RESOURCE_REQUEST.replace(
            "NAMESPACE_FILTER", self._namespace_filter
        )
        df_request_data = self.process_metrics_batch(
            resource_req_query, cluster_ids_filter, end_date.strftime("%s"), False
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
        cpu_usage_query = CPU_USAGE_MAX.replace(
            "NAMESPACE_FILTER", self._namespace_filter
        )
        mem_usage_query = MEMORY_USAGE_MAX.replace(
            "NAMESPACE_FILTER", self._namespace_filter
        )

        for dt in date_range(start_date, end_date):
            epoch = dt.strftime("%s")
            print("Getting usage metrics from date  ", dt.strftime("%d-%m-%Y"))
            cpu_usage_max.append(
                self.process_metrics_batch(cpu_usage_query, cluster_ids_filter, epoch)
            )
            memory_usage_max.append(
                self.process_metrics_batch(mem_usage_query, cluster_ids_filter, epoch)
            )

        df_cpu_usage_max = self.get_grouped_aggregation(cpu_usage_max, "max")
        df_memory_usage_max = self.get_grouped_aggregation(memory_usage_max, "max")

        df_memory_usage_max.value = df_memory_usage_max.value / GB_FACTOR
        
        return df_cpu_usage_max, df_memory_usage_max

    
    def process_metrics_batch(self,query, cluster_ids, end_date, add_dummy: bool = True):
        df_metric_data = concat(
            [
                self.get_metric_data(
                    query.replace("CLUSTER_FILTER", batch_ids),
                    batch_ids,
                    end_date
                )
                for batch_ids in cluster_ids
            ]
        )
        if add_dummy:
            df_metric_data["dummy_counter"] = 1
        return df_metric_data
    
    def get_cluster_id_batch(self, end_date, batch_size):
        cluster_ids = self.get_metric_data(CLUSTER_IDS, end_date.strftime("%s"))[ID_LABEL].unique()
        print("Reading clusters of batch size : "+ str(batch_size))
        result = [
            "|".join(cluster_ids[pos:pos + batch_size])
            for pos in range(0, len(cluster_ids), batch_size)
        ]
        return result
    
    def get_grafana_url_for_namespace(self, df):
        return f"""{df['grafana_url']}/d/{self.grafana_dashboard_uid}/
        kubernetes-compute-resources-namespace-pods?var-datasource=Observatorium&
        var-cluster=local-cluster&var-namespace={df['namespace']}"""
    
    
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

        df_merged["cpu_recommendation_request"] = df_merged.cpu_usage_max * (1 + tolerance / 100)
        df_merged["memory_recommendation_request"] = df_merged.memory_usage_max * (1 + tolerance / 100)
        df_merged["cpu_recommendation_limit"] = df_merged["cpu_recommendation_request"]
        df_merged["memory_recommendation_limit"] = df_merged["memory_recommendation_request"]

        df_merged["days_active"] = df_merged[
            ["dummy_counter_x", "dummy_counter_y"]
        ].fillna(0).apply(min, axis=1)
        df_merged.drop(columns=["dummy_counter_x", "dummy_counter_y"], inplace=True)
        
        self.endpointLogger.info("Output for endpoint %s : %s",self.name,self.endpoint)
        # Sort By Delta
        df_merged.drop(columns=['ephemeral_storage_value'],errors='ignore',inplace=True)
        df_merged.sort_values(by=['cpu_delta','memory_delta'],ascending=False,na_position="last",inplace=True)
        df_merged['grafana_url'] = self.endpoint['url'].replace("rbac-query-proxy","grafana")
        df_merged['grafana_url'] = df_merged.apply(self.get_grafana_url_for_namespace, axis=1)

        print("Top 5 recommendations for clusters in:",self.endpoint['url'])
        print(df_merged.head(10))
        print("Processed metrics from ",df_merged.cluster.nunique(),"clusters ")
        outFile=logPath+self.name+'.csv'
        MainLogger.info("Started writing output csv : %s ", outFile)
        df_merged.to_csv(outFile)
        MainLogger.info("Completed writing output csv : %s ", outFile)     
        #return df_merged
  

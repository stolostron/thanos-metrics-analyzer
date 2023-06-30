import os

ID_LABEL = "cluster"

GB_FACTOR = 1e9

resolution=os.environ.get('RESOLUTION', '10m')
# Queries

CLUSTER_IDS = "cluster_version" 

RESOURCE_REQUEST = f"""
    sum by ({ID_LABEL}, namespace, resource)
    (kube_pod_container_resource_requests:sum{{{ID_LABEL}=~'CLUSTER_FILTER', namespace!=''}})
"""
CPU_USAGE_MAX = f"""
    max_over_time(
      sum by ({ID_LABEL}, namespace)
      (node_namespace_pod_container:container_cpu_usage_seconds_total:sum{{{ID_LABEL}=~'CLUSTER_FILTER', namespace!=''}})[1d:{resolution}]
    )
"""
CPU_USAGE_AVG = f"""
    avg_over_time(
      sum by ({ID_LABEL}, namespace)
      (node_namespace_pod_container:container_cpu_usage_seconds_total:sum{{{ID_LABEL}=~'CLUSTER_FILTER', namespace!=''}})[1d:{resolution}]
    )
"""
MEMORY_USAGE_MAX = f"""
    max_over_time(
      sum by ({ID_LABEL}, namespace)
      (container_memory_working_set_bytes{{{ID_LABEL}=~'CLUSTER_FILTER', namespace!=''}})[1d:{resolution}]
    )
"""
MEMORY_USAGE_AVG = f"""
    avg_over_time(
      sum by ({ID_LABEL}, namespace)
      (container_memory_working_set_bytes{{{ID_LABEL}=~'CLUSTER_FILTER', namespace!=''}})[1d:{resolution}]
    )
"""
import os

ID_LABEL = "cluster"

GB_FACTOR = 1e9

resolution=os.environ.get('RESOLUTION', '10m')
# Queries
RESOURCE_REQUEST = f"""
    sum by ({ID_LABEL}, namespace, resource)
    (kube_pod_container_resource_requests:sum)
"""
CPU_USAGE_MAX = f"""
    max_over_time(
      sum by ({ID_LABEL}, namespace)
      (node_namespace_pod_container:container_cpu_usage_seconds_total:sum)[1d:{resolution}]
    )
"""
MEMORY_USAGE_MAX = f"""
    max_over_time(
      sum by ({ID_LABEL}, namespace)
      (container_memory_working_set_bytes)[1d:{resolution}]
    )
"""
# MEMORY_USAGE_MAX = f"""
#     max_over_time(
#       sum by ({ID_LABEL}, namespace)
#       (namespace:container_memory_usage_bytes:sum)[1d:{resolution}]
#     )
# """
CPU_USAGE_AVG = f"""
    avg_over_time(
      sum by ({ID_LABEL}, namespace)
      (node_namespace_pod_container:container_cpu_usage_seconds_total:sum)[1d:{resolution}]
    )
"""
MEMORY_USAGE_AVG = f"""
    avg_over_time(
      sum by ({ID_LABEL}, namespace)
      (container_memory_working_set_bytes)[1d:{resolution}]
    )
"""
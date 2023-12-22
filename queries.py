import os

ID_LABEL = "cluster"

GB_FACTOR = 1e9

resolution=os.environ.get('RESOLUTION', '10m')
# Queries

CLUSTER_IDS = "cluster_version"

RESOURCE_REQUEST_WORKLOAD = f"""
    sum(
      kube_pod_container_resource_requests{{{ID_LABEL}=~'CLUSTER_FILTER', NAMESPACE_FILTER}}
      * on(namespace,pod)
      group_left(workload, workload_type) namespace_workload_pod:kube_pod_owner:relabel{{{ID_LABEL}=~'CLUSTER_FILTER', NAMESPACE_FILTER}}
    ) by ({ID_LABEL}, namespace, workload, resource)
"""

CPU_USAGE_MAX_WORKLOAD = f"""
    max_over_time (
      sum (
        node_namespace_pod_container:container_cpu_usage_seconds_total:sum_rate{{{ID_LABEL}=~'CLUSTER_FILTER', NAMESPACE_FILTER}}
        * on(namespace,pod)
        group_left(workload, workload_type) namespace_workload_pod:kube_pod_owner:relabel{{{ID_LABEL}=~'CLUSTER_FILTER', NAMESPACE_FILTER}}
      ) by ({ID_LABEL}, namespace, workload) [1d:{resolution}]
    )
"""

MEMORY_USAGE_MAX_WORKLOAD = f"""
    max_over_time (
      sum (
        container_memory_working_set_bytes{{{ID_LABEL}=~'CLUSTER_FILTER', NAMESPACE_FILTER}}
        * on(namespace,pod)
        group_left(workload, workload_type) namespace_workload_pod:kube_pod_owner:relabel{{{ID_LABEL}=~'CLUSTER_FILTER', NAMESPACE_FILTER}}
      ) by ({ID_LABEL}, namespace, workload) [1d:{resolution}]
    )
"""

NAMESPACE_LABELS = f"""
    kube_namespace_labels{{LABEL_FILTER}}
"""

RESOURCE_REQUEST_NAMESPACE = f"""
    sum by ({ID_LABEL}, namespace, resource)
    (kube_pod_container_resource_requests:sum{{{ID_LABEL}=~'CLUSTER_FILTER', NAMESPACE_FILTER}})
"""
CPU_USAGE_MAX_NAMESPACE = f"""
    max_over_time(
      sum by ({ID_LABEL}, namespace)
      (node_namespace_pod_container:container_cpu_usage_seconds_total:sum{{{ID_LABEL}=~'CLUSTER_FILTER', NAMESPACE_FILTER}})[1d:{resolution}]
    )
"""
MEMORY_USAGE_MAX_NAMESPACE = f"""
    max_over_time(
      sum by ({ID_LABEL}, namespace)
      (container_memory_working_set_bytes{{{ID_LABEL}=~'CLUSTER_FILTER', NAMESPACE_FILTER}})[1d:{resolution}]
    )
"""

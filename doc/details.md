# Overview
This code can be run on any cluster or desktop as long as it can access to all the ACM hub Thanos which it connects to as defined in [thanos.json](../input/thanos.json).

## Analysis
The system examines for each namespace on each cluster -
1. CPU Usage and Memory Usage over a period of time
1. Measures the `maximum` resource usage over that time period
1. Looks at the sum total of the requests assigned and calculates the delta of total request assigned and usage max.
1. The results are sorted by this delta and saved in CSV.

Note: All pods in the namespace may not have requests assigned.


## Metrics used for analysis
|Type|Metric Name|Remarks|
|---|---|---|
|CPU Usage|node_namespace_pod_container:container_cpu_usage_seconds_total:sum|This is same as `node_namespace_pod_container:container_cpu_usage_seconds_total:sum_irate` . ACM has renamed this metrics to ensure backward compatibility.|
|Memory Usage|container_memory_working_set_bytes||
|CPU Request|kube_pod_container_resource_requests:sum{resource="cpu"}| This is ACM recording rule: `sum(kube_pod_container_resource_requests{container!=""}) by (resource, namespace)`|
|Memory Request|kube_pod_container_resource_requests:sum{resource="memory"}| This is ACM recording rule: `sum(kube_pod_container_resource_requests{container!=""}) by (resource, namespace)`|

## Tolerance
- This represents the buffer over maximum observed consumption included in the recommendation. As an example, if maximum observed memory consumption is 10GB and `tolerance` is set to 10, then the recommendation will be 11GB.
- It can be adjusted in [recommend.sh](../recommend.sh)

## Number of days analyzed
- Currently, the number of days used in analysis defaults to 10 days.
- It can be adjusted in [recommend.sh](../recommend.sh)





# Architecture Overview 

![ACM Right Sizing Architecture Overview](https://github.com/stolostron/thanos-metrics-analyzer/blob/main/data-assets/images/enhanced-dev-preview-architecture.jpg)

The ACM Right Sizing recommendations presented above are calculated with the following approach.
 * Prometheus Recording Rule(PrometheusRule) - We will calculate CPU/Memory capacity/usage at namespace/cluster level using PrometheusRule. It will be used for <=1d aggregation, we won’t be utilizing it for more than 1 day data points due to low data retention (15 days). This rule evaluation runs on each managed cluster.  
 * Records for one day are then forwarded  into each RHACM Hub using [observability-metrics-custom-allowlist](https://access.redhat.com/documentation/en-us/red_hat_advanced_cluster_management_for_kubernetes/2.10/html/observability/customizing-observability#adding-custom-metrics). 
 * We will utilize grafana to calculate 10/30/60 days of aggregated data at runtime 

Below is the screenshot of ACM Right Sizing grafana dashboard. 
![ACM Right Sizing Grafana dashboard](https://github.com/stolostron/thanos-metrics-analyzer/blob/main/data-assets/images/grafana-overview.png)

You can select the cluster you are interested in exploring and view the CPU/memory recommendations, requests, and utilization for different aggregation periods.
# Installation steps 

You can checkout [this](enhanced-dev-preview-installation-steps.md) page for detailed steps on installing ACM Right Sizing components.


# How to Use ?

We have given basic instruction on how you can use grafana [here](enhanced-dev-preview-how-to-use-grafana.md), you can check out for more details.   


# Disclaimer
* Prometheus rules are based on Cluster Name, NOT Cluster ID.
* CPU/Memory Request, Usage and Recommendation are showing Max/Peak values over the (last) selected number of aggregated days.
* As this is an enhanced developer preview, performance issues may occur while loading the Grafana dashboard.
* Currently, we are not back-filling historical data points, so after installing the ACM Right Sizing component, the admin needs to wait for some time.
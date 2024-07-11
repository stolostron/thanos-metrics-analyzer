# Prerequisite 
- Openshift Cluster (Tested with 4.15.13+ version)
- The Advanced Cluster Management operator should be installed on the hub cluster to facilitate cluster administration and data aggregation.
- [MCO](https://github.com/stolostron/multicluster-observability-operator/) should be installed into the hub cluster. 
- `oc` CLI should be installed and configured to interact with Openshift cluster


# Steps to Enable ACM Right Sizing Dev Preview 

For enabling ACM Right Sizing Dev Preview, we need to add Prometheus recording rule as well as [custom allowlist](https://access.redhat.com/documentation/en-us/red_hat_advanced_cluster_management_for_kubernetes/2.10/html/observability/customizing-observability#adding-custom-metrics) to each managed clusters.     

### Step 1: Login into Openshift Cluster

From the terminal, login into ACM hub cluster environment using login command. You can easily get it form the Hub cluster Console UI.  

```
oc login --token=*** --server=***
```

### Step 2: Deploy Policy 

We will utilize [Policy](https://access.redhat.com/documentation/en-us/red_hat_advanced_cluster_management_for_kubernetes/2.10/html/governance/governance#policy-overview) to deploy **Recording rule** as well as **custom allowlist** to each managed clusters. 

We have created sample policy for the Prometheus Recording Rule, you can find it [here](../data-assets/rs-rules-policy.yaml). Using below command you can deploy policy to Hub cluster.  

```
oc apply -f data-assets/rs-rules-policy.yaml
```

You can customize the cluster/namespace filter criteria based on need. Below are sample criteria used in the file where we exclude namespaces that start with `openshift` or `xyz`. Also including namespace where label is `empty` or contains `prod` or `dev` label.

- `namespace!~'openshift.*|xyz.*'`
- `(kube_namespace_labels{label_env=~"prod|dev"} or kube_namespace_labels{label_env=''})`


Similar way you can deploy custom allowlist policy, you can find sample [here](../data-assets/rs-allowlist-policy.yaml)
```
oc apply -f data-assets/rs-allowlist-policy.yaml
```


### Step 3: Adding Policies to PolicySet

Now apply the [Policy Configurations](../data-assets/rs-policyset.yaml) using below command to enable these policies across the fleet.These include the PolicySet, PlacementBinding and the Placement.
```
oc apply -f data-assets/rs-policyset.yaml
```

*Note: In the Placement resource above we are using the clusterCondition when the ManagedClusterConditionAvailable is equal to True. Along with clusterConditions, in the Placement, we can also utilize clusterSelector which can be used to select managed clusters based on label expressions. See example below:*

```
clusterSelector:                            
    matchExpressions:
      - key: hive.openshift.io/managed
        operator: In
        values:
          - true
```
In this example, we define that only clusters with the label `hive.openshift.op/managed=true` should have the policy applied. 

Any new managed cluster will automatically have this policy applied as long as it meets the `clusterSelector` expression.

### Step 4: Deploy Grafana Dashboard

[Here](../data-assets/acm_right_sizing_grafana_dashboard.yaml) is the yaml file that contains configuration of ACM Right-Sizing grafana dashboard. Use the following command to add this dashboard on Grafana. 

```
oc create -f data-assets/acm_right_sizing_grafana_dashboard.yaml
```


### Step 5: Access Grafana Dashboard

Wait for some time for the Prometheus Recording Rules to get triggered, and we will have some data points. You can then go to Grafana and search for the `ACM Right-Sizing Namespace` dashboard. Click on it, and you are ready to use ACM Right Sizing solution.



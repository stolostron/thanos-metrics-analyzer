# thanos-metrics-analyzer

A tool to connect to list of thanos endpoints and compute recommended CPU and memory settings , based on historic usage and resource request.

### Run on your laptop :
   - Have the ./input/thanos.json file updated with your thanos urls and respective tokens
   - Update the ./recommend.sh file with the valid GRAFANA_DASHBOARD_UID. (Default uid is `85a562078cdf77779eaa1add43ccec1e`. The uid is available in the bottom part of the configmap `grafana-dashboard-k8s-compute-resources-namespace-pods`.)
   - run shell script ./recommend.sh

Output : 
   - Go to the logs folder and look for .csv files with recommendations. CSV files are named after the index order of the thanos url.

### Run as a Kubernetes Job :
   - Have the ./charts/job.yaml file updated with your image pull secret
   - Have the ./charts/configmap.yaml file updated with your thanos urls and respective tokens
   - Have the ./charts/pvc.yaml file updated with your storageclass name
   - run `oc apply -f ./charts`

Output :
   - Go to the current date folder in the PVC mount and look for .csv files with recommendations. CSV files are named after the index order of the thanos url.
   - Charts directory include a sleeping pod that can be used to access the PVC mount

For more details to understand on how the system works, proceed [here](doc/details.md)   

# thanos-metrics-analyzer

A tool to connect to list of thanos end points and compute recommended CPU and memory settings , based on historic usage and request.

How to run :
   - Have the thanos.json file updated with your thanos urls and respective tokens
   - run shell script ./recommend.sh

Output : 
   - Go to the logs folder and look for .csv files with recommendations. CSV files are named after the index order of the thanos url.

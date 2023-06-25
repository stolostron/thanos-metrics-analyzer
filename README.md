# thanos-metrics-analyzer

A tool to connect to list of thanos endpoints and compute recommended CPU and memory settings , based on historic usage and resource request.

How to run :
   - Have the ./input/thanos.json file updated with your thanos urls and respective tokens
   - run shell script ./recommend.sh

Output : 
   - Go to the logs folder and look for .csv files with recommendations. CSV files are named after the index order of the thanos url.

For more details understanding on how the system works, proceed [here](doc/details.md)   

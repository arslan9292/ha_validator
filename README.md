# The High Availability Validator [a.k.a ha_validator]

## Automating the tedious task of validating a Red Hat Pacemaker cluster setup in just a few seconds

### Introduction

For an environment where a group of servers/systems acting like a single system providing High Availability, is called a Cluster Environment. When an issue occurs in such an environment, it is essential to perform a preliminary check to validate if the environment is configured as per the recommendations. A misconfigured cluster can lead to some unexpected behavior. Hence to validate whether the environment is fully supported, we have to review sosreport from all the Red Hat Pacemaker Cluster servers or nodes.

A two node cluster validation may not take much longer. But when the number of nodes increases, the time to compare each server with other rises to a great extent. This validation check is essential for each of the cases which has issues related to cluster. Imagine how long it may take if a cluster is 10 nodes (servers) & if that being complete production outage scenario!

This prompted for a need of a automation which can bring some ease with increased productivity while saving a great amount of time. So here is the python3 script **ha_validator** [High Availability Validator] to serve this purpose.

This script does the validation check and compares the data across all the cluster nodes, then creates a comprehensive report within seconds. Thereby saving a lot of time and we do not have to look in multiple files to validate whether the environment is correctly configured as per support policies of Red Hat.

All we started in October 2019 with the first check being kernel version same across all the nodes when I started to learn Python. Now with continuous work in past 3 years it has evolved to a great extent & validating almost all possible support policy for a Red Hat's Pacemaker Cluster environment.

The script is currently being used by Red Hat Associates over the support cases created by the customers. There will be a future release to this project where it can be used by anyone and does not have any dependecy.

#### Process Flowchart

![Flowchart](https://user-images.githubusercontent.com/6632266/198813535-f8aa7855-1ac0-40be-8fbb-f0bb5bb49ce9.png)


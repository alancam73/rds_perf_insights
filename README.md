# rds_perf_insights
Lists which AWS RDS instances in an account do NOT have Performance Insights enabled

### Description
AWS Lambda function to query all the RDS Database Instances in an Account to check if any of them 
do NOT have Performance Insights enabled. This feature is very valuable for finding eg slow queries
however it defaults to False so new projects dont have it enabled unless its explcitly set in a CFT
This Lambda also outputs the instances that have Perf Insights = False to a CloudWatch Log Stream

### Pre-requisites
* python 3.8 or higher
* setup the correct IAM permissions - this is done via the YAML CFT

### Environment variables
* log_group_envvar : the name of the CW Log Group to output the log stream

### Example output
```
Timestamp	                    Message	
2022-05-21T14:15:59.525-07:00	aa1q7wtdln8p3u,db.r5.large,aurora,AuroraDB-Aurora-Test-Alerts-Metrics,False
2022-05-21T14:15:59.613-07:00	aau7bptdcvvkga,db.r5.large,aurora,AuroraDB-Aurora-Test-Alerts-Metrics,False
2022-05-21T14:15:59.684-07:00	xyz-eks-test-aurora-cluster,db.r5.large,aurora-mysql,,False

```

### Triggers
This lambda can be run standalone or via a trigger eg daily via an EventBridge rule eg rate(1 day)

### Alternatives
You could achieve the same via a query in AWS Config
* AWS Config -> Advanced Queries -> Query Editor:
```sql
SELECT
  resourceId,
  resourceName,
  resourceType,
  tags,
  relationships,
  configuration.dBInstanceClass,
  configuration.performanceInsightsEnabled,
  availabilityZone
WHERE
  resourceType = 'AWS::RDS::DBInstance'
  AND configuration.performanceInsightsEnabled = false
```

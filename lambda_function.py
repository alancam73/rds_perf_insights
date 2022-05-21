# Lambda to print out all RDS instances in an account that do NOT have Performance Insights enabled
# Also logs results to CloudWatch log stream

import json
import boto3
import os
import botocore
from botocore.exceptions import ClientError
import uuid
import time
from datetime import datetime

rdsClient = boto3.client('rds')
logsClient = boto3.client('logs')

logGroupParam = os.getenv('log_group_envvar')

def lambda_handler(event, context):
    
    print("List the status of Performance Insights for each RDS instance")
    print("InstName,InstType,InstEngine,InstNameTag,InstPerformanceInsightsEnabled")
    
    # set up the log groups & log stream so we can push PerfInsightsEnabled False occurrences to CW
    log_group = str(logGroupParam)
    log_stream = 'RDSInstancePerfInsights'
    now = datetime.now()
    date_time_fmt = now.strftime("%m-%d-%Y-%H-%M-%S")
    log_stream_dt = date_time_fmt + '-' + log_stream
    # log_response = logsClient.create_log_group(logGroupName=log_group)
    logsClient.create_log_stream(
        logGroupName=log_group,
        logStreamName=log_stream_dt
    )

    # get the list of RDS instances in this acct & their Performance Insights T/F status
    response = rdsClient.describe_db_instances()
    seq_token = None
    for instance in response['DBInstances']:

        db_instance_name = instance['DBInstanceIdentifier']
        db_type = instance['DBInstanceClass']
        db_perfInsEnabled = instance['PerformanceInsightsEnabled']
        db_engine = instance['Engine']
        
        tags = rdsClient.list_tags_for_resource(ResourceName=instance["DBInstanceArn"])
        db_name_tag = ''
        for tag in tags["TagList"]:
            if tag['Key'] == 'Name':
                db_name_tag = tag['Value']

        if db_perfInsEnabled == False:
            print (db_instance_name, db_type, db_engine, db_name_tag, db_perfInsEnabled, sep=",")
            instList = [db_instance_name, db_type, db_engine, db_name_tag, str(db_perfInsEnabled)]
            instanceData = ",".join(instList)
            
            log_event = {
                'logGroupName': log_group,
                'logStreamName': log_stream_dt,
                'logEvents': [
                    {
                        'timestamp': int(round(time.time() * 1000)),
                        'message': instanceData
                    },
                ],
            }
            
            if seq_token:
                log_event['sequenceToken'] = seq_token
            response = logsClient.put_log_events(**log_event)
            seq_token = response['nextSequenceToken']
    
        
    return None
    

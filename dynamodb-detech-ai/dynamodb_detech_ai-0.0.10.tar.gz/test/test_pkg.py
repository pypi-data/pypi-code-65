from detech_query_pkg import dynamodb_queries as db
import boto3
from datetime import datetime
import time


#detech's DynamoDB Credentials
AWS_ACCESS_KEY_ID = 'AKIAX4UUIUBY44E3YSUZ'
AWS_SECRET_ACCESS_KEY = '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'
REGION_NAME = 'eu-west-2'

dynamodb = boto3.resource('dynamodb',aws_access_key_id=AWS_ACCESS_KEY_ID, 
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=REGION_NAME)

'''
db.create_metric(
  metric_id = "test6", date_bucket = str(datetime.now()).split(' ')[0],
  anom_alarm_id = "crazy_monkey.juicy_bananas.kiwi_count2", metric_name = "Duration",
  provider = "aws", namespace = "AWS/Lambda", agent = "CloudWatch", org_id = "test",
  app_id = "app1", alignment = "Sum", groupby = "service", 
  dimensions = [],
  first = int(time.time()-100), last = int(time.time()), data_points_list = [], dynamodb=dynamodb
)'''

#a = db.get_metric_details('test6', dynamodb)
a = db.query_most_recent_metric_fetching_log('prd_db_2', dynamodb)
print(a['last_fetched_ts'])
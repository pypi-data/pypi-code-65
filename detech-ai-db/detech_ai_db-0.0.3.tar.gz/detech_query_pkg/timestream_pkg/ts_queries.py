import sys
import random
import time

#sys.path.insert(1, '/home/jvelez/Documents/detech/Data_Pipelines/detech_query_pkg/timestream_pkg')
from .utils.ts_utils import create_timestream_session, prepare_metric_records, write_to_timestream, query_from_timestream


DATABASE_NAME = 'detech.ai'
TABLE_NAME = 'DevOpsMetrics'

def insert_metrics_from_metric_list(metric_list, session):
  '''
  Receives a list of metric dicts and inserts them into timestream
  '''
  records = []
  for metric in metric_list:
    dimensions = [
      {'Name':'org_id', 'Value': str(metric['org_id'])},
      {'Name':'region_name', 'Value':str(metric['region_name'])},
      {'Name':'namespace', 'Value':str(metric['namespace'])},
      {'Name':'component_id', 'Value':str(metric['component_id'])},
      {'Name':'period', 'Value': str(metric['period'])},
      {'Name':'agent', 'Value':str(metric['agent'])},
      {'Name':'metric_alignment', 'Value':str(metric['metric_alignment'])},
      {'Name':'unit', 'Value':str(metric['unit'])},
      {'Name': 'description', 'Value': str(metric['description'])},
      {'Name': 'metric_id', 'Value':str(metric['metric_id'])}
    ]
    records.append(prepare_metric_records(metric['metric_name'], str(metric['value']), metric['timestamp'], dimensions))
  results = write_to_timestream(records, DATABASE_NAME, TABLE_NAME, session)

def query_metrics(sql_query, session):
  '''
  Performs a query to timestream, and formats the response in a list of MetricModel objects
  '''
  """SELECT metric_id, agent, component_id, period, unit, org_id, metric_alignment, namespace,
  description, region_name, measure_value::double as value, measure_name as metric_name, BIN(time, 1m) as timestamp 
  FROM "detech.ai"."DevOpsMetrics"
  GROUP BY metric_id, agent, component_id, period, unit, org_id, metric_alignment, namespace,
  description, region_name, measure_value::double, measure_name , BIN(time, 1m)
  ORDER BY metric_id, BIN(time, 1m) DESC"""
  query_response = query_from_timestream(sql_query, DATABASE_NAME, TABLE_NAME ,session)
  metric_obj_list =[]
  if query_response['ResponseMetadata']['HTTPStatusCode'] == 200:
    if len(query_response['Rows']) == 0:#empty request
      print('Empty request')
    else:
      for metric in query_response['Rows']:
        #Each metric returned
        curr_metric = {}
        for idx, attr in enumerate(metric['Data']):
          curr_metric[query_response['ColumnInfo'][idx]['Name']] = attr['ScalarValue']
        metric_obj_list.append(curr_metric)
  else:
    raise Exception('Error in requesting query: Status Code: {}'.format(str(query_response['ResponseMetadata']['HTTPStatusCode'])))
  return metric_obj_list

#metric_list = test_insert_metrics()
#insert_metrics_from_metric_list(metric_list)
session = create_timestream_session(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
metric_obj_list = query_metrics("""SELECT metric_id, agent, component_id, period, unit, org_id, metric_alignment, namespace,
  description, region_name, measure_value::double as value, measure_name as metric_name, BIN(time, 1m) as timestamp 
  FROM "detech.ai"."DevOpsMetrics"
  GROUP BY metric_id, agent, component_id, period, unit, org_id, metric_alignment, namespace,
  description, region_name, measure_value::double, measure_name , BIN(time, 1m)
  ORDER BY metric_id, BIN(time, 1m) DESC""", session)

for metric in metric_obj_list:
  print(metric)
  print('')
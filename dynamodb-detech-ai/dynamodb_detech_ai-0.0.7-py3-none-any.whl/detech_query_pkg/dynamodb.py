from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr

from .utils.dynamodb_utils import put_item, delete_item_conditionally
from .utils.dynamodb_utils import get_item, query_by_key, get_item_and_retrieve_specific_attributes,\
  query_and_project_by_key_condition, scan_table, query_by_key_min_max
from .utils.dynamodb_utils import update_item, update_item_conditionally

import datetime

ALERTS_TABLE = 'alerts.items'
ALERTS_CONFIGS_TABLE = 'alerts.config'
METRICS_TIMESERIES_TABLE = 'metrics.ts'
LOGS_METRICS_FETCHING_TABLE = 'logs.cloud_metric_fetching'

############ ALERTS ###########################
def insert_alert(alert_id, metric_id, org_id, app_id, team_id, assigned_to, start_time,
  end_time, alert_description, is_acknowledged, anomalies_dict, related_prev_anomalies,
  service_graph, significance_score, dynamodb):
  '''
  insert_alert(alert_id = "256828", metric_id = 123, org_id = 'org_id', app_id = 'app_id', team_id = 'team_id', assigned_to = 'Jorge', \
  start_time = '2020-09-03 12:00:00', end_time = '2020-09-03 12:20:00', alert_description = 'Spike in costs',\
  is_acknowledged = 'True', anomalies_dict = {}, related_prev_anomalies = {},
  service_graph = {}, significance_score = '34.3')
  '''
  alert_dict = {
    'alert_id' : alert_id,
    'metric_id' : metric_id,
    'org_id': org_id,
    'app_id': app_id,
    'team_id' : team_id,
    'assigned_to' : assigned_to,
    'start_time' : start_time,
    'end_time' : end_time,
    'alert_description' : alert_description,
    'is_acknowledged' : is_acknowledged,
    'anomalies_dict' : anomalies_dict,
    'related_prev_anomalies' : related_prev_anomalies,
    'service_graph': service_graph,
    'significance_score':  significance_score
  }

  print(alert_dict)
  response = put_item(alert_dict, ALERTS_TABLE, dynamodb)
  return response

def get_alert_item_by_key(anom_id, dynamodb):
  key_dict = {
    "alert_id" : anom_id, 
  }
  alert_item = get_item(key_dict, ALERTS_TABLE, dynamodb)
  return alert_item

def update_alert_with_related_anomalies(alert_id,start_time, corr_anoms_dict, related_prev_anomalies, dynamodb):
  #https://stackoverflow.com/questions/52367094/how-to-update-dynamodb-table-with-dict-data-type-boto3
  #TODO add similar alerts
  update_expression = "set anomalies_dict=:a, related_prev_anomalies=:r"
  expression_attr_values = {
    ':a': corr_anoms_dict,
    ':r': related_prev_anomalies,
  }
  key_dict = {
    'alert_id' : alert_id,
    'start_time' : start_time,
  }
  
  update_item(key_dict, update_expression, expression_attr_values, ALERTS_TABLE, dynamodb)

  return True 

def terminate_alert(alert_id,start_time, end_timestamp, dynamodb):
  update_expression = "set end_timestamp=:e"
  expression_attr_values = {
    ':e': end_timestamp
  }
  key_dict = {
    'alert_id' : alert_id,
    'start_time' : start_time,
  }
  
  update_item(key_dict, update_expression, expression_attr_values, ALERTS_TABLE, dynamodb)

  return True 


############ METRICS ##########################
#create new metric_timeseries item for current day
def create_metric(metric_id, date_bucket, anom_alarm_id, metric_name, provider, namespace,
  agent, org_id, app_id, alignment, groupby, first, last, dimensions, data_points_list, dynamodb):
  '''
  create_metric(
    metric_id = "test1", date_bucket = "2020-10-02",
    anom_alarm_id = "crazy_monkey.juicy_bananas.kiwi_count", metric_name = "error_rate",
    provider = "aws", namespace = "dynamodb", agent = "CloudWatch", org_id = "test",
    app_id = "app1", alignment = "Sum", groupby = "service", first = 1535530412,
    dimensions = [{"Name": "TableName", "Value": "alerts.config"}],
    last = 1535530432, data_points_list = [
      { 'val': 55, 'time' : 1535530430}, 
      { 'val': 56, 'time': 1535530432}], dynamodb=dynamodb
  )
  '''
  metric_dict = {
    "metric_id" : metric_id, 
    "date_bucket" : date_bucket,
    "metric_name" : metric_name,
    "encrypted_id" : anom_alarm_id,
    "provider" : provider,
    "namespace" : namespace,
    "agent" : agent,
    "orgId" : org_id,
    "appId" : app_id, 
    "metric_alignment" : alignment,
    "groupby" : groupby,
    "first" : first,
    "last": last,
    "dimensions": dimensions,
    "data_points_list" : data_points_list
  }

  #print(alert_dict)
  response = put_item(metric_dict, METRICS_TIMESERIES_TABLE, dynamodb)
  return response

def get_metric_details(metric_id, dynamodb):
  now = datetime.datetime.now()
  date = str(now).split(' ')[0]
  key_dict = {
    "metric_id" : metric_id,
    "date_bucket" : date,
  }
  attr_list = ['metric_id', 'metric_name', 'namespace','metric_alignment', 'dimensions']
  metric_details = get_item_and_retrieve_specific_attributes(key_dict, attr_list, METRICS_TIMESERIES_TABLE, dynamodb)
  return metric_details

#query metrics info by metric_id key
def get_metric_item_by_key(metric_id, curr_date, dynamodb):
  #get_metric_item_by_key(123, '2020-09-10')
  key_dict = {
    "metric_id" : metric_id, 
    "date_bucket" : str(curr_date)
  }

  metric_item = get_item(key_dict, 'metric.ts', dynamodb)
  return metric_item

def scan_metrics_by_encrypted_id(anom_alarm_id, dynamodb):
  scan_kwargs = {
    'FilterExpression': Attr('encrypted_id').eq(anom_alarm_id),
  }
  metric_list = scan_table(scan_kwargs, 'metric.ts', dynamodb)
  metric_item = metric_list[0]
  return metric_item


############## ALERT CONFIGS ################
def query_alerts_configs_by_key(metric_id, dynamodb):
  key_condition = Key('metric_id').eq(metric_id)
  alerts_configs_list = query_by_key(key_condition, ALERTS_CONFIGS_TABLE, dynamodb)
  return alerts_configs_list  

def insert_alert_config(metric_id, alert_title, severity, alert_type, alert_direction, description, 
  duration, duration_unit, rule_dict, recipients_list, owner_dict, dynamodb):
  '''
  insert_alert_config(
    metric_id = "metric1245", alert_title = "Anomaly by Cluster", severity = "critical",
    alert_type = "anomaly", alert_direction = "spikes/drops", description = "Relevant to Play Store billing user journey",
    duration= 12, duration_unit = "hours", rule_dict = {}, recipients_list = [{
      "channel" : "webhook", 
      "contact" : "j.velez2210@gmail.com"
      },{
        "channel" : "slack",
        "contact" : "j.velez2210@gmail.com"
      }
    ], 
    owner_dict = {
      "user_id" : "user12341",
      "user_name" : "João Tótó",
    }
  )
  '''
  alert_dict = {
    "metric_id" : metric_id, 
    "alert_title" : alert_title,
    "severity" : severity, 
    "alert_type" : alert_type,
    "alert_direction" : alert_direction, 
    "description" : description,
    "duration" : duration,
    "duration_unit" : duration_unit,
    "rule_dict" : rule_dict,
    "recipients" : recipients_list,
    "owner" : owner_dict
  }

  #print(alert_dict)
  response = put_item(alert_dict, 'alerts.config')
  return response

############## LOGS #########################
def query_most_recent_metric_fetching_log(component_id, dynamodb):
  '''
  Fetches the log with the highest timestamp, from all the logs between start & end ts
  '''
  #TODO Insert a greater than last_fetched_ts condition to prevent the query to go too far in time
  key_condition = Key('component_id').eq(component_id) #& Key('last_fetched_ts').between(start_ts, end_ts)
  logs_list = query_by_key_min_max(key_condition, LOGS_METRICS_FETCHING_TABLE, False, dynamodb)
  log_item = logs_list[0]
  print(log_item)
  return log_item

############## EXAMPLES #####################
def update_values_in_dict_attr():
  '''
  dynamo = boto3.resource('dynamodb')  
    tbl = dynamo.Table('<TableName>')  

    result = tbl.update_item(  
        Key={  
            "game_id": game_id  
        },  
        UpdateExpression="SET players.#player_id.score = :score_val",  
        ExpressionAttributeNames={  
            "#player_id": player_id  
        },  
        ExpressionAttributeValues={  
            ":score_val": score_val  
        }  
    )
  '''
  return True


########## Function Calls ##########################
#query_most_recent_metric_fetching_log('prd_db')
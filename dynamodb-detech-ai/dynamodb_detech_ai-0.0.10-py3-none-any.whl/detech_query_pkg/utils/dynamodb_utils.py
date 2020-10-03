from pprint import pprint
import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from decimal import Decimal

from http import HTTPStatus


class DynamoDBError(Exception):
  def __init__(self, msg):
    self.msg = msg
  def __str__(self):
    return self.msg


def create_dynamodb_client(aws_access_key_id,aws_secret_access_key, region_name):
  try:
    return boto3.resource('dynamodb',aws_access_key_id=aws_access_key_id, 
      aws_secret_access_key=aws_secret_access_key, region_name=region_name)
  except ClientError as e:
    raise DynamoDBError(e.response['Error']['Message'])

def put_item(item_dict, table_name, dynamodb):
  '''
  Inserts json item into DynamoDB table
  item_dict = {
    "attr" : "value",
    "attr2" : "value2"
  }
  table_name = "alerts
  '''
  try:
    table = dynamodb.Table(table_name)
    return table.put_item(
        Item = item_dict
    )
  except ClientError as e:
    raise DynamoDBError(e.response['Error']['Message'])

def get_item(key_dict, table_name, dynamodb):
  '''
  Retrieves item from DynamoDB table
  key_dict = {
    "prim_key" : "value",
    "sort_key" : "value"
  }
  '''
  try:
    table = dynamodb.Table(table_name)
    return table.get_item(Key=key_dict)['Item']
  except ClientError as e:
    raise DynamoDBError(e.response['Error']['Message'])

def get_item_and_retrieve_specific_attributes(key_dict, attr_list, table_name, dynamodb):
  '''
  Retrieves item from DynamoDB table and retrieve specific attributes
  key_dict = {
    "prim_key" :"value",
    "sort_key" : "value"
  }
  attr_list = ['attr1', 'attr2']
  '''
  try:
    table = dynamodb.Table(table_name)
    return table.get_item(Key=key_dict, AttributesToGet=attr_list)['Item']
  except ClientError as e:
    raise DynamoDBError(e.response['Error']['Message'])

def update_item(key_dict, update_expression, expression_attr_values, table_name, dynamodb):
  '''
  Retrieves item from DynamoDB table
  key_dict = {
    "prim_key" = "value",
    "sort_key" = "value"
  }
  update_expression = "set service_graph=:i, metric_list=:l, significance_score=:s"
  expression_attr_values = {
    ':i': {'s1':['s2', 's3']},
    ':l': ['124','123'],
    ':s': Decimal(35.5)
  }
  #example to append to list
  UpdateExpression="SET some_attr = list_append(if_not_exists(some_attr, :empty_list), :i)",
  ExpressionAttributeValues={
    ':i': [some_value],
    "empty_list" : []
  }
  '''
  table = dynamodb.Table(table_name)
  try:
    return table.update_item(
      Key = key_dict,
      UpdateExpression= update_expression,
      ExpressionAttributeValues= expression_attr_values,
      ReturnValues="UPDATED_NEW"
    )
  except ClientError as e:
    raise DynamoDBError(e.response['Error']['Message'])
    

def update_item_conditionally(key_dict, condition_expression, update_expression, expression_attr_values, table_name, dynamodb):
  '''
  Retrieves item from DynamoDB table
  key_dict = {
    "prim_key" = "value",
    "sort_key" = "value"
  }
  update_expression = "set service_graph=:i, metric_list=:l, significance_score=:s"
  expression_attr_values = {
    ':i': {'s1':['s2', 's3']},
    ':l': ['124','123'],
    ':s': Decimal(35.5)
  }
  condition_expression = "significance_score <= :val"
  '''
  try:
    table = dynamodb.Table(table_name)
    return table.update_item(
      Key = key_dict,
      UpdateExpression= update_expression,
      ExpressionAttributeValues= expression_attr_values,
      ConditionExpression = condition_expression,
      ReturnValues="UPDATED_NEW"
    )
  except ClientError as e:
    raise DynamoDBError(e.response['Error']['Message'])
  

def delete_item_conditionally(key_dict, condition_expression, expression_attr_values, table_name, dynamodb):
  '''
  condition_expression = "significance_score <= :val"
  expression_attr_values = {
    ":val": Decimal(50)
  }
  key_dict = {
    'org_id': 'Aptoide',
    'start_time': '2020-09-03 12:00:00'
  }
  '''
  try:
    table = dynamodb.Table(table_name)
    return table.delete_item(
      Key=key_dict,
      ConditionExpression = condition_expression,
      ExpressionAttributeValues = expression_attr_values,
    )
  except ClientError as e:
    raise DynamoDBError(e.response['Error']['Message'])

def query_by_key(key_condition, table_name, dynamodb):
  '''
  Queries from DynamoDB table by key condition
  key_condition = Key('org_id').eq('Aptoide')
  '''
  try:
    table = dynamodb.Table(table_name)
    return table.query(
      KeyConditionExpression=key_condition
    )['Item']
  except ClientError as e:
    raise DynamoDBError(e.response['Error']['Message'])

def query_and_project_by_key_condition(projection_expr, expr_attr_names, key_condition, table_name, dynamodb):
  '''
  Queries from DynamoDB table by key condition and only returns some attrs
  key_condition = Key('year').eq(year) & Key('title').between(title_range[0], title_range[1])
  projection_expr = "#yr, title, info.genres, info.actors[0]"
  expr_attr_names = {"#yr": "year"}
  '''
  try:
    table = dynamodb.Table(table_name)
    return table.query(
      KeyConditionExpression = key_condition,
      ProjectionExpression = projection_expr,
      ExpressionAttributeNames = expr_attr_names
    )['Items']
  except ClientError as e:
    raise DynamoDBError(e.response['Error']['Message'])

def scan_table(scan_kwargs, table_name, dynamodb):
  '''
  Scans entire table looking for items that match the filter expression
  scan_kwargs = {
    'FilterExpression': Key('year').between(*year_range),
    'ProjectionExpression': "#yr, title, info.rating",
    'ExpressionAttributeNames': {"#yr": "year"}
  }
  '''
  try:
    table = dynamodb.Table(table_name)

    done = False
    start_key = None
    result_list = []
    while not done:
      if start_key:
        scan_kwargs['ExclusiveStartKey'] = start_key
      response = table.scan(**scan_kwargs)
      #Do SMTH with response
      result_list.append(response['Items'])
      start_key = response.get('LastEvaluatedKey', None)
      done = start_key is None
  except ClientError as e:
    raise DynamoDBError(e.response['Error']['Message'])
  else:
    return result_list

def query_by_key_min_max(key_condition, table_name, is_min, dynamodb):
  '''
  Queries from DynamoDB table by key condition
  key_condition = Key('part_id').eq(partId) & Key('range_key').between(start, end)
  '''
  try:
    table = dynamodb.Table(table_name)
    return table.query(
      KeyConditionExpression=key_condition,
      ScanIndexForward = is_min,
      Limit = 1
    )['Items']
  except ClientError as e:
    raise DynamoDBError(e.response['Error']['Message'])

def get_all_items_in_table(table_name, dynamodb):
  try:
    table = dynamodb.Table(table_name)
    return table.scan()['Items']
  except ClientError as e:
    raise DynamoDBError(e.response['Error']['Message'])
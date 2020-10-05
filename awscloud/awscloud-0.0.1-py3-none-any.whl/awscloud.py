__author__ = 'akashjeez'

import os, math, json, boto3
from dateutil.parser import parse
from datetime import datetime, timedelta
from botocore.exceptions import ClientError


class AWSCloud:

	def __init__(self, session) -> None:
		self.session = session


	def List_EC2_Instances(self) -> dict:
		try:
			dataset, ec2_obj = [], self.session.resource('ec2')
			for instance in ec2_obj.instances.all():
				instance = ec2_obj.Instance(instance.id)
				data_dump = {
					'Instance_ID': instance.id,
					'Instance_Type': instance.instance_type,
					'Architecture': instance.architecture,
					'CPU_Options': instance.cpu_options,
					'EBS_Optimized': instance.ebs_optimized,
					'Hypervisor': instance.hypervisor,
					'IAM_Profile': instance.iam_instance_profile,
					'Image_ID': instance.image_id,
					'Launch_Time': instance.launch_time.strftime('%d-%m-%y %I:%M %p'),
					'Key_Name': instance.key_name,
					'Monitoring': instance.monitoring.get('State', 'TBD'),
					'Network_Interface': instance.network_interfaces_attribute,
					'Availability': instance.placement.get('AvailabilityZone', 'TBD'),
					'Private_DNS_Name': instance.private_dns_name,
					'Private_IP_Address': instance.private_ip_address,
					'Root_Device_Name': instance.root_device_name,
					'Root_Device_Type': instance.root_device_type,
					'Security_Groups': instance.security_groups,
					'Source_Dest_Check': instance.source_dest_check,
					'State': instance.state.get('Name', 'TBD'),
					'Subnet_ID': instance.subnet_id,
					'Virtualization_Type': instance.virtualization_type,
					'VPC_ID': instance.vpc_id,
				}
				if instance.tags:
					data_dump.update( { i['Key'] : i['Value'] for i in instance.tags } )
				dataset.append( data_dump )
			return { 'count' : len(dataset), 'data' : dataset }
		except Exception as ex:
			return { 'data' : { 'error' : ex } }


	def List_EC2_Volumes(self) -> dict:
		try:
			dataset, ec2_obj = [], self.session.client('ec2')
			for data in ec2_obj.describe_volumes()['Volumes']:
				data_dump = {
					'Volume_ID': data.get('VolumeId', 'TBD'),
					'IOPS': data.get('Iops', 'TBD'),
					'State': data.get('State', 'TBD'),
					'Size_GB': data.get('Size', 'TBD'),
					'Snapshot_ID': data.get('SnapshotId', 'TBD'),
					'Encrypted': data.get('Encrypted', 'TBD'),
					'Volume_Type': data.get('VolumeType', 'TBD'),
					'Availability_Zone': data.get('AvailabilityZone', 'TBD'),
					'Creation_Date': data.get('CreateTime').strftime('%d-%m-%Y') 
						if 'CreateTime' in data.keys() else 'TBD',
				}
				if len(data['Attachments']) > 0:
					attachment = data.get('Attachments')[0]
					data_dump.update({
						'Attach_Device': attachment.get('Device', 'TBD'),
						'Attach_Instance_ID': attachment.get('InstanceId', 'TBD'),
						'Attach_Time': attachment.get('AttachTime').strftime('%d-%m-%Y')
							if 'AttachTime' in attachment.keys() else 'TBD',
						'Attach_State': attachment.get('State', 'TBD'),
						'Attach_Volume_ID': attachment.get('VolumeId', 'TBD'),
						'Attach_Delete_On_Termination': attachment.get('DeleteOnTermination', 'TBD')
					})
				if 'Tags' in data.keys():
					data_dump.update( { i['Key'] : i['Value'] for i in data['Tags'] } )
				dataset.append(data_dump)
			return { 'count' : len(dataset), 'data' : dataset }
		except Exception as ex:
			return { 'data' : { 'error' : ex } }


	def List_EC2_Snapshots(self) -> dict:
		try:
			dataset, ec2_obj = [], self.session.client('ec2')
			for data in ec2_obj.describe_snapshots(OwnerIds = ['self'])['Snapshots']:
				data_dump = {
					'Snapshot_id': data.get('SnapshotId', 'TBD'),
					'Size_GB': data.get('VolumeSize', 'TBD'),
					'Volume_ID': data.get('VolumeId', 'TBD'),
					'Start_Time': data['StartTime'].strftime('%d-%m-%Y') if 'StartTime' in data.keys() else 'TBD',
					'Encrypted': data.get('Encrypted', 'TBD'),
					'Owner_ID': data.get('OwnerId', 'TBD'),
					'Progress': data.get('Progress', 'TBD'),
					'State': data.get('State', 'TBD'),
					'Sescription': data.get('Description', 'TBD'),
				}
				if 'Tags' in data.keys():
					data_dump.update( { i['Key'] : i['Value'] for i in data['Tags'] } )
				dataset.append(data_dump)
			return { 'count' : len(dataset), 'data' : dataset }
		except Exception as ex:
			return { 'data' : { 'error' : ex } }


	def List_EC2_Security_Groups(self) -> dict:
		try:
			dataset, ec2_obj = [], self.session.resource('ec2')
			for data in ec2_obj.security_groups.all():
				data_dump = {
					'Security_Group_ID': data.id,
					'Security_Group_Name': data.group_name,
					'Inbound_Rules': data.ip_permissions,
					'Outbound_Rules': data.ip_permissions_egress,
					'Owner_ID': data.owner_id,
					'VPC_ID': data.vpc_id,              
					'Description': data.description,
				}
				if data.tags:
					data_dump.update( { i['Key'] : i['Value'] for i in data.tags } )
				dataset.append( data_dump )
			return { 'count' : len(dataset), 'data' : dataset }
		except Exception as ex:
			return { 'data' : { 'error' : ex } }


	def List_EC2_Load_Balancers(self) -> dict:
		try:
			dataset = []
			## Load Balancer Type is Application & Network.
			paginator = self.session.client('elbv2').get_paginator('describe_load_balancers')
			for response in paginator.paginate():
				for data in response['LoadBalancers']:
					dataset.append({
						'Load_Balancer_Name': data.get('LoadBalancerName'),
						'DNS_Name': data.get('DNSName', 'TBD'),
						'LB_Type': data.get('Type', 'TBD'),
						'Canonical_Zone_ID': data.get('CanonicalHostedZoneId', 'TBD'),              
						'Scheme': data.get('Scheme', 'TBD'),
						'Load_Balancer_ARN': data.get('LoadBalancerArn', 'TBD'),
						'VPC_ID': data.get('VpcId', 'TBD'),
						'State': data.get('State', 'TBD'),
						'Availability_Zone': data.get('AvailabilityZones', 'TBD'),
						'Security_Groups': data.get('SecurityGroups', 'TBD'),
						'Creation_Date': parse(str(data.get('CreatedTime'))).strftime('%d-%m-%Y')
							if 'CreatedTime' in data.keys() else 'TBD',
					})
			## Load Balancer Type is Classic.
			paginator = self.session.client('elb').get_paginator('describe_load_balancers')
			for response in paginator.paginate():
				for data in response['LoadBalancerDescriptions']:
					dataset.append({
						'Load_Balancer_Name': data.get('LoadBalancerName'),
						'DNS_Name': data.get('DNSName', 'TBD'),
						'LB_Type': 'Classic',
						'Canonical_Zone_ID': data.get('CanonicalHostedZoneNameID', 'TBD'),
						'Scheme': data.get('Scheme', 'TBD'),
						'Load_Balancer_ARN': data.get('LoadBalancerArn', 'TBD'),
						'Listener_Descriptions': data.get('ListenerDescriptions', 'TBD'),
						'Policies': data.get('Policies', 'TBD'),
						'Availability_Zone': data.get('AvailabilityZones', 'TBD'),
						'Subnets': data.get('subnets', 'TBD'),
						'VPC_ID': data.get('VPCID', 'TBD'),
						'Security_Groups': data.get('SecurityGroups', 'TBD'),
						'Instances': data.get('Instances', 'TBD'),
						'Health_check': data.get('HealthCheck', 'TBD'),
						'Source_SG_Name': data['SourceSecurityGroup'].get('GroupName', 'TBD'),
						'Owner_Alias': data['SourceSecurityGroup'].get('OwnerAlias', 'TBD'),
						'Creation_Date': parse(str(data.get('CreatedTime'))).strftime('%d-%m-%Y')
					})
			return { 'count' : len(dataset), 'data' : dataset }
		except Exception as ex:
			return { 'data' : { 'error' : ex } }


	def List_EC2_Network_Interfaces(self) -> dict:
		try:
			dataset, ec2_obj = [], self.session.client('ec2')
			paginator = ec2_obj.get_paginator('describe_network_interfaces')
			for response in paginator.paginate():
				for data in response['NetworkInterfaces']:
					dataset.append({
						'Network_Interface_ID': data.get('NetworkInterfaceId', 'TBD'),
						'Subnet_id': data.get('SubnetId', 'TBD'),
						'VPC_ID': data.get('VpcId', 'TBD'),
						'Availability_Zone': data.get('AvailabilityZone', 'TBD'),
						'Owner_ID': data.get('OwnerId', 'TBD'),
						'Status': data.get('Status', 'TBD'),
						'Security_Groups': data.get('Groups', 'TBD'),
						'MAC_Address': data.get('MacAddress', 'TBD'),
						'Private_DNS_Name': data.get('PrivateDnsName', 'TBD'),
						'Private_IP_Address': data.get('PrivateIpAddress', 'TBD'),
						'Public_IP_Address': data['Association'].get('PublicDnsName', 'TBD')
							if 'Association' in data.keys() else 'TBD', 
						'Attachment': data.get('Attachment', 'TBD'),
						'Description': data.get('Description', 'TBD'),
					})
			return { 'count' : len(dataset), 'data' : dataset }
		except Exception as ex:
			return { 'data' : { 'error' : ex } }


	def List_EC2_Key_Pairs(self) -> dict:
		try:
			dataset, ec2_obj = [], self.session.client('ec2')
			for data in ec2_obj.describe_key_pairs()['KeyPairs']:
				data_dump = {
					'Key_Pair_ID': data.get('KeyPairId', 'TBD'),
					'Key_Fingerprint': data.get('KeyFingerprint', 'TBD'),
					'Key_Name': data.get('KeyName', 'TBD'),
				}
				if 'Tags' in data.keys():
					data_dump.update( { i['Key'] : i['Value'] for i in data['Tags'] } )
				dataset.append(data_dump)
			return { 'count' : len(dataset), 'data' : dataset }
		except Exception as ex:
			return { 'data' : { 'error' : ex } }


	def List_Elastic_Beanstalk_Apps(self) -> dict:
		try:
			dataset, ec2_obj = [], self.session.client('elasticbeanstalk')
			paginator = ec2_obj.get_paginator('describe_environments')
			for response in paginator.paginate():
				for environment in response['Environments']:
					data_dump = {
						'Env_Name': environment.get('EnvironmentName', 'TBD'),
						'Env_ID': environment.get('EnvironmentId', 'TBD'),
						'App_Name': environment.get('ApplicationName', 'TBD'),
						'Platform': environment.get('SolutionStackName', 'TBD'),
						'Env_CName': environment.get('CNAME', 'TBD'),
						'Created_Date': datetime.strptime(str(environment['DateCreated'])[:10], '%Y-%m-%d').strftime('%d-%m-%Y')
							if 'DateCreated' in environment.keys() else 'TBD',
						'Updated_Date': datetime.strptime(str(environment['DateUpdated'])[:10], '%Y-%m-%d').strftime('%d-%m-%Y')
							if 'DateCreated' in environment.keys() else 'TBD',
						'Env_Status': environment.get('Status', 'TBD'),
						'Env_Health': environment.get('Health', 'TBD'),
						'Env_ARN': environment.get('EnvironmentArn', 'TBD'),
						'Env_Tier': environment.get('Tier').get('Name', 'TBD'),
					}
					if tags_data := ec2_obj.list_tags_for_resource(ResourceArn = environment['EnvironmentArn']):
						data_dump.update( { i['Key'] : i['Value'] for i in tags_data['ResourceTags'] } )
					dataset.append(data_dump)
			return { 'count' : len(dataset), 'data' : dataset }
		except Exception as ex:
			return { 'data' : { 'error' : ex } }


	def List_S3_Buckets(self) -> dict:
		try:
			dataset, s3_obj = [], self.session.client('s3')
			for data in s3_obj.list_buckets()['Buckets']:
				data_dump = {
					'Bucket_Name': data.get('Name', 'TBD'),
					'Creation_Date': parse( str( data['CreationDate'] ) ).strftime('%d-%m-%Y') 
					if 'CreationDate' in data.keys() else 'TBD',
				}
				try:
					## Get Bucket Tagging.
					if bucket_tagging := s3_obj.get_bucket_tagging(Bucket = data.get('Name')):
						data_dump.update( { i['Key'] : i['Value'] for i in bucket_tagging['TagSet'] } )
				except ClientError:	pass

				try:
					## Get Bucket Policy
					if bucket_policy := s3_obj.get_bucket_policy(Bucket = data.get('Name')):
						data_dump.update( json.loads( bucket_policy['Policy'] )['Statement'][0] )
				except ClientError:	pass

				try:
					## Get Bucket Policy Status like Public or Private.
					if bucket_policy_status := s3_obj.get_bucket_policy_status(Bucket = data.get('Name')):
						data_dump.update( { 'is_public' : bucket_policy_status['PolicyStatus']['IsPublic'] } )
				except ClientError:	pass
				dataset.append(data_dump)
			return { 'count' : len(dataset), 'data' : dataset }
		except Exception as ex:
			return { 'data' : { 'error' : ex } }


	def Convert_Size(self, size_bytes: str) -> str:
		if size_bytes == 0:	return '0B'
		size_name = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
		i = int( math.floor( math.log( size_bytes, 1024 ) ) )
		p = math.pow(1024, i)
		s = round(size_bytes / p, 2)
		return f'{s} {size_name[i]}'


	def List_Lambda_Functions(self) -> dict:
		try:
			dataset, lambda_obj = [], self.session.client('lambda')
			paginator = lambda_obj.get_paginator('list_functions')
			for response in paginator.paginate():
				for data in response['Functions']:
					data_dump = {
						'Lambda_Name': data.get('FunctionName', 'TBD'),
						'Lambda_Arn': data.get('FunctionArn', 'TBD'),
						'Lambda_Runtime': data.get('Runtime', 'TBD'),
						'Lambda_Role': data.get('Role', 'TBD'),
						'Lambda_Handler': data.get('Handler', 'TBD'),
						'VPC_Config': data.get('VpcConfig', 'TBD'),
						'Environment': data.get('Environment', 'TBD'),
						'Lambda_Codesize': self.Convert_Size( int(data['CodeSize']) ) if 'CodeSize' in data.keys() else 'TBD',
						'Lambda_Timeout': f"{ int(data['Timeout']) } Secs" if 'Timeout' in data.keys() else 'TBD',
						'Memory_Size': f"{ int(data['MemorySize']) } MB" if 'MemorySize' in data.keys() else 'TBD',
						'Last_Modified': datetime.strptime(data['LastModified'][:10], '%Y-%m-%d').strftime('%d-%m-%Y')
							if 'LastModified' in data.keys() else 'TBD',
					}
					if lambda_tags := lambda_obj.list_tags(Resource = data['FunctionArn'])['Tags']:
						data_dump.update( lambda_tags )
					dataset.append( data_dump )
			return { 'count' : len(dataset), 'data' : dataset }
		except Exception as ex:
			return { 'data' : { 'error' : ex } }


	def List_AWS_RDS(self) -> dict:
		try:
			dataset, rds = [], self.session.client('rds')
			paginator = rds.get_paginator('describe_db_instances')
			for response in paginator.paginate():
				for data in response['DBInstances']:
					data_dump = {
						'DB_Resource_ID': data.get('DbiResourceId', 'TBD'),
						'DB_Identifier': data.get('DBInstanceIdentifier'),
						'DB_Instance_Class': data.get('DBInstanceClass', 'TBD'),
						'DB_Instance_Status': data.get('DBInstanceStatus', 'TBD'),
						'Master_Username': data.get('MasterUsername', 'TBD'),
						'DB_Name': data.get('DBName', 'TBD'),
						'Multi_AZ': data.get('MultiAZ', 'TBD'),                 
						'DB_Engine_Version': data.get('EngineVersion', 'TBD'),
						'Storage_DB': data.get('AllocatedStorage', 'TBD'),
						'Storage_Type': data.get('PubliclyAccessible', 'TBD'),
						'DB_Instance_ARN': data.get('DBInstanceArn', 'TBD'),
						'endpoint_Address': data.get('Endpoint', 'TBD'),
						'Backup_Window': data.get('PreferredBackupWindow', 'TBD'),
						'Backup_Retention_Period': data.get('BackupRetentionPeriod', 'TBD'),
						'VPC_Security_Groups': data.get('VpcSecurityGroups', 'TBD'),
						'DB_Instance_Location': data.get('AvailabilityZone', 'TBD'),                       
						'Character_SetName': data.get('CharacterSetName', 'TBD'),
						'Publicly_Accessible': data.get('PubliclyAccessible', 'TBD'),
						'Storage_Encrypted': data.get('StorageEncrypted', 'TBD'),
						'CA_Certificate_Identifier': data.get('CACertificateIdentifier', 'TBD'),
						'Maintenance_Window': data.get('PreferredMaintenanceWindow', 'TBD'),
						'Option_Group_Name': data['OptionGroupMemberships'][0].get('OptionGroupName', 'TBD'),
						'Option_Group_Status': data['OptionGroupMemberships'][0].get('Status', 'TBD'),
						'Parameter_Group_Name': data['DBParameterGroups'][0].get('DBParameterGroupName', 'TBD'),
						'Parameter_Group_Status': data['DBParameterGroups'][0].get('ParameterApplyStatus', 'TBD'),
						'Creation_Date': parse( str( data.get('InstanceCreateTime') ) ).strftime('%d-%m-%Y'),
						'Latest_Restore_Date': parse( str( data.get('LatestRestorableTime') ) ).strftime('%d-%m-%Y') 
							if 'LatestRestorableTime' in data.keys() else 'TBD',
					}
					if subnet_group := data['DBSubnetGroup']:
						data_dump.update({
							'Subnet_Group_Name': subnet_group.get('DBSubnetGroupName', 'TBD'),
							'SG_Description': subnet_group.get('DBSubnetGroupDescription', 'TBD'),
							'VPC_ID': subnet_group.get('VpcId', 'TBD'),
							'Subnets': subnet_group.get('Subnets', 'TBD'),
						})
					dataset.append( data_dump )
			return { 'count' : len(dataset), 'data' : dataset }
		except Exception as ex:
			return { 'data' : { 'error' : ex } }


	def Get_EC2_CPU_Metrics(self, start_date: str, end_date: str) -> dict:
		try:
			## Period = 43200 -> 12 hrs | 21600 -> 6 hrs | 10800 -> 3 hrs | 3600 -> 1hr
			dataset, ec2_obj = [], self.session.resource('ec2')
			for instance in ec2_obj.instances.all():
				response = self.session.client('cloudwatch').get_metric_statistics(
					Namespace = 'AWS/EC2', MetricName = 'CPUUtilization', 
					Dimensions = [ {'Name': 'InstanceId', 'Value': instance.id } ], 
					StartTime = start_date, EndTime = end_date, Period = 43200, 
					Statistics = ['Average', 'Sum'], Unit = 'Percent' )
				for data in response['Datapoints']:
					time_stamp = datetime.strptime( str( data.get('Timestamp') ), '%Y-%m-%d %H:%M:00+00:00')\
						.strftime('%d-%m-%Y %I:%M %p')
					dataset.append({ 
						'Instance_ID': instance.id,
						'Timestamp': time_stamp,
						'CPU_Percentage': round( data.get('Average', 0.0), 2),
						'Sum': round( data.get('Sum', 0), 2)
					})
			return { 'count' : len(dataset), 'data' : dataset }
		except Exception as ex:
			return { 'data' : { 'error' : ex } }


	def List_Cost_Trust_Advisor(self) -> dict:
		try:
			categories = ['cost_optimizing', 'security', 'fault_tolerance', 'performance', 'service_limits']
			dataset, advisor_obj = [], self.session.client('support')
			response = advisor_obj.describe_trusted_advisor_checks(language = 'en')
			for check in response['checks']:
				if check.get('category') == 'cost_optimizing':
					data_lake = advisor_obj.describe_trusted_advisor_check_result(
						checkId = check.get('id'), language = 'en' )
					for data in data_lake['result']['flaggedResources']:
						data_dump = {k:v for k, v in zip(check.get('metadata'), data['metadata'])}
						data_dump.update({'check_id': check.get('id'), 'name': check.get('name')})
						dataset.append(data_dump)
			return { 'count' : len(dataset), 'data' : dataset }
		except Exception as ex:
			return { 'data' : { 'error' : ex } }


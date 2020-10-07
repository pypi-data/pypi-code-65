from datetime import datetime


class CloudFormationMock:
    def list_stacks(self, *args, **kwargs):
        return {
            'StackSummaries': [
                {
                    'StackId': 'string',
                    'StackName': 'TestStackName',
                    'TemplateDescription': 'string',
                    'CreationTime': datetime(2015, 1, 1),
                    'LastUpdatedTime': datetime(2015, 1, 1),
                    'DeletionTime': datetime(2015, 1, 1),
                    'StackStatus': 'IMPORT_ROLLBACK_COMPLETE',
                    'StackStatusReason': 'string',
                    'ParentId': 'string',
                    'RootId': 'string',
                    'DriftInformation': {
                        'StackDriftStatus': 'NOT_CHECKED',
                        'LastCheckTimestamp': datetime(2015, 1, 1)
                    }
                },
            ],
            'NextToken': 'string'
        }

    def describe_stacks(self, *args, **kwargs):
        return {
            'Stacks': [
                {
                    'StackId': 'string',
                    'StackName': 'TestStackName',
                    'ChangeSetId': 'string',
                    'Description': 'string',
                    'Parameters': [
                        {
                            'ParameterKey': 'string',
                            'ParameterValue': 'string',
                            'UsePreviousValue': True | False,
                            'ResolvedValue': 'string'
                        },
                    ],
                    'CreationTime': datetime(2015, 1, 1),
                    'DeletionTime': datetime(2015, 1, 1),
                    'LastUpdatedTime': datetime(2015, 1, 1),
                    'RollbackConfiguration': {
                        'RollbackTriggers': [
                            {
                                'Arn': 'string',
                                'Type': 'string'
                            },
                        ],
                        'MonitoringTimeInMinutes': 123
                    },
                    'StackStatus': 'IMPORT_ROLLBACK_COMPLETE',
                    'StackStatusReason': 'string',
                    'DisableRollback': True | False,
                    'NotificationARNs': [
                        'string',
                    ],
                    'TimeoutInMinutes': 123,
                    'Capabilities': [
                        'CAPABILITY_AUTO_EXPAND',
                    ],
                    'Outputs': [
                        {
                            'OutputKey': 'key',
                            'OutputValue': 'value',
                            'Description': 'string',
                            'ExportName': 'key'
                        },
                    ],
                    'RoleARN': 'string',
                    'Tags': [
                        {
                            'Key': 'string',
                            'Value': 'string'
                        },
                    ],
                    'EnableTerminationProtection': False,
                    'ParentId': 'string',
                    'RootId': 'string',
                    'DriftInformation': {
                        'StackDriftStatus': 'NOT_CHECKED',
                        'LastCheckTimestamp': datetime(2015, 1, 1)
                    }
                },
            ],
            'NextToken': 'string'
        }

from localstack.utils.aws import aws_models
EDXNn=super
EDXNc=None
EDXNh=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  EDXNn(LambdaLayer,self).__init__(arn)
  self.cwd=EDXNc
  self.runtime=''
  self.handler=''
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.EDXNh.split(':')[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,EDXNh,env=EDXNc):
  EDXNn(RDSDatabase,self).__init__(EDXNh,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,EDXNh,env=EDXNc):
  EDXNn(RDSCluster,self).__init__(EDXNh,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,EDXNh,env=EDXNc):
  EDXNn(AppSyncAPI,self).__init__(EDXNh,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,EDXNh,env=EDXNc):
  EDXNn(AmplifyApp,self).__init__(EDXNh,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,EDXNh,env=EDXNc):
  EDXNn(ElastiCacheCluster,self).__init__(EDXNh,env=env)
class TransferServer(BaseComponent):
 def __init__(self,EDXNh,env=EDXNc):
  EDXNn(TransferServer,self).__init__(EDXNh,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,EDXNh,env=EDXNc):
  EDXNn(CloudFrontDistribution,self).__init__(EDXNh,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)

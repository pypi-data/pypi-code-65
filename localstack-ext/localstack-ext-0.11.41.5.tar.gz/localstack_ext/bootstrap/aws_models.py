from localstack.utils.aws import aws_models
dhGof=super
dhGoC=None
dhGoX=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  dhGof(LambdaLayer,self).__init__(arn)
  self.cwd=dhGoC
  self.runtime=''
  self.handler=''
  self.envvars={}
  self.versions={}
class RDSDatabase(aws_models.Component):
 def __init__(self,dhGoX,env=dhGoC):
  dhGof(RDSDatabase,self).__init__(dhGoX,env=env)
 def name(self):
  return self.dhGoX.split(':')[-1]
class RDSCluster(aws_models.Component):
 def __init__(self,dhGoX,env=dhGoC):
  dhGof(RDSCluster,self).__init__(dhGoX,env=env)
 def name(self):
  return self.dhGoX.split(':')[-1]
# Created by pyminifier (https://github.com/liftoff/pyminifier)

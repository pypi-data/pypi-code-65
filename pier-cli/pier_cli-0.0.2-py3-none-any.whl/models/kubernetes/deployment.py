class Deployment:

	def __init__(self, name):
		self.name = name

	@staticmethod
	def from_k8s_deployment(k8s_deployment):
		return Deployment(k8s_deployment.metadata.name)
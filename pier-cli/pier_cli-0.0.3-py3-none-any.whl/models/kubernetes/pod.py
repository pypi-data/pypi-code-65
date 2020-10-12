class Pod:

	def __init__(self, name):
		self.name = name

	@staticmethod
	def from_k8s_pod(k8s_pod):
		return Pod(k8s_pod.metadata.name)
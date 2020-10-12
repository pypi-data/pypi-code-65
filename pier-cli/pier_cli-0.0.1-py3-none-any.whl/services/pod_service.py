from kubernetes import client, config

from pier_cli.models.kubernetes import Pod, Deployment


class PodService:

    APP_LABEL = { 'app': 'pier' }

    def __init__(self):
        config.load_kube_config()
        self.core_v1_api = client.CoreV1Api()
        self.apps_v1_api = client.AppsV1Api()

    def list_pods(self, namespace='default'):
        return [Pod.from_k8s_pod(kp) for kp in self.core_v1_api.list_namespaced_pod(
            namespace, label_selector=self._label_selector).items]

    def list_deployments(self, namespace='default'):
        return [Deployment.from_k8s_deployment(kd) for kd in self.apps_v1_api.list_namespaced_deployment(
            namespace, label_selector=self._label_selector).items]

    def create_deployment(self, deployment_name, image, namespace='default'):
        labels = {"name": deployment_name, **self.APP_LABEL }

        container = client.V1Container(
            name=deployment_name,
            image=image.name,
            image_pull_policy="IfNotPresent")

        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels=labels),
            spec=client.V1PodSpec(containers=[container]))

        selector = client.V1LabelSelector(match_labels=labels)

        spec = client.V1DeploymentSpec(selector=selector, template=template)

        body = client.V1Deployment(spec=spec, metadata=client.V1ObjectMeta(name=deployment_name, labels=labels))

        api_response = self.apps_v1_api.create_namespaced_deployment(
            namespace, body)

    def delete_deployment(self, deployment, namespace='default'):
        self.apps_v1_api.delete_namespaced_deployment(
            namespace=namespace, name=deployment.name)

    @property
    def _label_selector(self):
        return ''.join([f'{k}={v}' for k,v in self.APP_LABEL.items()])
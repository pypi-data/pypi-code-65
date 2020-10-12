""" For handling success & failure methods and push to batch-monitor """

from .metrics_pusher import MetricsPusher
from prometheus_client import CollectorRegistry, Gauge


class MetricMonitoring:
    """ Handling success & failure methods and push to batch-monitor """
    def __init__(self, job_name):
        self.job = job_name

    def get_metrics_pusher(self):
        metrics_pusher = MetricsPusher(job=self.job)
        metrics_pusher.set_metrics_pod_ips()
        return metrics_pusher

    def push_metrics(self, metrics, metrics_dec):
        metrics_pusher_obj = self.get_metrics_pusher()
        collector_registry = CollectorRegistry()
        labels = {'app_name': self.job}
        gauge_obj = Gauge(metrics,
                          metrics_dec,
                          list(labels.keys()),
                          registry=collector_registry)
        gauge_obj.labels(*labels.values()).set_to_current_time()
        metrics_pusher_obj.push_metrics(collector_registry)

    def push_success_metrics(self):
        self.push_metrics('job_succeeded',
                          'Last time a batch job successfully finished')

    def push_error_metrics(self):
        self.push_metrics('job_error',
                          'Job Failed to finished')

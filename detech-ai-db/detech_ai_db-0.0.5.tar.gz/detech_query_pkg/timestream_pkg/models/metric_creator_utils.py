from .metrics_model import MetricModel

def build_metric_model(metric_id, metric_name, org_id, component_id, 
    namespace, metric_alignment, agent, dimensions, region_name=None,
    is_default=False, description=None, period=60,unit=None, samples=[]):
  return MetricModel(
    metric_id=metric_id,
    metric_name=metric_name, 
    org_id = org_id,
    region_name = region_name,
    namespace = namespace,
    component_id = component_id,
    period = period,
    agent = agent,
    dimensions = dimensions,
    metric_alignment = metric_alignment,
    unit = unit,
    description = description,
    is_default = is_default,
    samples=[]
  )


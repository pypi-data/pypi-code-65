class MetricModel(object):
  """
  MetricModel record
  Args:
    metric (Metric, mandatory): The metric to return, including the metric name, namespace, and dimensions
    period (int, mandatory): The granularity, in seconds, of the returned data points
    stat (str, mandatory): The statistic to return
    unit (str): If you specify a unit, the operation returns only data that was collected with that unit specified
  """
  def __init__(self, metric_id,metric_name, org_id, component_id, namespace, 
  metric_alignment, region_name, agent, dimensions = {},
  is_default=False, description=None, period=60,unit=None, samples=[]):
    self.metric_id = metric_id
    self.metric_name = metric_name
    self.org_id = org_id
    self.region_name = region_name
    self.namespace = namespace
    self.component_id = component_id
    self.period = period
    self.agent = agent
    self.metric_alignment = metric_alignment
    self.unit = unit
    self.description = description
    self.is_default = is_default
    self.samples = samples
    self.dimensions = dimensions

  def get_metric_name(self):
    return self.metric_name

  def to_dict(self):
    """
    Returns a dict representation of a MetricModel instance for serialization.
    Returns:
      dict: Dict populated with self attributes to be serialized
    """
    dictionary = dict(
      metric_id = self.metric_id,
      metric_name=self.metric_name,
      org_id=self.org_id,
      region_name = self.region_name,
      namespace=self.namespace,
      component_id=self.component_id,
      agent=self.agent,
      unit = self.unit,
      period=self.period,
      dimensions=self.dimensions,
      description=self.description,
      metric_alignment=self.metric_alignment,
      samples=self.samples)

    if self.description is not None:
      dictionary.update(description=self.description)
    if self.unit is not None:
      dictionary.update(unit=self.unit)
    return dictionary
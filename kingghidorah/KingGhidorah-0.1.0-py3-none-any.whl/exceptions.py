class _GhidorahError(Exception):
  """
    You shouldn't be using this base class for anything besides inheriting stuff
    """

  def __str__(self):
    return f"\n{self.__class__.__doc__}"


class _UpstreamError(_GhidorahError):
  """
    A catch all error, return information about the error another library gave us.
    """


class _InvalidURL(_GhidorahError):
  """
    The URL you have provided is invalid.
    """


class _NoMoreResources(_GhidorahError):
  """
    The query returned no resources, workflows, or projects in the Database. You forgot to make or upload something!
    """

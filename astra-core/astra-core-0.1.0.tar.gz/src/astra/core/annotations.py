
"""
Provides helpers to implement class and function annotations.
"""

import typing as t

Decorable = t.Union[t.Type, t.Callable]
T_Annotation = t.TypeVar('T_Annotation', bound='Annotation')
_ANNOTATIONS_KEY = '__astra_http_annotations__'


class Annotation:

  @classmethod
  def get(cls: t.Type[T_Annotation], obj: Decorable) -> t.Optional[T_Annotation]:
    return getattr(obj, _ANNOTATIONS_KEY, {}).get(cls)

  def __call__(self, obj: Decorable) -> Decorable:
    registry = getattr(obj, _ANNOTATIONS_KEY, None)
    if registry is None:
      registry = {}
      setattr(obj, _ANNOTATIONS_KEY, registry)
    if type(self) in registry:
      raise RuntimeError(f'{obj!r} already decorated with {type(self).__name__}')
    registry[type(self)] = self
    return obj

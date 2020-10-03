from abc import ABC
from dataclasses import Field
from enum import Enum
from typing import *

from functional import Option, Some

ALLOWED_HTTP_METHODS = \
[
    'get',
    'put',
    'post',
    'delete',
    'options',
    'head',
    'patch',
    'trace',
]

class Model(ABC):
    pass

T = TypeVar('T')
Z = TypeVar('Z')
class Filter(Generic[T], ABC):
    
    def check_value(self, value: T) -> bool:
        raise NotImplementedError
    
    @property
    def decoder(self) -> Optional[Callable[[Z], T]]:
        raise NotImplementedError
    @property
    def encoder(self) -> Optional[Callable[[T], Z]]:
        raise NotImplementedError
    def decode(self, value: Z) -> T:
        raise NotImplementedError
    def encode(self, value: T) -> Z:
        raise NotImplementedError
    
    @classmethod
    def empty(cls) -> Optional['Filter[T]']:
        raise NotImplementedError
    
    @property
    def is_empty(self) -> bool:
        raise NotImplementedError
    
    def mix_with(self, f: 'Filter[T]') -> 'Filter[T]':
        raise NotImplementedError

# region Traits
class HavingId(Model, ABC):
    @property
    def id(self) -> str:
        raise NotImplementedError

class HavingDescription(Model, ABC):
    description: Optional[str]

class HavingExtendedDescription(HavingDescription, ABC):
    summary: Optional[str]
    example: Optional[str]

class HavingPath(Model, ABC):
    name: str
    path: str
    pretty_path: str
    is_top_level: bool
    
    def recursive_update(self, mapping: Callable[['HavingPath', 'HavingPath'], Any], *, ignore_top_level: bool = True):
        raise NotImplementedError

class HavingValue(Model, Generic[T], ABC):
    default: Option[T]
    filter: Optional[Filter[T]]

class HavingStyle(Model, Generic[T], ABC):
    style: Optional[str]
    explode: bool
    allow_reserved: bool
# endregion

# definitions
class ModelEnumData(HavingExtendedDescription, HavingPath, Generic[T], ABC):
    possible_values: List[T]
    base_class: Union['ModelClass', Type[T]]
    
    def check_value(self, value: T) -> bool:
        raise NotImplementedError

class ModelSchema(HavingId, HavingValue[T], HavingExtendedDescription, HavingPath, Generic[T], ABC):
    property_name: Optional[str]
    property_format: Optional[str]
    
    nullable: bool
    read_only: bool
    write_only: bool
    
    cls: Union['ModelClass', ModelEnumData, Type[T]]
    
    @property
    def metadata(self) -> Dict[str, 'ModelSchema']:
        raise NotImplementedError
    @property
    def as_field(self) -> Field:
        raise NotImplementedError

class ModelClass(HavingId, HavingExtendedDescription, HavingPath, ABC):
    properties: Dict[str, ModelSchema]
    required_properties: List[str]
    additional_properties: Union[bool, ModelSchema]
    
    parents: List['ModelClass']
    merged: bool
    
    @property
    def all_properties_iter(self) -> Iterator[Tuple[str, ModelSchema]]:
        raise NotImplementedError
    @property
    def all_properties(self) -> Dict[str, ModelSchema]:
        raise NotImplementedError
    
    @property
    def all_required_properties_iter(self) -> Iterator[str]:
        raise NotImplementedError
    @property
    def all_required_properties(self) -> List[str]:
        raise NotImplementedError

class ModelServerVariable(HavingValue[str], HavingDescription, ABC):
    default: Some[str]

class ParameterType(Enum):
    Query = 'query'
    Header = 'header'
    Path = 'path'
    Cookie = 'cookie'

class ModelEncodingObject(HavingStyle, ABC):
    content_type: str
    headers: Optional[Dict[str, 'ModelParameter']]

class ModelMediaTypeObject(Model, ABC):
    schema: Optional[ModelSchema]
    example: Option[T]
    examples: Optional[Dict[str, T]]
    encoding: Optional[Dict[str, ModelEncodingObject]]

class ModelParameter(HavingId, HavingDescription, HavingStyle, HavingPath, Generic[T], ABC):
    name: str
    required: bool
    parameter_type: ParameterType
    
    deprecated: bool
    allow_empty_value: bool
    
    schema: Optional[ModelSchema]
    content: Optional[Dict[str, ModelMediaTypeObject]]
    example: Option[T]
    examples: Optional[Dict[str, T]]

class ModelExternalDocumentation(HavingDescription, ABC):
    url: str

class ModelServer(HavingDescription, ABC):
    url: str
    variables: Optional[Dict[str, ModelServerVariable]]

class ModelRequestBodyObject(HavingDescription, HavingPath, ABC):
    content: Dict[str, ModelMediaTypeObject]
    required: bool

class ModelResponseObject(HavingDescription, HavingPath, ABC):
    # headers: Optional[Dict[str, ModelParameter]]
    content: Optional[Dict[str, ModelMediaTypeObject]]
    # links: Optional[Dict[str, ModelLinkObject]] # ignored

class ModelEndpoint(HavingId, HavingExtendedDescription, HavingPath, ABC):
    tags: Optional[List[str]]
    external_docs: Optional[ModelExternalDocumentation]
    operation_id: Optional[str]
    request_body: Optional[ModelRequestBodyObject]
    responses: Dict[str, ModelResponseObject]
    default_response: Optional[ModelRequestBodyObject]
    callbacks: Optional[Dict[str, Any]]
    deprecated: bool
    security: Optional[Any]
    servers: Optional[ModelServer]
    
    all_parameters: List[ModelParameter]
    own_parameters: List[ModelParameter]
    parent_parameters: List[ModelParameter]

class ModelPath(HavingId, HavingExtendedDescription, HavingPath, ABC):
    endpoints: Dict[str, ModelEndpoint]
    servers: Optional[ModelServer]
    parameters: List[ModelParameter]
    endpoint_path: str
# endregion


__all__ = \
[
    'ALLOWED_HTTP_METHODS',
    
    'Filter',
    'HavingDescription',
    'HavingExtendedDescription',
    'HavingId',
    'HavingPath',
    'HavingStyle',
    'HavingValue',
    'Model',
    'ModelClass',
    'ModelEncodingObject',
    'ModelEndpoint',
    'ModelEnumData',
    'ModelExternalDocumentation',
    'ModelMediaTypeObject',
    'ModelParameter',
    'ModelPath',
    'ModelRequestBodyObject',
    'ModelResponseObject',
    'ModelSchema',
    'ModelServer',
    'ModelServerVariable',
    'ParameterType',
]

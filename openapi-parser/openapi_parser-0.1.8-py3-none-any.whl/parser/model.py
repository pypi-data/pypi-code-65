from abc import ABC
from dataclasses import Field, dataclass, field
from functools import partial
from typing import *

from dataclasses_json import dataclass_json, LetterCase, config, DataClassJsonMixin
from functional import Option, OptionNone, Some
from typing.re import *

from openapi_parser.model import *
from openapi_parser.util.typing_proxy import extract_generic, GenericProxy
from openapi_parser.util.utils import SearchableEnum
from .filters import *

# region Schemas & Classes
METADATA_KEY = 'openapi-parser'

@dataclass
class HavingPathImpl(HavingPath, ABC):
    name: str = field(init=False)
    path: str = field(init=False)
    is_top_level: bool = field(init=False, default=False)
    
    _pretty_path: str = field(init=False, default=None)
    @property
    def pretty_path(self) -> str:
        return self._pretty_path
    @pretty_path.setter
    def pretty_path(self, value: Optional[str]):
        if (value is None):
            if (self.is_top_level):
                value = self.name
            else:
                value = self.path
        
        self._pretty_path_setter(value)
        self._pretty_path = value
    
    def _pretty_path_setter(self, value: Optional[str]):
        old_value = self._pretty_path
        self._pretty_path = value
        # noinspection PyTypeChecker
        self.recursive_update(partial(type(self)._update_child_pretty_path, old=old_value))
    
    def _child_items(self) -> Iterator[Union[Type, GenericProxy, ModelSchema, HavingPath, None]]:
        raise NotImplementedError
    
    def recursive_update(self, mapping: Callable[[HavingPath, HavingPath], Any], *, ignore_top_level: bool = True):
        children = list(self._child_items())
        i: int = 0
        while i < len(children):
            child = children[i]
            i += 1
            
            if (isinstance(child, ModelSchema)):
                children.extend(find_filters(child.filter, HavingPath))
                child = child.cls
            
            if (child is None):
                continue
            
            # noinspection PyTypeChecker
            is_generic, base, args = extract_generic(child)
            if (not is_generic):
                args = [ base ]
            for cls in args:
                if (isinstance(cls, HavingPath)):
                    if (ignore_top_level and cls.is_top_level):
                        continue
                    else:
                        mapping(self, cls)
                        cls.recursive_update(mapping, ignore_top_level=ignore_top_level)
    
    def _update_child_pretty_path(self, child: HavingPath, *, old: Optional[str]):
        if (old is not None and child.pretty_path.startswith(old)):
            child.pretty_path = self.pretty_path + child.pretty_path[len(old):]
        else:
            child.pretty_path = self.pretty_path + '/' + child.name

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ModelClassImpl(ModelClass, HavingPathImpl, DataClassJsonMixin):
    properties: Dict[str, Union[ModelSchema, Any]] = field(compare=False, hash=False)
    required_properties: List[str] = field(default_factory=list, metadata=config(field_name='required'))
    additional_properties: Union[bool, Union[ModelSchema, Any]] = True
    
    description: Optional[str] = None
    summary: Optional[str] = field(default=None, metadata=config(field_name='title'))
    example: Optional[str] = None
    
    parents: List[ModelClass] = field(init=False, default_factory=list)
    merged: bool = field(init=False, default=False)
    
    def _child_items(self) -> Iterator[Union[Type, GenericProxy, ModelSchema, HavingPath, None]]:
        yield from self.properties.values()
    
    @property
    def all_properties_iter(self) -> Iterator[Tuple[str, ModelSchema]]:
        for p in self.parents:
            yield from p.all_properties_iter
        yield from self.properties.items()
    @property
    def all_properties(self) -> Dict[str, ModelSchema]:
        return dict(self.all_properties_iter)
    
    @property
    def all_required_properties_iter(self) -> Iterator[str]:
        for p in self.parents:
            yield from p.all_required_properties_iter
        yield from self.required_properties
    @property
    def all_required_properties(self) -> List[str]:
        return list(self.all_required_properties_iter)
    
    @property
    def id(self) -> str:
        return self.name

@dataclass
class ClassRef:
    class_path: str
    class_model: ModelClass

@dataclass
class ForwardRef(ClassRef):
    @property
    def class_model(self) -> ModelClass:
        raise ValueError(f"Attempt to load forward-ref '{self.class_path}'")

class PropertyType(SearchableEnum):
    Integer = 'integer'
    Number  = 'number'
    Boolean = 'boolean'
    String  = 'string'
    Array   = 'array'
    Object  = 'object'

MISSING = object()

T = TypeVar('T')
@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ModelSchemaImpl(ModelSchema, DataClassJsonMixin, Generic[T]):
    property_name: str = field(init=False)
    property_type: Optional[PropertyType] = field(default=None, metadata=config(field_name='type'))
    property_format: Optional[str] = field(default=None, metadata=config(field_name='format'))
    description: Optional[str] = None
    summary: Optional[str] = field(default=None, metadata=config(field_name='title'))
    example: Optional[str] = None
    
    default: Option[T] = field(default=OptionNone)
    nullable: bool = False
    read_only: bool = False
    write_only: bool = False
    
    filter: Filter[T] = field(init=False, default_factory=EmptyFilter)
    cls: Union[ModelClass, Type[T]] = field(init=False, default=Any)
    
    def __post_init__(self):
        if (not Option.is_option(self.default)):
            self.default = Some(self.default)
    
    @property
    def metadata(self) -> Dict[str, ModelSchema]:
        return { METADATA_KEY: self }
    
    @property
    def as_field(self) -> Field:
        kwargs = dict()
        if (self.default.non_empty):
            kwargs['default'] = self.default
        
        f = field(metadata=config(metadata=self.metadata, encoder=self.filter.encoder, decoder=self.filter.decoder), **kwargs)
        f.type = self.cls
        return f
    
    @property
    def id(self) -> str:
        return self.property_name


def extract_metadata(f: Field) -> ModelSchema:
    return f.metadata[METADATA_KEY]
# endregion
# region Endpoints

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ModelEncodingObjectImpl(ModelEncodingObject, DataClassJsonMixin):
    content_type: str
    headers: Optional[Dict[str, 'ModelParameter']]
    
    style: Optional[str] = None
    explode: bool = OptionNone
    allow_reserved: bool = False
    
    def __post_init__(self):
        if (self.explode is OptionNone):
            self.explode = self.style == 'form'

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ModelMediaTypeObjectImpl(ModelMediaTypeObject, DataClassJsonMixin):
    schema: Optional[ModelSchema] = None
    example: Option[T] = OptionNone
    examples: Optional[Dict[str, T]] = None
    encoding: Optional[Dict[str, ModelEncodingObjectImpl]] = None
    
    def __post_init__(self):
        if (not isinstance(self.example, Option)):
            self.example = Some(self.example)

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ModelResponseObjectImpl(ModelResponseObject, HavingPathImpl, DataClassJsonMixin):
    description: str
    # headers: Optional[Dict[str, ModelParameter]]
    content: Optional[Dict[str, ModelMediaTypeObjectImpl]] = None
    # links: Optional[Dict[str, ModelLinkObject]] # ignored
    
    def _child_items(self) -> Iterator[Union[Type, GenericProxy, ModelSchema, HavingPath, None]]:
        if (self.content is not None):
            for v in self.content.values():
                yield v.schema

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ModelServerVariableImpl(ModelServerVariable, DataClassJsonMixin):
    default: Some[str] = field(metadata=config(decoder=Some))
    filter: Optional[EnumFilter[T]] = field(init=False, default=None)
    description: Optional[str] = None

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ModelServerImpl(ModelServer, DataClassJsonMixin):
    url: str
    description: Optional[str] = None
    variables: Optional[Dict[str, ModelServerVariableImpl]] = None

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ModelParameterImpl(ModelParameter, HavingPathImpl, DataClassJsonMixin):
    name: str = field(init=True)
    parameter_type: ParameterType = field(metadata=config(field_name='in'))
    description: Optional[str] = None
    
    required: bool = False
    deprecated: bool = False
    allow_empty_value: bool = False
    
    schema: Optional[ModelSchema] = None
    content: Optional[Dict[str, ModelMediaTypeObjectImpl]] = None
    example: Option[T] = OptionNone
    examples: Optional[Dict[str, T]] = None
    
    style: Optional[str] = None
    explode: bool = OptionNone
    allow_reserved: bool = False
    
    def __post_init__(self):
        if (self.explode is OptionNone):
            self.explode = self.style == 'form'
        if (not isinstance(self.example, Option)):
            self.example = Some(self.example)
    
    @property
    def id(self) -> str:
        return self.name
    
    def _child_items(self) -> Iterator[Union[Type, GenericProxy, ModelSchema, HavingPath, None]]:
        yield self.schema
        if (self.content is not None):
            for v in self.content.values():
                yield v.schema

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ModelRequestBodyObjectImpl(ModelRequestBodyObject, HavingPathImpl, DataClassJsonMixin):
    content: Dict[str, ModelMediaTypeObjectImpl]
    description: Optional[str] = None
    required: bool = False
    
    def _child_items(self) -> Iterator[Union[Type, GenericProxy, ModelSchema, HavingPath, None]]:
        if (self.content is not None):
            for v in self.content.values():
                yield v.schema

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ModelEndpointImpl(ModelEndpoint, HavingPathImpl, DataClassJsonMixin):
    responses: Dict[str, ModelResponseObject]
    tags: Optional[List[str]] = None
    # external_docs: Optional[ModelExternalDocumentationImpl] = None
    operation_id: Optional[str] = None
    request_body: Optional[ModelRequestBodyObject] = None
    default_response: Optional[ModelResponseObject] = field(init=False)
    callbacks: Optional[Dict[str, Any]] = None
    deprecated: bool = False
    security: Optional[Any] = None
    servers: Optional[ModelServerImpl] = None
    
    own_parameters: List[ModelParameter] = field(default_factory=list, metadata=config(field_name='parameters'))
    parent_parameters: List[ModelParameter] = field(init=False, default_factory=list)
    all_parameters: List[ModelParameter] = field(init=False, default_factory=list)
    
    description: Optional[str] = None
    summary: Optional[str] = None
    example: Optional[str] = field(init=False, default=None)
    
    @property
    def id(self) -> str:
        return self.operation_id
    
    @property
    def name(self) -> str:
        return self.operation_id
    
    def _child_items(self) -> Iterator[Union[Type, GenericProxy, ModelSchema, HavingPath, None]]:
        yield self.request_body
        yield self.default_response
        yield from self.responses.values()
        yield from self.own_parameters

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ModelPathImpl(ModelPath, HavingPathImpl, DataClassJsonMixin):
    endpoints: Dict[str, ModelEndpoint] = field(init=False, default_factory=dict)
    servers: Optional[ModelServerImpl] = None
    parameters: List[ModelParameter] = field(default_factory=list)
    
    description: Optional[str] = None
    summary: Optional[str] = None
    example: Optional[str] = field(init=False, default=None)
    
    endpoint_path: str = field(init=False)
    @property
    def id(self) -> str:
        return self.endpoint_path
    
    def _child_items(self) -> Iterator[Union[Type, GenericProxy, ModelSchema, HavingPath, None]]:
        yield from self.parameters
        yield from self.endpoints.values()
    
    @property
    def name(self) -> str:
        return self.endpoint_path

# endregion

__all__ = \
[
    'ClassRef',
    'ForwardRef',
    'HavingPathImpl',
    'ModelClassImpl',
    'ModelEncodingObjectImpl',
    'ModelEndpointImpl',
    'ModelMediaTypeObjectImpl',
    'ModelParameterImpl',
    'ModelPathImpl',
    'ModelRequestBodyObjectImpl',
    'ModelResponseObjectImpl',
    'ModelSchemaImpl',
    'ModelServerImpl',
    'ModelServerVariableImpl',
    'PropertyType',
    
    'extract_metadata',
]


# Auto generated from issue_106.yaml by pythongen.py version: 0.4.0
# Generation date: 2020-08-25 16:45
# Schema: test_106
#
# id: https://issue_test/106/schema
# description:
# license:

import dataclasses
import sys
from typing import Optional, List, Union, Dict, ClassVar, Any
from dataclasses import dataclass
from biolinkml.utils.slot import Slot
from biolinkml.utils.metamodelcore import empty_list, empty_dict, bnode
from biolinkml.utils.yamlutils import YAMLRoot, extended_str, extended_float, extended_int
if sys.version_info < (3, 7, 6):
    from biolinkml.utils.dataclass_extensions_375 import dataclasses_init_fn_with_kwargs
else:
    from biolinkml.utils.dataclass_extensions_376 import dataclasses_init_fn_with_kwargs
from biolinkml.utils.formatutils import camelcase, underscore, sfx
from rdflib import Namespace, URIRef
from biolinkml.utils.curienamespace import CurieNamespace


metamodel_version = "1.5.3"

# Overwrite dataclasses _init_fn to add **kwargs in __init__
dataclasses._init_fn = dataclasses_init_fn_with_kwargs

# Namespaces
XSD = CurieNamespace('xsd', 'http://example.org/UNKNOWN/xsd/')
DEFAULT_ = CurieNamespace('', 'https://issue_test/106/schema/')


# Types
class String(str):
    """ A character string """
    type_class_uri = XSD.string
    type_class_curie = "xsd:string"
    type_name = "string"
    type_model_uri = URIRef("https://issue_test/106/schema/String")


# Class references



@dataclass
class C1(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("https://issue_test/106/schema/C1")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "c1"
    class_model_uri: ClassVar[URIRef] = URIRef("https://issue_test/106/schema/C1")

    s1: Optional[str] = None
    s2: Optional[str] = None

@dataclass
class C2(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("https://issue_test/106/schema/C2")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "c2"
    class_model_uri: ClassVar[URIRef] = URIRef("https://issue_test/106/schema/C2")

    s1: Optional[str] = None


# Slots
class slots:
    pass

slots.s1 = Slot(uri=DEFAULT_.s1, name="s1", curie=DEFAULT_.curie('s1'),
                      model_uri=DEFAULT_.s1, domain=None, range=Optional[str])

slots.s2 = Slot(uri=DEFAULT_.s2, name="s2", curie=DEFAULT_.curie('s2'),
                      model_uri=DEFAULT_.s2, domain=None, range=Optional[str])
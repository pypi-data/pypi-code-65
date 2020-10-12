from flask import current_app
from importlib import import_module
from .policy import Policy

def import_class(name):
    #
    # imports class from string 'name' 
    #

    components = name.split('.')
    module_name = '.'.join(components[:-1])
    mod = import_module(module_name)
    cls = getattr(mod, components[-1])
    return cls

def get_policy_class():
    #
    # returns policy class
    #

    if current_app.config.get('CLASSNAME_POLICY'):
        return import_class(current_app.config.get('CLASSNAME_POLICY'))

    return Policy

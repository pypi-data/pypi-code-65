#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sanic_jinja2 import Environment, PackageLoader, TemplateNotFound
from jinja2 import FileSystemLoader
from .plugin import sanic_jinja2, SanicJinja2

__version__ = '0.8.0'

__all__ = ['sanic_jinja2', 'Environment', 'PackageLoader', 'FileSystemLoader',
           'TemplateNotFound']


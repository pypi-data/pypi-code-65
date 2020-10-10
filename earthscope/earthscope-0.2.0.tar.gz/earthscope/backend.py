from ipywidgets import DOMWidget, trait_types, Output, VBox, Textarea
from traitlets import Unicode, Int, List, Float, Dict
from improc.dbops import parse
from concurrent.futures import ThreadPoolExecutor
import threading, time

import sys
import logging
import requests
logger = logging.getLogger(__name__)

from .package_version import package_version
    
# TODO: consider moving more geojson related fetching/state logic from Map.js into here
class Earthscope(DOMWidget):
    _view_name = Unicode('EarthscopeWidget').tag(sync=True)
    _model_name = Unicode('EarthscopeModel').tag(sync=True)
    _view_module = Unicode('@ceresimaging/earthscope').tag(sync=True)
    _model_module = Unicode('@ceresimaging/earthscope').tag(sync=True)

    _view_module_version = Unicode(package_version).tag(sync=True)
    _model_module_version = Unicode(package_version).tag(sync=True)

    sources = List(Dict).tag(sync=True)

    # TODO: make the center attribute set happen here instead of in Map.js
    zoom = Float().tag(sync=True)

    def __init__(self, sources, *args, **kwargs):
        self.sources = sources
        super(Earthscope, self).__init__(*args, **kwargs)

    def add_source(self, source_id):
        if source_id in self.sources:
            return

        new_source = create_source_config(source_id)
        self.sources = self.sources + [new_source]

# TODO: don't hardcode tileserver url on the backend
base_tile_url = None
def setup(base_url='https://improc.ceresimaging.net/hub/user-redirect/tileserver/flights', tile_url='/tiles/{z}/{x}/{y}'):
    global base_tile_url
    base_tile_url = base_url + tile_url
setup()

def view(source_ids):
    global base_tile_url

    source_ids = list(set(source_ids))
    sources = list(map(create_source_config, source_ids))

    return Earthscope(sources) 

def create_source_config(source_id):
    source = {}
    if source_id.endswith(".tif"):
        source = {
            'displayName': parse.get_camera_or_type(source_id),
            'type': 'raster',
            'sourceId': source_id,
            'source': {
                'type': 'raster',
                # TODO: don't hardcode tileserver url on the backend
                'tiles': [base_tile_url + source_id],
                'tileSize': 256,
            },
        }
    elif source_id.endswith(".shp"):
        source = {
            'displayName': 'field borders',
            'type': 'geojson',
            'sourceId': source_id
        }
    else:
        logger.warning(f"not sure how to load {source_id} - unknown data type")

    return source

def get_first_raster_source(sources):
    return next(x for x in sources if x['type'] == 'raster')
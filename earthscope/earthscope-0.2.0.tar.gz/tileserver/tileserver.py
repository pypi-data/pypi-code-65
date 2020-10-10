import os, io, logging
from pathlib import Path

from flask import Flask, g, request, jsonify, send_file, redirect, url_for
from flask_cors import CORS

import mercantile
import mapnik

from improc.gis.shapetools import convert_shapefile_to_geojson

from tileserver.convert_to_rgb_8bit import convert_to_rgb_8bit_if_needed
from tileserver.tiff_io import sniff_tiff_shape

logging.basicConfig()

logger = logging.getLogger(__name__)
app = Flask(__name__)
CORS(app)

URL_BASE = os.environ.get('IMAGE_TILER_URL_PREFIX', "/flights")
CERES_FLIGHTS_DIR = Path(os.environ.get('CERES_FLIGHTS_DIR', './flights'))

MAPNIK_STYLE = """
    <Map>
        <Style filter-mode="first" name="imagery">
            <Rule>
            <RasterSymbolizer comp-op="dst-over" opacity="1" scaling="bilinear" />
            </Rule>
        </Style>
        <Layer name="imagery">
            <StyleName>imagery</StyleName>
        </Layer>
    </Map>
"""

TILE_SIZE=(1024,1024)

def path_to_static_tiffs(tiff_key):
    return (CERES_FLIGHTS_DIR / tiff_key).resolve() if tiff_key else None

def path_to_static_shapefile(shapefile_key):
    return (CERES_FLIGHTS_DIR / shapefile_key).resolve() if shapefile_key else None

def mapnik_datasource(tiff_path):
    return mapnik.Datasource(
        type='gdal',
        file=str(tiff_path)
    )

def add_layer_to_map(map, tiff_path):
    datasource = mapnik_datasource(tiff_path)

    # Initialize map with the style XML
    mapnik.load_map_from_string(map, MAPNIK_STYLE)

    # Set the datasource on the layer to our GDAL TIFF path
    layer = map.layers[0]
    layer.datasource = datasource

def zoom_to_tile_extent(map, x, y, z):
    bbox = mercantile.bounds(x, y, z)    
    map.zoom_to_box(mapnik.Box2d(bbox.west, bbox.south, bbox.east, bbox.north))

def rasterize_to_png(map):
    tile = mapnik.Image(map.width, map.height)
    mapnik.render(map, tile)

    # For examples of flags and options besides png32, you could check out:
    # https://github.com/mapnik/python-mapnik/blob/8481096ebaa94e907a505c1dc6bebec4294ab19f/test/python_tests/png_encoding_test.py#L23-L38
    raster = tile.tostring('png32')

    return raster

def calculate_center(datasource):
    extents = datasource.envelope()
    lat = (extents.miny + extents.maxy)/2.0
    lon = (extents.minx + extents.maxx)/2.0
    return [lon, lat]

def get_fit_bounds(datasource):
    extents = datasource.envelope()
    return [[extents.minx, extents.miny], [extents.maxx, extents.maxy]]

def render_map_for(tiff_key, tile_size=TILE_SIZE, before_render=lambda map: None):
    tiff_path = path_to_static_tiffs(tiff_key)

    if not tile_size:
        tile_size = reversed(sniff_tiff_shape(tiff_path))

    map = mapnik.Map(*tile_size)

    # This is required or our very explicit tile sizes will be overridden
    map.aspect_fix_mode=mapnik.aspect_fix_mode.RESPECT

    tiff_path = convert_to_rgb_8bit_if_needed(tiff_path)
    add_layer_to_map(map, tiff_path)

    # Run provided function prior to rendering, often zooms to
    # the appropriate extent for the time, but could do other stuff
    before_render(map)

    png = rasterize_to_png(map)
    
    return send_file(io.BytesIO(png), mimetype='image/png')

@app.route(f"{URL_BASE}/tiles/<int:z>/<int:x>/<int:y>/<path:tiff_key>")
def tiles(z=None, x=None, y=None, tiff_key=None):
    zoom_map_to_tile = lambda map: zoom_to_tile_extent(map, x, y, z)
    return render_map_for(tiff_key, before_render=zoom_map_to_tile)

@app.route(f"{URL_BASE}/png/<path:tiff_key>")
def png(tiff_key):
    zoom_map_to_fit_all = lambda map: map.zoom_all()
    return render_map_for(tiff_key, tile_size=None, before_render=zoom_map_to_fit_all)

@app.route(f"{URL_BASE}/geojson/<path:shapefile_key>")
def geojson(shapefile_key):
    shapefile_path = path_to_static_shapefile(shapefile_key)
    return convert_shapefile_to_geojson(shapefile_path)

@app.route(f"{URL_BASE}/center/<path:tiff_key>")
def center(tiff_key):
    tiff_path = path_to_static_tiffs(tiff_key)
    datasource = mapnik_datasource(tiff_path)
    center = calculate_center(datasource)
    return jsonify(center)

@app.route(f"{URL_BASE}/extents/<path:tiff_key>")
def extents(tiff_key):
    tiff_path = path_to_static_tiffs(tiff_key)
    datasource = mapnik_datasource(tiff_path)
    bounds = get_fit_bounds(datasource)
    return jsonify(bounds)

@app.after_request
def add_header(response):
    response.cache_control.max_age = 300 # secs
    return response

@app.route('/', methods=['GET'])
def tile_test():
    return redirect(url_for('static', filename='tile-tester.html'))

print("""
If you used the default local-flights-setup.sh script with the default configuration the following might work:
    http://localhost:9090/services/image-tiler/flights/png/Flight%2011290/registered/2020-07-27%2056968%20Overman%20VNIR.tif
""")

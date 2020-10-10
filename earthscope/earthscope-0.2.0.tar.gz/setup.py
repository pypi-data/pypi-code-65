import pathlib, json
from setuptools import setup, find_packages

DOT = pathlib.Path(__file__).parent
package_json = json.loads((DOT / "package.json").read_text())

setup(
    name="earthscope",
    version=package_json['version'],
    description="GeoTIFF viewer for JupyterLab",
    long_description="long description is long",
    long_description_content_type="text/markdown",
    url="https://github.com/ceresimaging/earthscope",
    author="Seth Nickell",
    author_email="snickell@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(),
    entry_points={
        'jupyter_serverproxy_servers': [
            # Register the tileserver/ endpoint on our jupyter-hub
            # to start the command line returned by earthscope/tileserver/register_jupyter_endpoint.py
            'tileserver = tileserver:register_jupyter_endpoint',
        ]
    },
    include_package_data=True,
    install_requires=[
      "jupyter-server-proxy",
      "ipywidgets",
      "traitlets",
      "rasterio",
      'importlib-metadata ~= 1.0 ; python_version < "3.8"',
    ],
)

from pathlib import Path

# This command is what is launched automatically by jupyter-server-proxy 
# to create the tile/ url endpoint on jupyter-hub, so in a sense, this
# is the command for launching the "prod version" of the tielserver
def register_jupyter_endpoint():
  print("earthscope.tileserver.__init__.py:setup_tileserver(): registering tileserver/ endpoint and command with jupyter-server-proxy")
  return {
    'command': ['python3', '-m', 'flask', 'run', '-p', '{port}', '--with-threads'],
    'timeout': 30,
    'environment': {
      # we're using system python3-mapnik deb package from ubuntu
      # installed in the improc-notebook.dockerfile
      # building python-mapnik head is/was really hard, this
      # will work as long as the /opt/conda/bin python version
      # matches ubuntu, but yeah, its a littler perilous
      'PYTHONPATH': '/usr/lib/python3/dist-packages',
      'FLASK_APP': 'tileserver.tileserver',
      'FLASK_ENV': 'development',
      'BASE_URL_NOTEBOOK': '{base_url}',
      'CERES_FLIGHTS_DIR': str(Path.home() / 'flights'),
    },
    'port': 9010,
  }
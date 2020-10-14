# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['faststan', 'faststan.cli', 'faststan.wrappers']

package_data = \
{'': ['*']}

install_requires = \
['asyncio-nats-client>=0.10.0,<0.11.0',
 'asyncio-nats-streaming>=0.4.0,<0.5.0',
 'loguru>=0.5.3,<0.6.0',
 'pydantic>=1.6,<2.0',
 'returns>=0.14.0,<0.15.0',
 'typer>=0.3.2,<0.4.0']

entry_points = \
{'console_scripts': ['nats = faststan.cli.nats:app',
                     'stan = faststan.cli.stan:app']}

setup_kwargs = {
    'name': 'faststan',
    'version': '0.20.0',
    'description': 'Build data streaming pipelines using NATS or NATS streaming',
    'long_description': '# FastSTAN\n\n<a href="https://gitlab.com/faststan/faststan/-/commits/next"><img alt="Pipeline status" src="https://gitlab.com/faststan/faststan/badges/next/pipeline.svg"></a>\n<a href="https://gitlab.com/faststan/faststan/-/commits/next"><img alt="Coverage report" src="https://gitlab.com/faststan/faststan/badges/next/coverage.svg"></a>\n<a href="https://python-poetry.org/docs/"><img alt="Packaging: poetry" src="https://img.shields.io/badge/packaging-poetry-blueviolet"></a>\n<a href="https://flake8.pycqa.org/en/latest/"><img alt="Style: flake8" src="https://img.shields.io/badge/style-flake8-ff69b4"></a>\n<a href="https://black.readthedocs.io/en/stable/"><img alt="Format: black" src="https://img.shields.io/badge/format-black-black"></a>\n<a href="https://docs.pytest.org/en/stable/"><img alt="Packaging: pytest" src="https://img.shields.io/badge/tests-pytest-yellowgreen"></a>\n<a href="https://pypi.org/project/faststan/"><img alt="PyPI" src="https://img.shields.io/pypi/v/faststan"></a>\n<a href="https://faststan.gitlab.io/faststan/"><img alt="Documentation" src="https://img.shields.io/badge/docs-mkdocs-blue"></a>\n<a href="https://opensource.org/licenses/MIT"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>\n[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://gitlab.com/faststan/faststan)\n\nEasily deploy NATS and NATS Streaming subscribers using Python.\n\n## Features\n\n- Define subscribers using sync and async python functions\n- Automatic data parsing and validation using type annotations and pydantic\n- Support all subscription configuration available in stan.py and nats.py\n- Start subscriptions or services from command line\n- Publish messages from command line\n\n## Quick start\n\n- Install the package from pypi:\n\n```bash\npip install faststan\n```\n\n### Using the command line\n\nCreate your first NATS subscriber:\n\n- Create a file named `app.py` and write the following lines:\n\n```python\nfrom pydantic import BaseModel\n\nclass NewEvent(BaseModel):\n    name: str\n    datetime: int\n\ndef on_event(event: NewEvent):\n    print(f"INFO :: Received new message: {event}")\n```\n\n- Start your subscriber:\n\n```shell\nnats sub start demo --function app:on_event\n```\n\n- Publish a message:\n\n```shell\nnats pub demo --name "John Doe" --datetime 1602661983\n```\n\nNATS Streaming behave the same way:\n\n- Define your subscription:\n\n```python\nfrom pydantic import BaseModel\n\n\nclass Greetings(BaseModel):\n    message: str\n\ndef on_event(event: NewEvent) -> Greetings:\n    print(f"Info :: Received new request.")\n    return Greetings(message=f"Welcome to {event.name}!"\n```\n\n- Start it using `stan sub start` command:\n\n```shell\nstan sub start demo --function app:on_event\n```\n\n- And publish message using `stan pub` command:\n\n```shell\nstan pub demo --name "John Doe"\n```\n\n### Using Python API\n\nIn this example, we will build a machine learning service that perform a prediction using an ONNX model. This service will be impletended using the [request/reply] pattern.\n\nBefore running the example, make sure you have the dependencies installed:\n\n- `onnxruntime`\n- `numpy`\n- `httpx`\n\n```python\nimport asyncio\nfrom typing import List, Dict\nfrom faststan.nats import FastNATS\nfrom pydantic import BaseModel, validator\n\nfrom httpx import AsyncClient\nimport numpy as np\nimport onnxruntime as rt\n\n\nasync def load_predictor(\n    app: FastNATS,\n    url: str = "https://s3-per-grenoble.ams3.digitaloceanspaces.com/models/rf_iris.onnx",\n) -> None:\n    """Load an ONNX model and return a predictor for this model."""\n\n    async with AsyncClient() as http_client:\n        http_response = await http_client.get(url)\n\n    sess = rt.InferenceSession(http_response.content)\n\n    input_name = sess.get_inputs()[0].name\n    label_name = sess.get_outputs()[0].name\n    proba_name = sess.get_outputs()[1].name\n\n    def predict(data: np.ndarray):\n        """Perform prediction for given data."""\n        return sess.run([label_name, proba_name], {input_name: data})\n\n    app.state["predictor"] = predict\n\n\nclass Event(BaseModel):\n    """Incoming data expected by the predictor."""\n\n    values: np.ndarray\n    timestamp: int\n\n    @validator("values", pre=True)\n    def validate_array(cls, value):\n        """Cast data to numpy array with float32 precision.\n\n        A ValidationError will be raise if any error is raised in this function.\n        """\n        return np.array(value, dtype=np.float32)\n\n    class Config:\n        # This must be set to True in order to let pydantic handle numpy types\n        arbitrary_types_allowed = True\n\n\nclass Result(BaseModel):\n    """Result returned by the predictor."""\n\n    probabilities: List[\n        Dict[int, float]\n    ]  # Example: [{ 0: 0.25, 1:0.75}, {0: 0.15, 1: 0.85}]\n    labels: List[int]  # Example: [1, 1]\n\n\napp = FastNATS()\napp.state = {}\n\nawait load_predictor(app)\nawait app.connect()\n\n\n@app.reply("predict")\ndef predict(event: Event) -> Result:\n    print(f"{event.timestamp} :: Received new event data")\n    labels, probas = app.state["predictor"](event.values)\n    return {"probabilities": probas, "labels": labels.tolist()}\n\n\nawait app.start()\n```\n\n- You can now publish messages on the service:\n\n```python\nfrom faststan import FastNATS\n\n\nasync with FastNATS() as nats_client:\n    reply_msg = await nats_client.request_json(\n        "predict", {"values": [[0, 0, 0, 0]], "timestamp": 1602661983}\n    )\n\nprint(f"Received a reply: {reply_msg}")\n```\n',
    'author': 'gcharbon',
    'author_email': 'guillaume.charbonnier@capgemini.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/faststan/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

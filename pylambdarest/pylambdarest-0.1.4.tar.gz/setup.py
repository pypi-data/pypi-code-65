# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pylambdarest']

package_data = \
{'': ['*']}

install_requires = \
['jsonschema>=3.2.0,<4.0.0']

setup_kwargs = {
    'name': 'pylambdarest',
    'version': '0.1.4',
    'description': 'Lightweight framework for building REST API using AWS Lambda + API Gateway',
    'long_description': '# pylambdarest\n\n[![CI/CD Status](https://github.com/MarwanDebbiche/pylambdarest/workflows/CI%2FCD/badge.svg?branch=master)](https://github.com/MarwanDebbiche/pylambdarest/actions?query=branch:master)\n[![Coverage Status](https://coveralls.io/repos/github/MarwanDebbiche/pylambdarest/badge.svg?branch=master)](https://coveralls.io/github/MarwanDebbiche/pylambdarest?branch=master)\n\npylambdarest is a lightweight framework for building REST API using AWS Lambda + API Gateway.\n\nUnlike most of other Python frameworks, it does not provide any routing capability. The routing should be handled by API Gateway itself.\n\nBasically, it provides a `@route` decorator to parse the API Gateway event into a `Request` object accessible from the handler function as an argument. It also formats the handler\'s output to the expected Lambda + API Gateway format seamlessly.\n\nTurning this:\n\n```python\nimport json\n\ndef handler(event, context):\n    body = json.loads(event["body"])\n    query_params = event["queryStringParameters"]\n    path_params = event["pathParameters"]\n\n    return {\n        "statusCode": 200,\n        "body": json.dumps({\n            "message": f"Hello from AWS Lambda {body[\'name\']}!!"\n        })\n    }\n\n```\n\nInto this:\n\n```python\nfrom pylambdarest import route\n\n@route()\ndef handler(request):\n    body = request.json\n    query_params = request.query_params\n    path_params = request.path_params\n\n    return 200, {"message": f"Hello from AWS Lambda {body[\'name\']}!!"}\n```\n\n\nYou can still access the original `event` and `context` arguments from the handler:\n\n```python\nfrom pylambdarest import route\n\n@route()\ndef handler(request, event, context):\n    print(event)\n    print(context)\n    body = request.json\n\n    return 200, {"message": f"Hello from AWS Lambda {body[\'name\']}!!"}\n```\n\n<br/>\n\nPath parameters defined in API Gateway can also be accessed directly as function argument:\n\n<br/>\n\n![api-gateway-path-params](https://raw.githubusercontent.com/MarwanDebbiche/pylambdarest/master/images/api-gateway-path-params.png)\n\n```python\nfrom pylambdarest import route\n\n@route()\ndef get_user(user_id):\n    print(user_id)\n\n    # get user from db\n    user = {"id": user_id, "name": "John Doe"}\n\n    return 200, user\n```\n\n## Schema Validation\n\npylambdarest also provides basic schema validation using [jsonschema](https://github.com/Julian/jsonschema):\n\n```python\nfrom pylambdarest import route\n\nuser_schema = {\n    "type": "object",\n    "properties": {\n        "name": {"type": "string"}\n    },\n    "required": ["name"],\n    "additionalProperties": False\n}\n\n@route(body_schema=user_schema)\ndef create_user(request):\n    # If the request\'s body does not\n    # satisfy the user_schema,\n    # a 400 will be returned\n\n    # Create user here\n\n    return 201\n\n\nquery_params_schema = {\n    "type": "object",\n    "properties": {\n        # Only string types are allowed for query parameters.\n        # Types casting should be done in the handler.\n        "page": {"type": "string"}\n    },\n    "additionalProperties": False\n}\n\n@route(query_params_schema=query_params_schema)\ndef get_users(request):\n    page = int(request.query_params.get("page", 1))\n\n    # request users in db\n    users = [\n        {"userId": i}\n        for i in range((page - 1) * 50, page * 50)\n    ]\n\n    return 200, users\n```\n\n## Motivation\n\nWhy another framework ?\n\nWhen using API Gateway and python Lambdas, the most common pattern is to have one unique Lambda triggered by a proxy API Gateway resource. The Lambda then uses a framework like Flask to do all the routing. In an API Gateway + Lambda context, I feel like **the routing should be handled by API Gateway itself**, then forwarding the request to specific Lambda functions for each resource or endoint.\n\nN.B: I find it useful to declare the API Gateway -> Lambda routing using the amazing [serverless](https://www.serverless.com/) framework\n\n## Installation\n\nYou can install pylambdarest using pip:\n\n```\npip install pylambdarest\n```\n\npylambdarest should also be included in the deployment package of your Lambdas. If you use the serverless framework to manage your deployment, this can be done easily using the [serverless-python-requirements](https://github.com/UnitedIncome/serverless-python-requirements) plugin.\n\nTo speed-up your API development, I also recommend using the [serverless-offline](https://github.com/dherault/serverless-offline) plugin.\n\nYou can look at the [sample](https://github.com/MarwanDebbiche/pylambdarest/tree/master/sample) to have a working example of this set-up.\n',
    'author': 'Marwan Debbiche (Macbook Pro)',
    'author_email': 'marwan.debbiche@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MarwanDebbiche/pylambdarest',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)

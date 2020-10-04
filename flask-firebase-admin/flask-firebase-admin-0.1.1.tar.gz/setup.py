# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flask_firebase_admin']

package_data = \
{'': ['*']}

install_requires = \
['firebase-admin>=4.0.0,<5.0.0', 'flask>=1.0.0,<2.0.0']

setup_kwargs = {
    'name': 'flask-firebase-admin',
    'version': '0.1.1',
    'description': 'Firebase for Flask',
    'long_description': '# Flask Firebase Admin\n\nAdd Firebase (a Firebase Admin app) to a Flask application.\n\n## Installation\n\n```bash\npip install flask-firebase-admin\n```\n\n## Quickstart\n\nIn the simplest case, let\'s protect a route, specifically, we\'ll require a user to provide a firebase jwt to one of our routes:\n\n```python\nfrom flask import Flask\nfrom flask_firebase_admin import FirebaseAdmin\n\napp = Flask(__name__)\nfirebase = FirebaseAdmin(app) # uses GOOGLE_APPLICATION_CREDENTIALS\n\n@app.route("/unprotected")\ndef unprotected():\n    return {"message": "Hello from unprotected route!"}\n\n@app.route("/protected")\n@firebase.jwt_required  # This route now requires authorization via firebase jwt\ndef protected():\n    return {"message": "Hello from protected route!"}\n\nif __name__ == "__main__":\n    app.run(debug=True)\n```\n\nAssuming the code above is located in a module named `app.py`, start the Flask application:\n\n```bash\nGOOGLE_APPLICATION_CREDENTIALS="/path/to/service_account.json" python app.py\n```\n\nAnd in a separate terminal window, ping the unprotected route:\n\n```bash\n$ curl http://127.0.0.1:5000/unprotected\n{\n  "message": "Hello from unprotected route!"\n}\n```\n\nLooks good. Now the protected route:\n\n```bash\n$ curl http://127.0.0.1:5000/protected\n{\n  "error": {\n    "message": "No credentials provided"\n  }\n}\n```\n\nOK, makes sense. Now with some credentials:\n\n```bash\n$ TOKEN="your-firebase-token ..."\n$ curl -H "Authorization: JWT ${TOKEN}" http://127.0.0.1:5000/protected\n{\n  "message": "Hello from protected route!"\n}\n```\n\nExcellent. We now have a application with routes (one route) which require the user to provide their Firebase JWT!\n\n- `request.user`\n- configuration\n  - sample with explicitly providing service account\n  - changing authorization scheme\n  - other config\n- aliased modules\n',
    'author': 'Andrew Ross',
    'author_email': 'andrew.ross.mail@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/andrewrosss/flask-firebase-admin',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

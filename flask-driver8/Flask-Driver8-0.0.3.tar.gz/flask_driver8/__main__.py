from flask import Flask
from flask_driver8 import driver8_blueprint

app = Flask(__name__)
app.register_blueprint(driver8_blueprint.driver8_blueprint)


def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()

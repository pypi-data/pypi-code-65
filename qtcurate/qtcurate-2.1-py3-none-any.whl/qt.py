from qtcurate.config import BASE_URL


class Qt:
    api_key = None
    url = None

    @staticmethod
    def init(key: str, environment: str = "") -> None:
        Qt.api_key = key
        if environment != "":
            environment = f"{environment}."
        Qt.url = f"http://{environment}{BASE_URL}"

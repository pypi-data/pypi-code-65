import json
import os

class Meta:
    def __init__(self):
        self.__dict__.update(
            json.loads(
                open(
                    os.path.abspath(
                        os.path.join(
                            os.path.dirname(
                                os.path.dirname(__file__)
                            ),
                            'METADATA.json'
                        )
                    )
                ).read()
            )
        )

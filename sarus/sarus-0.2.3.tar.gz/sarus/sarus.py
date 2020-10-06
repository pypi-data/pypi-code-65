"""
   Copyright 2020 Sarus SAS

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

   Sarus library to leverage sensitive data without revealing them

   This lib contains classes and method to browse,
   learn from & explore sensitive datasets.
   It connects to a Sarus server, which acts as a gateway, to ensure no
   results/analysis coming out of this lib are sensitive.
"""
import requests
import tempfile
import tarfile
import textwrap
import cloudpickle
import tensorflow as tf
import io
import os
import sys
import re
import json
import matplotlib.pyplot as plt
import time
import getpass
import base64
import numpy as np
import pandas as pd
from PIL import Image


class Dataset:
    """
    A class based on tf.data.dataset to provide a representation of datasets
    used by Sarus, remotely.
    To be shared by client & server.
    """

    def __init__(
        self,
        name,
        id,
        client,
        type_metadata=None,
        URI=None,
        human_description=None,
        marginals=None,
        columns=None,
        target_delta=None,
        max_epsilon=None,
    ):
        self.name = name
        self.id = id
        self.client = client
        try:
            self.type_metadata = json.loads(type_metadata)
        except Exception:
            self.type_metadata = None
        self.URI = URI
        self.columns = columns
        self.human_description = human_description
        self._synthetic = None
        self._synthetic_rows_number = None
        try:
            self.marginals = json.loads(marginals)
        except Exception:
            self.marginals = None
        self.target_delta = target_delta
        self.max_epsilon = max_epsilon

    @classmethod
    def from_dict(cls, data, client):
        """Get a dataset from the json data sent by the server"""
        return cls(
            data.get("name"),
            data.get("id"),
            client,
            type_metadata=data.get("type_metadata"),
            marginals=data.get("marginals"),
            URI=data.get("URI"),
            human_description=data.get("human_description"),
            target_delta=data["privacy_accountant"].get("target_delta"),
            max_epsilon=data["privacy_accountant"].get("max_epsilon"),
        )

    @property
    def epsilon(self):
        resp = requests.get(
            f"{self.client.base_url}/datasets/{self.id}",
            cookies=self.client.cookies,
            verify=self.client.verify,
        )
        if resp.status_code > 200:
            raise Exception(
                f"Error while retrieving the current value of epsilon. "
                f"Gateway answer was: \n{resp}"
            )
        return resp.json()["privacy_accountant"]["current_epsilon"]

    def synthetic(self, rows_number=None, force_refresh=False):
        """
        Returns synthetic data as a pandas dataframe, downloading them if they
        are not cached yet.

        Args:
            rows_number (int): number of rows to return
            force_refresh: if True, does not use cache

        Returns:
            pandas.DataFrame: synthetic data
        """
        if (
            force_refresh
            or self._synthetic is None
            or (rows_number is None and self._synthetic_rows_number is not None)
            or (
                rows_number is not None
                and self._synthetic_rows_number is not None
                and rows_number > self._synthetic_rows_number
            )
        ):
            # we need to fetch more rows
            self._synthetic_rows_number = rows_number
            resp = requests.get(
                f"{self.client.base_url}/synthetic_data/{self.id}",
                cookies=self.client.cookies,
                verify=self.client.verify,
                stream=True,
                params={"rows_number": self._synthetic_rows_number}
                if self._synthetic_rows_number is not None
                else {},
            )
            if resp.status_code > 200:
                raise Exception(
                    f"Error while retrieving synthetic data. "
                    f"Gateway answer was: \n{resp}"
                )
            # Unfortunately does not work with resp.raw
            self._synthetic = pd.read_parquet(io.BytesIO(resp.content))
        return self._synthetic.iloc[:rows_number]

    def _plot_marginal_feature(self, marginal_feature, width=1.5, heigth=1.5):
        if "statistics" not in marginal_feature:
            return None

        # text-based representations
        # count for categories
        distrib = marginal_feature["statistics"].get("distribution")
        if distrib:
            html_response = ""
            distrib_s = sorted(distrib, key=lambda x: -x["probability"])
            if len(distrib_s) > 5:
                others_count = len(distrib_s) - 5
                others_sum = sum([x["probability"] for x in distrib_s[5:]])
                distrib_s = distrib_s[0:5]
                distrib_s.append(
                    {
                        "name": f"Other ({others_count})",
                        "probability": others_sum,
                        "class_other": "True",
                    }
                )
            for item in distrib_s:
                html_response += "<div><div class='category "
                if "class_other" in item:
                    html_response += "other"
                html_response += f"''>\
                    {item['name']}\
                  </div>\
                  <div class='number'> {round(100*item['probability'],2)}%\
                  </div>\
                 </div>"
            return html_response

        # Graph-based representation
        _ = plt.figure(figsize=(width, heigth))
        # cumulDistribution for real
        cumul = marginal_feature["statistics"].get("cumulativeDistribution")
        if cumul:
            try:
                plt.fill_between(
                    [vp["value"] for vp in cumul],
                    [vp["probability"] for vp in cumul],
                )
            except Exception:
                pass
        fi = io.BytesIO()
        plt.tight_layout()
        plt.savefig(fi, format="svg")
        plt.clf()
        svg_dta = fi.getvalue()  # this is svg data
        return svg_dta.decode()

    def to_html(self, display_type=False):
        """
        return a HTML representation of this dataset, to be displayed
        in a Notebook for example.
        We'd like to render something like: https://www.kaggle.com/fmejia21/demographics-of-academy-awards-oscars-winners
        """
        css = """<style>
        @import url('https://rsms.me/inter/inter.css');
        @supports (font-variation-settings: normal) {
            html {font-family: 'Inter var', sans-serif; }
            table {font-size: 12px; border-collapse: collapse;}
            td, th {
                border: 1px solid rgb(222, 223, 224);
                font-weight: 500;
                color: rgba(0,0,0,0.7);
                padding: 8px;
                vertical-align:top;
                }
            tr.desc>td>div {
                display: flex; width: 140px;
                flex-wrap: wrap;
                justify-content: space-between;
            }
            tr.desc>td {
                border-bottom-width: 4px;
                }
            div.category {
                width: 70px;
                padding: 4px;
                margin-bottom: 4px;
                color: black;
                }
            div.number {
                padding: 4px;
                margin-bottom: 4px;
                color: rgb(0, 138, 188);
                text-align: right;
            }
            td>div:hover {
                background-color: rgba(0,0,0,0.03);
              }
            tr.synthetic {
                font-family: 'Roboto Mono', Monaco, Consolas, monospace;
              }
            tr.synthetic>td {
                padding: 8px 4px;
                color: rgba(0, 0, 0, 0.7);
              }
            div.other {color: rgba(0, 0, 0, 0.4);!important}
         </style>"""

        table = "<table>\
                <thead><tr>\n"
        columns = self.type_metadata["features"]
        for c in columns:
            table += f"<th>{c['name']}</th>\n"

        table += """</thead></tr>
                <tbody>
                <tr class='desc'>"""

        columns = self.type_metadata["features"]
        for c in self.marginals["features"]:
            table += f"<td>{self._plot_marginal_feature(c)}</td>\n"
        table += "</tr><tr>"
        if display_type:
            for c in columns:
                table += f"<td>{c['type']}</td>\n"

        table += "</tr></tbody></table>"

        return f"<html>{css}<body>\n \
                   {table}\
                 </body></html>"

    def synthetic_to_html(self, rows_number=None, force_refresh=False):
        """
        Display synthetic data as html
        Args:
            rows_number (int): number of rows to display
            force_refresh (bool): if True, does not use cached synthetic data

        Returns:
            str: html representation of the synthetic data
        """
        synthetic: pd.DataFrame = self.synthetic(
            rows_number=rows_number, force_refresh=force_refresh
        )
        image_cols = [
            f["name"]
            for f in self.type_metadata["features"]
            if "image" in f["type"]
        ]

        def _image_formatter(im):
            return (
                f'<img src="data:image/png;base64,'
                f'{base64.b64encode(im).decode()}">'
            )

        return synthetic.to_html(
            formatters={c: _image_formatter for c in image_cols},
            escape=False,
        )

    def synthetic_as_tf_dataset(
        self, batch_size, rows_number=None, force_refresh=False
    ):
        """
        Returns synthetic data as a tensorflow.data.Dataset

        Args:
            batch_size (int): size of the batches in the dataset
            rows_number (int): number of rows in the dataset
            force_refresh (bool): if True, does not use cached synthetic data

        Returns:
            tensorflow.data.Dataset
        """
        # get the output types and shapes
        # TODO: get the types from the protobuf
        output_types = dict()
        output_shapes = dict()
        for c in self.synthetic().columns:
            val = self.synthetic()[c].iloc[0]
            if self.synthetic()[c].dtype == "O":
                # not a native pandas dtype, handle the encoded image case
                if isinstance(val, (bytes, np.bytes_)):
                    val = np.asarray(Image.open(io.BytesIO(val)))
                else:
                    raise NotImplementedError(f"Unknown dtype for column {c}")
            output_types[c] = tf.as_dtype(val.dtype)
            output_shapes[c] = val.shape

        def generator():
            for _, row in self.synthetic(
                rows_number=rows_number, force_refresh=force_refresh
            ).iterrows():
                sample = dict()
                for name, v in row.items():
                    if isinstance(v, (bytes, np.bytes_)):
                        v = np.asarray(Image.open(io.BytesIO(v)))
                    sample[name] = v
                yield sample

        return tf.data.Dataset.from_generator(
            generator, output_types=output_types, output_shapes=output_shapes
        ).batch(batch_size)


class Client:
    def _url_validator(self, url):
        """
        From https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not
        """
        regex = re.compile(
            r"^(?:http|ftp)s?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        return re.match(regex, url) is not None

    def __init__(
        self,
        url="http://0.0.0.0:5000",
        username=None,
        password=None,
        verify=True,
    ):
        # verify: if False, doesn't check SSL certificate if protocol is https
        # TODO : self.progress_bar = Progbar(100, stateful_metrics=None)

        if self._url_validator(url):
            self.base_url = url
        else:
            raise Exception("Bad url")
        self.verify = verify
        if not password:
            password = getpass.getpass(prompt="Password: ", stream=None)
        try:
            request = requests.post(
                f"{self.base_url}/login",
                json={"username": username, "password": password},
                headers={"Content-Type": "application/json"},
                verify=self.verify,
            )
            self.cookies = request.cookies
            request.raise_for_status()
        except Exception:
            raise Exception(
                "Error during login: incorrect username or password"
            )

    def available_datasets(self):
        request = requests.get(
            f"{self.base_url}/datasets",
            cookies=self.cookies,
            verify=self.verify,
        )
        return [ds["name"] for ds in request.json()]

    def fetch_dataset_by_id(self, id):
        """Fetch a dataset from the Sarus Gateway

        Args:
            id (int): id of the dataset to be fetched

        Returns:
            an instance of Dataset
        """
        try:
            request = requests.get(
                f"{self.base_url}/datasets/{id}",
                cookies=self.cookies,
                verify=self.verify,
            )
            dataset = Dataset.from_dict(request.json(), self)
            return dataset
        except Exception:
            raise Exception("Dataset not available")

    def fetch_dataset_by_name(self, name):
        """Fetch a dataset from the Sarus Gateway

        Args:
            name (string): name of the dataset to be fetched

        Returns:
            Dataset: an instance of Dataset
        """
        try:
            request = requests.get(
                f"{self.base_url}/datasets/name/{name}",
                cookies=self.cookies,
                verify=self.verify,
            )
            dataset = Dataset.from_dict(request.json(), self)
            return dataset
        except Exception:
            raise Exception("Dataset not available")

    def fit(
        self,
        transform_def,
        keras_model_def,
        x=None,
        target_epsilon=None,
        batch_size=64,
        non_DP_training=False,
        dp_l2_norm_clip=1,
        dp_noise_multiplier=1,
        dp_num_microbatches=None,  # default: batch size
        tf_seed=None,
        print_privacy_info=True,
        **kwargs,
    ):
        """
        Launches remotely the training of a model, passed in keras_model_def

        Args:
            transform_def (callable): transform function
            keras_model_def (callable): function returning the model to train
            x (Dataset): dataset used for training
            y (Dataset): (Optional) target dataset used for training
            target_epsilon (float): If set, we stop the training when this value
                is reached
            batch_size (int): batch size
            non_DP_training (bool): if True, we trigger an additional training
                without DP, to compare performances (the resulting model is NOT
                returned)
            dp_l2_norm_clip (float): max value used to clip the gradients during
                DP-SGD training
            dp_noise_multiplier (float): noise multiplier for DP-SGD
            dp_num_microbatches (int): Number of microbatches (by default, equal
                to batch_size, so we get microbatches of size 1)
            tf_seed (int): The tensorflow seed is set to this value before the
                model is trained.
            **kwargs: other kwargs to pass to tensorflow Model.fit() function

        Returns:
            int: Id of the task
        """
        # for retro-compatibility, if y is set, delete it
        if "y" in kwargs:
            del kwargs["y"]

        if (
            dp_num_microbatches is not None
            and batch_size % dp_num_microbatches != 0
        ):
            raise ValueError(
                f"batch_size should be a multiple of dp_num_microbatches, got {batch_size} and {dp_num_microbatches}"
            )
        from tensorflow.keras import Model

        # set the seed
        if tf_seed is not None:
            tf.random.set_seed(tf_seed)

        model: Model = keras_model_def()
        # learn input/output shapes by running predict on the first line of
        #  synthetic data (shapes required to use the SavedModel format)

        # TODO improve when single format is used
        if transform_def:
            model.predict(
                transform_def(
                    x.synthetic_as_tf_dataset(batch_size),
                    features=x.type_metadata["features"],
                )
            )
        else:
            model.predict(x.synthetic_as_tf_dataset(batch_size))

        saved_model = _save_model(model)

        start_eps = x.epsilon

        request = requests.post(
            f"{self.base_url}/fit",
            data=cloudpickle.dumps(
                (
                    transform_def,
                    saved_model,
                    x.id,
                    target_epsilon,
                    non_DP_training,
                    batch_size,
                    dp_l2_norm_clip,
                    dp_noise_multiplier,
                    dp_num_microbatches,
                    tf_seed,
                    kwargs,
                )
            ),
            headers={"Content-Type": "application/octet-stream"},
            cookies=self.cookies,
            verify=self.verify,
        )
        if request.status_code > 200:
            raise Exception(
                f"Error while training the model.\
                             Full Gateway answer was:{request}"
            )
        task_id = request.json()["task"]
        status = self.poll_training_status(task_id)
        error_message = status.get("error_message", None)
        if error_message is not None:
            raise RuntimeError(
                f"Training failed with the following error:\n"
                f"{textwrap.indent(error_message, '  |')}"
            )
        if print_privacy_info:
            print(
                f"Training finished successfuly.\n"
                f"Epsilon is now {x.epsilon:.03f}. It was {start_eps:.03f} "
                f"before training the model.\n"
                f"The privacy budget (max epsilon) for this dataset is "
                f"{x.max_epsilon:.03f}."
            )
        return task_id

    def training_status(self, id):
        """Fetch a dataset from the Sarus Gateway

        Args:
            id (int): id of the task to be queried. It was provided by the fit
            method

        Returns:
            a string with the status of a training tasks
        """

        request = requests.get(
            f"{self.base_url}/tasks/{id}",
            cookies=self.cookies,
            verify=self.verify,
        )
        return request.json()

    def poll_training_status(self, id, timeout=1000):
        """Poll & display the status of a training task

        Args:
            id (int): id of the task to be queried. It was provided by the fit
            method
            timeout (int): in seconds

        Returns:
            dict: The training status at the end of the task

        Raises:
            TimeoutError: if timeout is reached before the training finishes
        """

        offset = 0
        elapsed_time = 0.0
        while elapsed_time < timeout:
            elapsed_time += 0.5
            request = requests.get(
                f"{self.base_url}/tasks/{id}",
                params=dict(offset=offset),
                cookies=self.cookies,
                verify=self.verify,
            )
            response_dict = request.json()
            offset = response_dict.get("next_offset", 0)
            if "progress" in response_dict:
                progress = base64.b64decode(
                    response_dict["progress"].encode("ascii")
                ).decode("ascii")
                if progress:
                    sys.stdout.write(progress)
            else:
                # this is the end of the training
                sys.stdout.write("\n")
                return response_dict
            sys.stdout.flush()
            time.sleep(0.5)
        raise TimeoutError(
            "Timeout reached while waiting for the model training to finish."
        )

    def fetch_model(self, id):
        """Fetch a trained model from the Sarus Gateway

        Args:
            id (int): id of the task to be queried. It was provided by the fit
            method

        Returns:
            a Keras model
        """

        response = requests.get(
            f"{self.base_url}/models/{id}",
            cookies=self.cookies,
            verify=self.verify,
        )
        # apparently we need to save to a temp file
        # https://github.com/keras-team/keras/issues/9343
        with tempfile.TemporaryDirectory() as _dir:
            f = tarfile.open(fileobj=io.BytesIO(response.content), mode="r:gz")
            f.extractall(_dir)

            return tf.keras.models.load_model(_dir)


def _save_model(model):
    with tempfile.TemporaryDirectory() as _dir:
        model.save(_dir)
        with tempfile.TemporaryDirectory() as _second_dir:
            path = os.path.join(_second_dir, "tmpzip")
            with tarfile.open(path, mode="w:gz") as archive:
                archive.add(_dir, recursive=True, arcname="")
            with open(path, "rb") as f:
                ret = f.read()
                return ret

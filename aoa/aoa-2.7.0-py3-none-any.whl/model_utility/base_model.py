from aoa.model_utility.model_utility import ModelUtility
import logging
import json
import os
from jinja2 import Template


class BaseModel(object):

    def __init__(self, model_utility: ModelUtility):
        self.model_utility = model_utility

    @staticmethod
    def get_model_id(model_path, rtn_val=False):
        catalog = {}
        index = 0
        model_ids = "Use one of the following models\n"

        for model in os.listdir(model_path):
            if os.path.exists(model_path + model + "/model.json"):
                with open(model_path + model + "/model.json", 'r') as f:
                    model_definition = json.load(f)
                    catalog[index] = model_definition
                    index += 1

        for key in catalog:
            model_ids += "{1}: {0}\n".format(catalog[key]["id"], catalog[key]["name"])

        if rtn_val:
            return catalog

        raise ValueError(model_ids)

    def __template_sql_script(self, filename, jinja_ctx):
        with open(filename) as f:
            template = Template(f.read())

        return template.render(jinja_ctx)

    def __execute_sql_script(self, conn, filename, jinja_ctx):
        script = self.__template_sql_script(filename, jinja_ctx)

        stms = script.split(';')

        for stm in stms:
            stm = stm.strip()
            if stm:
                logging.info("Executing statement: {}".format(stm))

                try:
                    conn.execute(stm)
                except Exception as e:
                    if stm.startswith("DROP"):
                        logging.warning("Ignoring DROP statement exception")
                    else:
                        raise e

    def __configure_pyspark(self, model_definition, model_artefacts_path, model_dir):
        import findspark
        import os
        from zipfile import ZipFile
        from os.path import basename, relpath
        import tempfile

        # zip up model files for py-files
        base_zip_path = model_dir + "/model_modules"
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as model_modules_fp:
            with ZipFile(model_modules_fp, 'w') as zip:
                for folder_name, _, filenames in os.walk(base_zip_path):
                    for filename in filenames:
                        full_file_path = os.path.join(folder_name, filename)
                        zip_path = relpath(full_file_path, base_zip_path)
                        zip.write(full_file_path, zip_path)

        # read the spark submit resources for the model
        if "resources" not in model_definition or "training" not in model_definition["resources"]:
            raise Exception("pyspark models require a resources->training section in model.json")

        resources = model_definition["resources"]["training"]
        aoa_spark_conf = os.environ.get("AOA_SPARK_CONF", "--conf spark.aoa.modelPath={}".format(model_artefacts_path))

        os.environ["PYSPARK_SUBMIT_ARGS"] = "--master {} {} --py-files {} {} pyspark-shell".format(
            resources["master"], resources["args"], model_modules_fp.name, aoa_spark_conf)

        # SPARK_HOME should be set
        spark_home = findspark.find()
        findspark.init(spark_home)

        self.logger.info("Using SPARK_HOME: {}".format(spark_home))
        self.logger.info("Using PYSPARK_SUBMIT_ARGS: {}".format(os.environ["PYSPARK_SUBMIT_ARGS"]))
        self.logger.info("Using AOA_SPARK_CONF: {}".format(os.environ.get("AOA_SPARK_CONF", "")))

    def __get_engine(self, model_definition):
        if "automation" in model_definition \
                and "trainingEngine" in model_definition["automation"]:
            return model_definition["automation"]["trainingEngine"]

        return model_definition["language"]

    def __run_r_model(self, model_id, base_path, data_conf, mode):
        import tempfile
        import subprocess

        with tempfile.NamedTemporaryFile(delete=False) as fp:
            fp.write(json.dumps(data_conf).encode())

        cmd = self.model_utility.dir_path + "/run_model.R {} {} {} {}".format(model_id, mode, fp.name, base_path)
        subprocess.check_call(cmd, shell=True)

def getConfig(ini_file_location=None):
    import os

    try:
        import configparser
    except ImportError:
        import ConfigParser as configparser

    config_file_path = ""
    config_file_exists = False
    config_return = {
            "bucket": "",
            "access_key": "",
            "api_base": "https://api.init.st"
        }

    if (ini_file_location != None):
        if (os.path.exists(ini_file_location)):
            config_file_path = ini_file_location
            config_file_exists = True
        else:
            raise Exception("ini file path specified, but doesn't exist or is not accessable")
    else:
        home = os.path.expanduser("~")
        config_file_home_path = os.path.abspath("{home}/isreader.ini".format(home=home))
        config_file_local_path = os.path.abspath("{current}/isreader.ini".format(current=os.getcwd()))

        config_file_exists = False
        config_file_path = config_file_home_path
        if (os.path.exists(config_file_home_path)):
            config_file_path = config_file_home_path
            config_file_exists = True
        elif (os.path.exists(config_file_local_path)):
            config_file_path = config_file_local_path
            config_file_exists = True

    if (config_file_exists):
        config = configparser.ConfigParser()
        config.read(config_file_path)
        if (config.has_section("isreader.client_config")):
            if (config.has_option("isreader.client_config", "access_key")):
                config_return["access_key"] = config.get("isreader.client_config", "access_key")
            if (config.has_option("isreader.client_config", "bucket_key")):
                config_return["bucket_key"] = config.get("isreader.client_config", "bucket_key")
        if (config.has_section("isreader.api_config")):
            if (config.has_option("isreader.api_config", "api_base")):
                config_return["api_base"] = config.get("isreader.api_config", "api_base")
                if (not config_return["api_base"].startswith("https://") and not config_return["api_base"].startswith("http://")):
                    raise Exception("api_base must start with valid http:// or https://")

    return config_return
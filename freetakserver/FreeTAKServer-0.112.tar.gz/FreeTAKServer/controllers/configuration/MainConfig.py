class MainConfig:
    """
    this is the main configuration file and is the only one which
    should need to be changed
    """
    # this is the port to which clients will connect
    CoTServiceIP = int(8087)

    # this needs to be changed for private data packages to work
    DataPackageServiceDefaultIP = str("0.0.0.0")

    # whether or not to save CoT's to the DB
    SaveCoTToDB = bool(False)

    # this should be set before startup
    DBFilePath = str('FTSDataBase.db')

    # the version information of the server (recommended to leave as default)
    version = 'FreeTAKServer-1.1RC6'
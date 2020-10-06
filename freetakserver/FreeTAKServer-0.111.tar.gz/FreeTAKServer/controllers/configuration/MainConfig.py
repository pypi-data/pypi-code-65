class MainConfig:
    """
    this is the main configuration file and is the only one which
    should need to be changed
    """
    CoTServiceIP = int(15777)

    DataPackageServiceDefaultIP = str("192.168.2.75")

    SaveCoTToDB = bool(False)

    #DBFilePath = str(r'/home/ghost/FTSTesting/FreeTAKServer/controllers/testing.db')
    DBFilePath = str(r'C:\Users\natha\PycharmProjects\InDev\FreeTAKServer\controllers\testing.db')

    version = 'FreeTAKServer-1.1RC6'
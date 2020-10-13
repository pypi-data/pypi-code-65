#! /usr/bin/python3

from ioa import *


def main():
    thisDevice = Device()
    thisDevice.addResource(Resource(Resource.type.ACTOR))

    print(thisDevice)
    pass


if __name__ == "__main__":
    main()

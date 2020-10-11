import os
"""
webp_cli_wrapper

This file provides wrapper functions to use libwebp in a comfortable way.
You need to have libwebp installed
Alpine: apk add libwebp-tools
Debian/Ubuntu: apt install webp
"""


def convert_to_webp(source, output, quality: int = 80, method: int = 4, lossless: bool = False,
                    multithreading: bool = True):
    """

    Args:
        source: Input file path e.g "some.jpg"
        output: Output file path e.g "some.webp"
        quality: Quality of the compression defaults to 80. If lossless is true smaller quality will be faster but the
            file is larger a higher quality will take longer but the file is smaller.
        method: Compression method 0-6 Defaults to 4
        lossless: Default False set only to true if the file is a PNG
        multithreading: Use multithreading if available defaults to true
    """
    command = f"cwebp -q {quality} -m {method} "

    if lossless:
        command += "-lossless "
    if multithreading:
        command += "-mt "

    command += f"{source} -o {output}"

    stream = os.popen(command)
    print(stream.read())


def convert_from_wepb(source: str, output: str, multithreading: bool = True):
    """

    Args:
        source: Input file path e.g "some.webp"
        output: Output file path e.g "some.png"
        multithreading: Use multithreading if available defaults to true

    """
    command = "dwebp "
    if multithreading:
        command += "-mt "
    command += f"-o {output} {source}"

    stream = os.popen(command)
    print(stream.read())


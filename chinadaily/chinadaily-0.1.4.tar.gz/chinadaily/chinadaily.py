"""Main module."""
import os
import shutil
import tempfile
from datetime import datetime

import requests
from PyPDF2 import PdfFileReader, PdfFileWriter


def merge(files, filename):
    """ Merge PDF's

    """
    output = PdfFileWriter()

    for f in files:
        input = PdfFileReader(open(f, "rb"), strict=False)

        # 获得源PDF文件中页面总数
        pageCount = input.getNumPages()

        # 分别将page添加到输出output中
        for iPage in range(pageCount):
            output.addPage(input.getPage(iPage))

    stream = open(filename, "wb")
    output.write(stream)
    stream.close()


def download(date):
    """

    """
    fmt_path = '%Y-%m/%d'
    file_path = datetime.strftime(date, fmt_path)
    fmt_name = '%Y%m%d'
    file_prefix = datetime.strftime(date, fmt_name)

    base = "http://paper.people.com.cn/rmrb/images"
    print("downloading with requests")

    # create a temp dir to download segment files
    temp_dir = tempfile.mkdtemp()
    files = []
    for i in range(1, 31):
        filename = f"rmrb{file_prefix}{i:02d}.pdf"
        url = f"{base}/{file_path}/{i:02d}/{filename}"

        r = requests.get(url)
        if r.ok:
            print(url)
            output = os.path.join(temp_dir, filename)
            files.append(output)
            with open(output, "wb") as f:
                f.write(r.content)
        else:
            print('download complete!!')
            break

    outfile = f"rmrb{file_prefix}.pdf"
    merge(files, outfile)

    # remove tmp dir
    shutil.rmtree(temp_dir)

    return outfile

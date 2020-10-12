from ipykernel.kernelbase import Kernel
import dolphindb as ddb
import json
import numpy as np
import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt 
from io import BytesIO
from flask import Flask
import urllib, base64
import binascii
import mplfinance as mpf

class DolphinDBKernel(Kernel):
    implementation = 'DolphinDB'
    implementation_version = '1.0'
    language = 'python'
    language_version = '1.0'
    language_info = {
        'name': 'python',
        'mimetype': 'text/plain',
        'file_extension': '.py',
    }
    banner = "DolphinDB Kernel"
    s = ddb.session()
    f = open("./dolphindb/creds.py", "r")
    strCreds = f.read()
    strCreds = strCreds.replace("\'", "\"")
    creds = json.loads(strCreds)

    # connect to DolphinDB server
    def connect(self, server, port, username, password):
        self.s.connect(server, port, username, password)

    # return a base64-encoded PNG from a matplotlib figure
    def _to_png(self, plt):
        imgdata = BytesIO()
        plt.savefig(imgdata, format='png')
        imgdata.seek(0)
        png = urllib.parse.quote(base64.b64encode(imgdata.getvalue()))
        return png

    # do_execute takes code as input and sends response to the client
    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        if code.startswith('connect-to-ddb-pre') or code.startswith('connect-to-ddb-new'):
            code_list = code.split()
            server = code_list[1]
            port = int(code_list[2])
            username = code_list[3]
            password = code_list[4]
            self.connect(server, port, username, password)
            if code.startswith('connect-to-ddb-new'):
                bytes_password = password.encode()
                hex_bytes_password = binascii.b2a_hex(bytes_password)
                encrypted_password = hex_bytes_password.decode()
                new_cred = {
                    'server': server,
                    'port': port,
                    'user': username,
                    'password': encrypted_password
                }                
                self.creds.append(new_cred)
                new_creds = self.creds
                s = json.dumps(new_creds)
                f = open("./dolphindb/creds.py", "w")
                f.write(s)

        elif code.startswith('retrieve-credentials'):
            for cred in self.creds:
                encrypted_password = cred['password']
                hex_bytes_password = encrypted_password.encode()
                decrypted_password = binascii.a2b_hex(hex_bytes_password).decode()
                cred['password'] = decrypted_password
            content = json.dumps(self.creds)
            stream_content = {'name': 'stdout', 'text': content}
            self.send_response(self.iopub_socket, 'stream', stream_content)

        elif code.startswith('delete-cred-at'):
            code_list = code.split()
            idx = (int)(code_list[1])
            self.creds.pop(idx)
            new_creds = self.creds
            s = json.dumps(new_creds)
            f = open("./dolphindb/creds.py", "w")
            f.write(s)

        else:
            res = self.s.run(code)
            resType = type(res)

            if resType == dict and res.__contains__('chartType'):
                data = res['data']
                values_arr = data[0]
                labels = data[1]
                series_name = data[2]
                chartType = res['chartType']
                title = res['title'][0]
                cnt = len(values_arr[0])
                if chartType == 8:
                    if cnt == 4:
                        series_name = ['High', 'Low', 'Open', 'Close']
                    elif cnt == 5:
                        series_name = ['High', 'Low', 'Open', 'Close', 'Volume']

                # clear current plot first
                plt.clf()

                # 6: SCATTER
                if chartType == 6:
                    x = res['title'][1]
                    y = res['title'][2]
                    values = []
                    for num in data[0]:
                        values.append(num)
                    plt.scatter(values, data[1])
                    plt.xlabel(x, fontsize=14)
                    plt.xlabel(y, fontsize=14)
                    plt.title(title)
                    plt.legend()
                    png = self._to_png(plt)

                # 0～5 + KLINE: 8
                elif chartType in [0,1,2,3,4,5,8]:
                    series_dict = {}
                    for idx  in range(len(values_arr[0])):
                        curr_val = []
                        for curr_arr in values_arr:
                            curr_val.append(curr_arr[idx])
                        series_dict[series_name[idx]] = curr_val
                    # 8
                    if chartType == 8:
                        ts_index = pd.DatetimeIndex(labels)
                        df = pd.DataFrame(series_dict, index=ts_index)
                        mc = mpf.make_marketcolors(
                                                up='tab:green',down='tab:red',
                                                edge='lime',
                                                wick={'up':'green','down':'red'},
                                                volume='tab:blue'
                                                )
                        s  = mpf.make_mpf_style(base_mpl_style="seaborn", marketcolors=mc, mavcolors=["yellow","orange","skyblue"])
                        buf = BytesIO()
                        if cnt == 4:
                            mpf.plot(df, type="candle", title=title, mav=(3,6,9), figratio=(12,6), style=s, savefig=buf)
                        elif cnt == 5:
                            mpf.plot(df, type="candle", title=title, mav=(3,6,9), figratio=(12,6), volume=True, style=s, savefig=buf)
                        buf.seek(0)
                        png = urllib.parse.quote(base64.b64encode(buf.getvalue()))
                    # 0 ~5
                    else:
                        df = pd.DataFrame(series_dict, index=labels)
                        # AREA
                        if chartType == 0:
                            df.plot(kind='area', stacked=False)
                        # BAR
                        elif chartType == 1:
                            df.plot(kind='bar', stacked=False)
                        # COLUMN
                        elif chartType == 2:
                            df.plot(kind='barh', stacked=False)
                        # HISTOGRAM
                        elif chartType == 3:
                            num_bins = res['binCount']
                            df.plot(kind='hist', stacked=False, bins=num_bins)
                            if res.__contains__('binStart') and res.__contains__('binEnd'):
                                start = res['binStart']
                                end = res['binEnd']
                                plt.xlim(xmin=start, xmax=end)
                        # LINE
                        elif chartType == 4:
                            df.plot(kind='line', stacked=False)
                        # PIE
                        elif chartType == 5:
                            df.plot(kind='pie', subplots=True, stacked=True)      
                        plt.title(title)
                        plt.legend()
                        png = self._to_png(plt)

                # content to display
                content = {
                    'source': 'kernel',
                    'data': {
                        'image/png': png
                    },
                    'metadata': {
                        'image/png': {
                            'width': 800,
                            'height': 600
                            }
                    }
                }

            elif resType == str or (res is None) or resType == bool or resType == int or resType == float or  resType == dict and not res.__contains__('chartType'):
                content = json.dumps(res)

            elif resType == np.ndarray:
                res_list = []
                for element in res:
                    res_list.append(element)
                content = tabulate(zip(res_list))

            elif resType == np.datetime64:
                content = json.dumps(res, indent=4, sort_keys=True, default=str) 

            elif resType == set:
                content = json.dumps(list(res))

            elif resType == pd.core.frame.DataFrame:
                df = pd.DataFrame(res)
                # row and col num
                row_num = df.shape[0]
                col_num = df.shape[1]
                # get header
                jsonString = df.to_json(orient='split')
                jsonObject = json.loads(jsonString)
                header = jsonObject["columns"]
                # first 5 rows and last 5 rows
                if row_num > 60:
                    head = df.head()
                    tail = df.tail()
                    df_range = pd.concat([head, tail])
                    content = tabulate(df_range, headers=header, tablefmt='simple')
                else:
                    content = tabulate(res, headers=header, tablefmt='simple')

            elif resType == list:
                content = tabulate(zip(res))

            if code != 'NULL' and content == 'null':
                content = ""

            if not silent:
                if(resType == dict and res.__contains__('chartType')):
                    self.send_response(self.iopub_socket, 'display_data', content)
                else:
                    stream_content = {'name': 'stdout', 'text': content}
                    self.send_response(self.iopub_socket, 'stream', stream_content)
            
        return {
            'status': 'ok',
            'execution_count': self.execution_count,
            'payload': [],
            'user_expressions': {},
            }


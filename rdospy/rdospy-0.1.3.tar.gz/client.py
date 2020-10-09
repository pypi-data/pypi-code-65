#!/usr/bin/env python3
# Authors : Julien DAVID & Ismail MOUMNI
import socket
import json

__RDOS_Host__ = '127.0.0.1'
__RDOS_Port__ = '9393'
# List to save REQUEST Parameters send FROM SERVER for query Match
__RDOS_Req__ = {"parameters": "request"}
__RDOS_Gen__ = {}


class RdosClient():

    # Function client_init connects to server and sends JSON Parameters needed
    # Function input Host : Server IP - Port : Server Port
    # Function output returns JSON from server side contaning parameters
    def __init__(self, port):
        data = {"parameters": "request"}
        socket = self.server_conn(__RDOS_Host__, port)
        print("Connexion to socket : ")
        print("Data :", (data))
        dat = json.dumps((data))
        socket.send(bytes(json.dumps(dat), "utf-8"))
        recv = socket.recv(4096)
        query = (json.loads(recv.decode('utf-8')))
        print("Generators list from Database : ", query)
        __RDOS_Gen__ = query
        print(__RDOS_Gen__)

    # Function insert_query takes a query and send it to server for inserting a new job
    # Function insert_query parameters : Dictionary
    def insert_query(self, data: dict):
        if (data is not None):
            socket = self.server_conn('127.0.0.1', 9393)
            req = json.dumps((data))
            print("data send to server :", req)
            socket.send(bytes((req), "utf-8"))
            recv = socket.recv(4096)
            query = ((recv.decode('utf-8')))
            print("data received:", query)
        else:
            raise Exception("Dictionnaire Vide !!")

    # Function get_objects connects client to server by socket
    # Function get_objects takes 2 parameters
    # Function get_objects returns the state of the server
    def get_objects(self):
        try:
            s = self.server_conn(__RDOS_Host__, __RDOS_Port__)
            message = json.dump((__RDOS_Req__))
            recv = self.send_st(s, message)
            print("Message ENVOYE : ", recv)
            return recv
        except socket.error as msg:
            print("Erreur de Connexion vers le client:" % msg)

    # Function missing_keys returns non existing fields in a dict
    # Function input biblio and dict
    # Function returns a list containing missing values else raises an Exception
    def missing_keys(biblio: dict, gen: dict):
        missing = []
        if(biblio is not None and gen is not None):
            for key in biblio:
                if key not in gen:
                    missing.append(key)
            return missing
        else:
            raise Exception("Dictionnaire Vide!!")

    # Function match_generator_dict Matches Dictionnary with a dictionnary
    # Function input 2 dictionaries to match
    # Function output true if dictionaries match else returns list of missing keys
    def match_query_dict(self, biblio: dict, data: dict):
        if biblio is not None and data is not None:
            return biblio.keys() == data.keys()
        else:
            return(self.missing_keys(biblio, data))

    # Function send_st sends to socket data bytes
    # Function input socket and data
    def send_st(self, s: socket, data: str):
        s.send(bytes(data, "utf-8"))

    # Function send_json_server sends dictionnary contaning Data in JSON Format
    # Function takes a HOST Port TO connect with server and a Dictionnary
    # Function prints Data send
    def send_js_server(self, Host, Port, biblio: dict):
        if not biblio:
            print("Dictionnary is Empty ")
        else:
            data = self.dict_to_JSON(biblio)
            self.run_client(Host, Port, data)
            print("Data send to server :", data)

    # send_mess Function that returns a message from a server to a client
    # Function takes 2 parameters (Socket & Message )
    # Function Output message send from server
    def send_query(self, s: socket, message: dict):
        if (message is not None):
            try:
                if self.match_query_dict(message, __RDOS_Gen__):
                    try:
                        s.send(bytes(message, "utf-8"))
                        data = s.recv(1024)
                        return (data)
                    except Exception:
                        tool = data.keys().strip('[]')
                        match = self.missing_keys(message, __RDOS_Gen__[tool])
                        print("Missing parameters:" % match)
            except ValueError as msg:
                print("Erreur requete Vide " % msg)

    # Function server_conn creates a socket and connects it to server
    # Function server_conn take No arguments
    # Function returns a socket after making connexion
    def server_conn(host, port):
        serve_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            serve_sock.connect((host, port))
            return serve_sock
        except socket.error as exc:
            print("%s" % exc)

    # Function dict_to_JSON transforms DICTIONNARY TO Json String
    # Function input Dictionnary
    # Function OUTPUT Json string Format
    def dict_to_JSON(self, biblio: dict):
        if(biblio is not None):
            if (self.missing_keys(biblio, __RDOS_Gen__) == []):
                return json.dumps(biblio)
            else:
                for a in __RDOS_Gen__:
                    print("Parameter: {}, Value : {}".format(a, __RDOS_Gen__[a]))
        else:
            raise Exception("Dictionnaire Vide!!")

    # Function json_to_dict changes a json file into a Dict
    # Function takes a json dict as input and returns a dictionary
    def json_to_dict(js):
        if js is not None:
            data = json.loads(js)
            return data
        else:
            raise Exception("Dictionnaire Vide!!")

    # Function help prints the generators parameters
    # Function returns generator parameters
    def help():
        print('Generator parameters :')
        for a in __RDOS_Gen__:
            print("Parameter: {}, Default Value : {}".format(a, __RDOS_Gen__[a]))

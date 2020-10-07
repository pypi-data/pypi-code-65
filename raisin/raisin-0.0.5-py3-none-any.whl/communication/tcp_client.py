#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import socket
import select
import sys
import threading

import raisin


class ClientIpv4:
    """
    permet d'avoir un dialogue avec un serveur
    """
    def __init__(self, ipv4, port, parallelization_rate, signature):
        assert 0 <= parallelization_rate <= 2
        self.ipv4 = str(ipv4)
        self.port = port
        self.parallelization_rate = parallelization_rate
        self.signature = signature
        self.must_die = False

        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # creation d'un TCP/IP socket, SOCK_STREAM=>TCP
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # on tente de reutiliser le port si possible
        self.tcp_socket.connect((self.ipv4, self.port))                       # on etabli la connection

    def send(self, question):
        """
        envoi une question brute, non serialisee.
        ne retourne rien mais cette methode bloque tant que la question n'est pas partie
        """
        with raisin.Printer("Envoi de la question '%s'..." % question, signature=self.signature):
            raisin.communication.tcp_server.send(
                self.tcp_socket,
                raisin.serialize(
                    question,
                    parallelization_rate=self.parallelization_rate,
                    compresslevel=(-1 if self.parallelization_rate else 0),
                    signature=self.signature),
                signature=self.signature)

    def receive(self):
        """
        attend que le serveur reponde.
        retourne la reponsse deserialise du serveur
        """
        with raisin.Printer("Reception de la reponse...", signature=self.signature):
            data = raisin.communication.tcp_server.receive(self.tcp_socket, signature=self.signature)

        is_direct = data[0]
        if is_direct:
            return raisin.deserialize(data[1:], parallelization_rate=self.parallelization_rate, psw=None, signature=self.signature)
        else:
            with open(data[1:].decode("utf-8"), "rb") as f:
                reply = raisin.deserialize(f, parallelization_rate=self.parallelization_rate, psw=None, signature=self.signature)
            os.remove(data[1:].decode("utf-8"))
            return reply

    def close(self):
        self.must_die = True
        self.tcp_socket.close()

    def __del__(self):
        self.close()

class ClientIpv6:
    """
    permet d'avoir un dialogue avec un serveur
    """
    def __init__(self, ipv6, port, parallelization_rate, signature):
        assert 0 <= parallelization_rate <= 2
        self.ipv6 = str(ipv6)
        self.port = port
        self.parallelization_rate = parallelization_rate
        self.signature = signature
        self.must_die = False

        self.tcp_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, False)
        self.tcp_socket.connect((self.ipv6, self.port))

    def send(self, question):
        """
        envoi une question brute, non serialisee.
        ne retourne rien mais cette methode bloque tant que la question n'est pas partie
        """
        with raisin.Printer("Envoi de la question '%s'..." % question, signature=self.signature):
            raisin.communication.tcp_server.send(
                self.tcp_socket,
                raisin.serialize(
                    question,
                    parallelization_rate=self.parallelization_rate,
                    compresslevel=(-1 if self.parallelization_rate else 0),
                    signature=self.signature),
                signature=self.signature)

    def receive(self):
        """
        attend que le serveur reponde.
        retourne la reponsse deserialise du serveur
        """
        with raisin.Printer("Reception de la reponse...", signature=self.signature):
            data = raisin.communication.tcp_server.receive(self.tcp_socket, signature=self.signature)

        is_direct = data[0]
        if is_direct:
            return raisin.deserialize(data[1:], parallelization_rate=self.parallelization_rate, psw=None, signature=self.signature)
        else:
            with open(data[1:].decode("utf-8"), "rb") as f:
                reply = raisin.deserialize(f, parallelization_rate=self.parallelization_rate, psw=None, signature=self.signature)
            os.remove(data[1:].decode("utf-8"))
            return reply

    def close(self):
        self.must_die = True
        self.tcp_socket.close()

    def __del__(self):
        self.close()



"""
copier coller du site
"""

def example():
    # Choosing Nickname
    nickname = input("Choose your nickname: ")

    # Connecting To Server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 55555))

    # Listening to Server and Sending Nickname
    def receive():
        while True:
            try:
                # Receive Message From Server
                # If 'NICK' Send Nickname
                message = client.recv(1024).decode('ascii')
                if message == 'NICK':
                    client.send(nickname.encode('ascii'))
                else:
                    print(message)
            except:
                # Close Connection When Error
                print("An error occured!")
                client.close()
                break

    # Sending Messages To Server
    def write():
        while True:
            message = '{}: {}'.format(nickname, input(''))
            client.send(message.encode('ascii'))

    # Starting Threads For Listening And Writing
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    write_thread = threading.Thread(target=write)
    write_thread.start()





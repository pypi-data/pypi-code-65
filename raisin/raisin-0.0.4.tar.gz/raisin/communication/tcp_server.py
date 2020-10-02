#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import multiprocessing
import os
import socket
import threading
import uuid

import raisin


"""
un lien interressant:
https://www.neuralnine.com/tcp-chat-in-python/
"""


def send_data(s, generator, signature):
    """
    permet d'envoyer des donnees
    'generator' est la sortie d'une fonctions de serialisation
    """
    def standardize_generator_sizes(generator, buff_size):
        """
        'generator' est un generateur qui cede des paquets de taille tres variable
        les paquets doivent etre de type 'bytes'
        le but est ici, d'uniformiser la taille des packets afin de renvoyer des packets de 
        'buff_size' octets
        cede donc les paquets au fure et a meusure
        """
        pack = b""
        for data in generator:                                          # on va lentement vider le generateur
            pack += data                                                # pour stocker peu a peu les paquets dans cette variable
            while len(pack) >= buff_size:                               # si le packet est suffisement gros
                yield pack[:buff_size]                                  # on le retourne avec la taille reglementaire
                pack = pack[buff_size:]                                 # puis on le racourci et on recomence le test
        if pack:
            yield pack       
    
    def anticipator(generator):
        """
        cede les packets du generateur accompagne d'un boolean
        qui vaut True si l'element itere est le dernier
        et false sinon. Le generateur doit donc etre capable de ceder au moin un paquet
        """
        actuel = next(generator)
        for pack in generator:
            yield False, actuel
            actuel = pack
        yield True, actuel
    
    with raisin.Printer("Envoi des donnees...", signature=signature) as p:
        for is_end, data in anticipator(standardize_generator_sizes(generator, 1024*1024 -1)):
            p.show("Contenu: %s" % (bytes([is_end]) + data))
            s.send(bytes([is_end]) + data)

def send_object(s, obj, signature):
    """
    fonctionne comme send_data
    mais prend un objet en entree
    n'est efficace que pour les petits objets
    """
    with raisin.Printer("Envoi d'un objet...", signature=signature):
        return send_data(s,
                        raisin.serialize(
                            obj,
                            compresslevel=0,
                            parallelization_rate=0,
                            copy_file=False,
                            signature=self.signature),
                        signature=signature)

def receive_data(s, signature):
    """
    permet de receptionner les donnees,
    meme si elle sont nombreuses
    retourne soit directement les donnes soit le nom du fichier qui les contients
    ce qui permet de distinguer les 2, c'est le premier bit qui vaut 1 si les donnees sont directement recuperee
    ou 0 si ce qui suit est le nom de fichier
    """
    with raisin.Printer("Reception des donnees brutes...", signature=signature) as p:
        data = s.recv(1024*1024)
        is_end = data[0]
        if is_end:
            p.show("Contenu: %s" % (b"\x01" + data[1:]))
            return b"\x01" + data[1:]
        filename = os.path.join(str(raisin.temprep), str(uuid.uuid4()))
        with open(filename, "wb") as f:
            f.write(data[1:])
            while not is_end:
                data = s.recv(1024*1024)
                f.write(data[1:])
                is_end = data[0]
        p.show("Contenu: %s" % (b"\x00" + filename.encode("utf-8")))
        return b"\x00" + filename.encode("utf-8")

def receive_object(s, signature):
    """
    fonction comme receive_data mais retourne directement l'objet
    deserialise
    """
    with raisin.Printer("Reception et mise en forme des donnees...", signature=signature):
        data = receive_data(s, signature)
        if data[0] == 1: # dans le cas ou les donnees sont toute presentes
            return raisin.deserialize(data[1:], parallelization_rate=0, signature=signature)
        elif data[0] == 0: # si c'est ecrit dans un fichier
            with open(data[1:].decode("utf-8")) as f:
                obj = raisin.deserialize(f, parallelization_rate=0, signature=signature)
            os.remove(data[1:].decode("utf-8"))
            return obj

def _client(ip_client, port_client, client_socket, signature):
    """
    prend en charge un client
    """
    with raisin.Printer("Communication en cours...", signature=signature) as p:
        with raisin.Printer("Reception de la requette...", signature=signature):
            requette = receive(client_socket, signature=signature)
        with raisin.Printer("Traitement de la requette...", signature=signature):
            resultat = raisin.communication.answering.answering(
                requette,
                signature,
                )
        with raisin.Printer("Envoi de la reponse...", signature=signature):
            send(client_socket, resultat, signature=signature)
        client_socket.close()

class ServerIpv4(threading.Thread):
    """
    se met en ecoute sur une ipv4
    """
    def __init__(self, parallelization_rate, signature):
        threading.Thread.__init__(self)
        assert 0 <= parallelization_rate <= 2
        self.parallelization_rate = parallelization_rate
        self.signature = signature
        self.must_die = False

        self.port = raisin.worker.configuration.load_settings()["server"]["port"]
        self.listen = raisin.worker.configuration.load_settings()["server"]["listen"]
        self.ip = str(raisin.Id().ipv4_lan)

        self.tcp_socket = socket.socket(
            socket.AF_INET,         # socket internet plutot qu'un socket unix
            socket.SOCK_STREAM,     # creation d'un TCP/IP socket, SOCK_STREAM=>TCP
            )
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # on tente de reutiliser le port si possible
        self.tcp_socket.bind((self.ip, self.port))
    
    def run(self):        
        with raisin.Printer("Lancement du serveur ipv4...", signature=self.signature) as p:
            while not self.must_die:
                self.tcp_socket.listen(self.listen)
                p.show("En ecoute sur l'addresse %s port %d." % (self.ip, self.port))
                client_socket, (ip_client, port_client) = self.tcp_socket.accept()
                
                if self.parallelization_rate == 0:   # si il n'y a qu'une parallelisation tres locale
                    _client(
                        ip_client,
                        port_client,
                        client_socket,
                        signature=self.signature,
                        )
                elif self.parallelization_rate == 1: # si il faut paralleliser avec threading
                    threading.Thread(
                        target=_client,
                        args=(ip_client, port_client, client_socket),
                        kwargs={
                            "signature": uuid.uuid4(),
                            },
                        ).start()
                elif self.parallelization_rate == 2: # si il faut paralleliser avec multiprocessing
                    multiprocessing.Process(
                        target=_client,
                        args=(
                            ip_client,
                            port_client,
                            client_socket,
                            ),
                         kwargs={
                            "signature": uuid.uuid4(),
                            },
                        ).start()
                else:
                    raise ValueError("'parallelization_rate' ne peut valoir que 0, 1 ou 2, pas %s." % self.parallelization_rate)

    def close(self):
        self.must_die = True
        self.tcp_socket.close()

    def __del__(self):
        self.close()

class ServerIpv6(threading.Thread):
    """
    se met en ecoute sur une ipv6
    """
    def __init__(self, parallelization_rate, signature):
        threading.Thread.__init__(self)
        assert 0 <= parallelization_rate <= 2
        self.parallelization_rate = parallelization_rate
        self.signature = signature
        self.must_die = False

        self.port = raisin.worker.configuration.load_settings()["server"]["port"]
        self.listen = raisin.worker.configuration.load_settings()["server"]["listen"]
        self.ip = str(raisin.Id().ipv6)

        self.tcp_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)   # creation d'un TCP/IP socket, SOCK_STREAM=>TCP
        self.tcp_socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
        self.tcp_socket.bind((self.ip, self.port))

    def run(self):
        with raisin.Printer("Lancement du serveur ipv6...", signature=self.signature) as p:
            while not self.must_die:
                self.tcp_socket.listen(self.listen)
                p.show("En ecoute sur l'addresse %s port %d." % (self.ip, self.port))
                client_socket, (ip_client, port_client, *_) = self.tcp_socket.accept()

                if self.parallelization_rate == 0: # si il n'y a qu'une parallelisation tres locale
                    _client(
                        ip_client,
                        port_client,
                        client_socket,
                        signature=self.signature,
                        )
                elif self.parallelization_rate == 1: # si il faut paralleliser avec threading
                    threading.Thread(
                        target=_client,
                        args=(ip_client, port_client, client_socket),
                        kwargs={
                            "signature": uuid.uuid4(),
                            },
                        ).start()
                elif self.parallelization_rate == 2: # si il faut paralleliser avec multiprocessing
                    multiprocessing.Process(
                        target=_client,
                        args=(
                            ip_client,
                            port_client,
                            client_socket,
                            ),
                         kwargs={
                            "signature": uuid.uuid4(),
                            },
                        ).start()
                else:
                    raise ValueError("'parallelization_rate' ne peut valoirt que 0, 1 ou 2, pas %s." % self.parallelization_rate)

    def close(self):
        self.must_die = True
        self.tcp_socket.close()

    def __del__(self):
        self.close()

class Server:
    """
    c'est un serveur ipv4 et ipv6
    qui permet de gerer plein de clients.
    Il comunique avec un orchestrateur pour gerer les differentes taches demandees par
    les clients
    """
    def __init__(self, signature=None):
        self.signature = signature
        with raisin.Printer("Initialisation of TCP servers...", signature=self.signature) as p:
            # partie serveur
            self.port = raisin.worker.configuration.load_settings()["server"]["port"]
            self.listen = raisin.worker.configuration.load_settings()["server"]["listen"]
            myid = raisin.Id()
            self.ipv4 = myid.ipv4_lan
            self.ipv6 = myid.ipv6
            if self.ipv4 == None and self.ipv6 == None:
                raise RuntimeError("Impossible de detecter l'ip, peut etre n'y a-t-il pas internet?")

            if self.ipv4:
                self.tcp_socket_ipv4 = socket.socket(
                    socket.AF_INET,         # socket internet plutot qu'un socket unix
                    socket.SOCK_STREAM)     # creation d'un TCP/IP socket, SOCK_STREAM=>TCP
                self.tcp_socket_ipv4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # on tente de reutiliser le port si possible
                self.tcp_socket_ipv4.bind((str(self.ipv4), self.port))
            else:
                self.tcp_socket_ipv4 = None
            if self.ipv6:
                self.tcp_socket_ipv6 = socket.socket(
                    socket.AF_INET6,        # socket internet en ipv6
                    socket.SOCK_STREAM)     # creation d'un TCP/IP socket, SOCK_STREAM=>TCP
                self.tcp_socket_ipv6.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
                self.tcp_socket_ipv6.bind((str(self.ipv6), self.port))
            else:
                self.tcp_socket_ipv6 = None

            # partie environement
            self.clients = {}               # c'est tous les clients connectes

    def close(self):
        """
        permet de fermer proprement les sockets
        """
        with raisin.Printer("Close connection...", signature=self.signature):
            if self.tcp_socket_ipv4:
                self.tcp_socket_ipv4.close()
            if self.tcp_socket_ipv6:
                self.tcp_socket_ipv6.close()

    def receive_ipv4(self):
        """
        gere l'entree des nouveau clients
        """
        while 1:
            with raisin.Printer("En attente de nouveau client...", signature=self.signature) as p:
                client_socket, (ip_client, port_client) = self.tcp_socket_ipv4.accept()   # Accept Connection
                p.show("Un client d'ip %s tente de se connecter via le port %d." % (ip_client, port_client))

                with raisin.Printer("Demande de plus amples informations...", signature=self.signature):
                    question1 = {"type":"question", "question":"How are you?"}
                    send_object(client_socket, question1, signature=self.signature)
                    identity = receive_object(clients, signature=self.signature)
                    with raisin.Printer("Verification de la reponse...", signature=self.signature):
                        if type(identity) is not dict:
                            p.show("Client expulse car il n'a pas repondu avec un dictionaire.")
                            answer = {"type":"error", "message":"Vous devez envoyer un dictionnaire, pas un %s." % type(identity)}
                            send_object(client_socket, answer, signature=self.signature)
                            continue
                        if "type" not in identity:
                            p.show("Client expulse car il n'y a pas de champ 'type' dans ca reponse.")
                            answer = {"type":"error", "message":"Il doit y avoir un champs 'type' dans votre reponse."}
                            send_object(client_socket, answer, signature=self.signature)
                            continue
                        if identity["type"] != "identity":
                            p.show("Client expulse car il ne veut pas donner son identite.")
                            answer = {"type":"error", "message":"Le type de reponse atendu est 'identity', pas %s." % str(identity["type"])}
                            send_object(client_socket, answer, signature=self.signature)
                            continue
                        if "public_key" not in identity:
                            p.show("Client expulse car il n'a pas donne ca clef publique")
                            answer = {"type":"error", "message":"Il doit y avoir un champs 'public_key' dans votre reponse."}
                            send_object(client_socket, answer, signature=self.signature)
                            continue
                        if type(identity["public_key"]) is not bytes:
                            p.show("Client expulse car ca clef publique n'est pas de type 'bytes'.")
                            answer = {"type":"error", "message":"La clef publique doit etre de type 'bytes', pas %s." % type(identity["public_key"])}
                            send_object(client_socket, answer, signature=self.signature)
                            continue
                        if not raisin.re.search(r"-----BEGIN PUBLIC KEY-----(.|\n)+-----END PUBLIC KEY-----", identity["public_key"].decode()):
                            p.show("Client expulse car la clef publique n'est pas au format 'PEM'.")
                            answer = {"type":"error", "message":"La clef publique n'est pas au format 'PEM'."}
                            send_object(client_socket, answer, signature=self.signature)
                            continue
                        p.show("Le client a livre son identite.")
                    if raisin.worker.configuration.load_settings()["server"]["force_authentication"]:
                        with raisin.Printer("Envoi d'un challenge pour confirmer l'identite...", signature=self.signature):
                            challenge = uuid.uuid4().bytes   # creation aleatoire d'une phrase 
                            question2 = {                    # on chiffre cette phrase avec la clef publique du client
                                "type":"challenge",
                                "challenge":raisin.worker.security.encrypt_rsa(
                                    challenge,
                                    identity["public_key"],
                                    parallelization_rate=0,
                                    signature=self.signature)}
                            answer_challenge = send_object(client_socket, question2, signature=self.signature) # on demande au client de la dechiffrer
                            if type(answer_challenge) is not dict:
                                p.show("Client expulse car il n'a pas repondu au challenge avec un dictionaire.")
                                answer = {"type":"error", "message":"Vous devez envoyer un dictionnaire, pas un %s." % type(answer_challenge)}
                                send_object(client_socket, answer, signature=self.signature)
                                continue
                            if "type" not in answer_challenge:
                                p.show("Client expulse car il n'y a pas de champ 'type' dans ca reponse.")
                                answer = {"type":"error", "message":"Il doit y avoir un champs 'type' dans votre reponse."}
                                send_object(client_socket, answer, signature=self.signature)
                                continue
                            if answer_challenge["type"] != "challenge_back":
                                p.show("Client expulse car ca reponse n'est pas un retour de challenge.")
                                answer = {"type":"error", "message":"Le type de reponse atendu est 'challenge_back', pas %s." % str(answer_challenge["type"])}
                                send_object(client_socket, answer, signature=self.signature)
                                continue
                            if "challenge" not in answer_challenge:
                                p.show("Client expulse car il n'a pas voulut repondre au challenge.")
                                answer = {"type":"error", "message":"Il doit y avoir un champs 'challenge' dans votre reponse."}
                                send_object(client_socket, answer, signature=self.signature)
                            if answer_challenge["challenge"] != challenge:
                                p.show("Client expulse car il n'a pas reussi le defit.")
                                answer = {"type":"error", "message":"Vous etes un escrot, vous n'avez pas reussi le defit!"}
                                send_object(client_socket, answer, signature=self.signature)
                                continue
                            p.show("Le client a reussi le defit.")




                # # Request And Store Nickname
                # client.send('NICK'.encode('ascii'))
                # nickname = client.recv(1024).decode('ascii')
                # nicknames.append(nickname)
                # clients.append(client)

                # # Print And Broadcast Nickname
                # print("Nickname is {}".format(nickname))
                # broadcast("{} joined!".format(nickname).encode('ascii'))
                # client.send('Connected to server!'.encode('ascii'))

                # # Start Handling Thread For Client
                # thread = threading.Thread(target=handle, args=(client,))
                # thread.start()

    def __del__(self):
        self.close()


"""
Ce qui suit, c'est un copier/coller du site
"""

def example():
    # Connection Data
    host = '127.0.0.1'
    port = 55555

    # Starting Server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()

    # Lists For Clients and Their Nicknames
    clients = []
    nicknames = []

    # Sending Messages To All Connected Clients
    def broadcast(message):
        for client in clients:
            client.send(message)

    # Handling Messages From Clients
    def handle(client):
        while True:
            try:
                # Broadcasting Messages
                message = client.recv(1024)
                broadcast(message)
            except:
                # Removing And Closing Clients
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast('{} left!'.format(nickname).encode('ascii'))
                nicknames.remove(nickname)
                break

    # Receiving / Listening Function
    def receive():
        while True:
            # Accept Connection
            client, address = server.accept()
            print("Connected with {}".format(str(address)))

            # Request And Store Nickname
            client.send('NICK'.encode('ascii'))
            nickname = client.recv(1024).decode('ascii')
            nicknames.append(nickname)
            clients.append(client)

            # Print And Broadcast Nickname
            print("Nickname is {}".format(nickname))
            broadcast("{} joined!".format(nickname).encode('ascii'))
            client.send('Connected to server!'.encode('ascii'))

            # Start Handling Thread For Client
            thread = threading.Thread(target=handle, args=(client,))
            thread.start()

    receive()



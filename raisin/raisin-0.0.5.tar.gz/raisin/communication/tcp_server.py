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

class _Receiver(threading.Thread):
    """
    Permet d'etre en ecoute sans bloquer le fil principal.
    Permet donc d'ecouter plusieurs ip a la fois
    """
    def __init__(self, tcp_socket):
        threading.Thread.__init__(self)
        self.tcp_socket = tcp_socket
        self.queue = [] # c'est la fifo des clients en attente
        self.must_die = False

    def run(self):
        """
        fonction appellee par self.start()
        c'est ici que l'on ajoute les nouveaux clients a la file
        """
        while not self.must_die:
            self.queue.append(self.tcp_socket.accept())

    def stop(self):
        """
        demande gentiment au server de s'arretter
        """
        self.must_die = True

    def kill(self):
        """
        arrete le serveur imediatement, meme si une opperation est en cours
        """
        if self.is_alive():
            self.join(timeout=0)

    def __iter__(self):
        """
        c'est ici que l'on vide la file
        """
        while self.queue:
            yield self.queue.pop(0)

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
                self.tcp_socket_ipv4.listen()
                self.receiver_ipv4 = _Receiver(self.tcp_socket_ipv4)
            else:
                self.tcp_socket_ipv4 = None
                self.receiver_ipv4 = None
            if self.ipv6:
                self.tcp_socket_ipv6 = socket.socket(
                    socket.AF_INET6,        # socket internet en ipv6
                    socket.SOCK_STREAM)     # creation d'un TCP/IP socket, SOCK_STREAM=>TCP
                self.tcp_socket_ipv6.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
                self.tcp_socket_ipv6.bind((str(self.ipv6), self.port))
                self.tcp_socket_ipv6.listen()
                self.receiver_ipv6 = _Receiver(self.tcp_socket_ipv6)
            else:
                self.tcp_socket_ipv6 = None
                self.rceiver_ipv6 = None
            
            # partie environement
            self.clients = {}               # c'est tous les clients connectes

    def is_accepted(self, public_key):
        """
        renvoi True si ce client a le droit de se connecter
        retourne False si il n'a pas le droit.
        retourne None si on doit demander l'avis de l'utilisateur 
        Ne pose aucune question a l'utilisateur, retourne sans attendre
        """
        with raisin.Printer("Testing if a pecific client is accepted...", signature=self.signature) as p:
            blacklisted = os.path.join(os.path.expanduser("~"), ".raisin/blacklisted.py")
            if os.path.exists(blacklisted):
                with open(blacklisted, "r", encoding="utf-8") as f:
                    if public_key.replace(b"\n", b"") in eval(f.read()):
                        p.show("It is accepted.")
                        return False
            whitelisted = os.path.join(os.path.expanduser("~"), ".raisin/whitelisted.py")
            if os.path.exists(whitelisted):
                with open(whitelisted, "r", encoding="utf-8") as f:
                    if public_key.replace(b"\n", b"") in eval(f.read()):
                        p.show("It is refoule.")
                        return True
            if raisin.worker.configuration.load_settings()["server"]["accept_new_client"]:
                p.show("It is accepted.")
                return True
            p.show("Maybe, we must ask the question.")
            return None

    def accept(self, identity):
        """
        ajoute le client passe en parametre dans la liste blanche
        ou a la liste noir si l'utilisateur le veut
        Si il faut attendre l'approbation de l'utilisateur,
        cette fonction est bloquante.
        retourne True si au final le client est accepte, et False sinon
        """
        with raisin.Printer("Ask to user for acept a new client...", signature=self.signature) as p:
            is_a = self.is_accepted(identity["public_key"])
            if is_a == True:
                p.show("The client is already accepted.")
                return True
            if is_a == False:
                p.show("This client is already baned.")
                return False
            question =  "'%s' client shouaite se connecter.\n" % identity["username"] \
                        + "Il travail sur l'os '%s' sur le PC %s.\n" % (identity["os_version"], identity["hostname"]) \
                        + "Il est localise en %s a %s.\n" % (identity["country"], identity["city"]) \
                        + "Il pretend avoir l'adresse mac %s.\n" % identity["mac"]
            rep = raisin.worker.configuration.question_binaire(question, default=None, existing_window=None)
            listed = "whielisted.py" if rep else "blacklisted"
            path = os.path.join(os.path.expanduser("~"), ".raisin", listed)
            data = set()
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = eval(f.read())
            data.add(identity["public_key"].replace(b"\n", b""))
            with open(path, "w", encoding="utf-8") as f:
                f.write(repr(data))
            if rep:
                p.show("The client is desormais accepted.")
            else:
                p.show("This client is desormaisbaned.")
            return rep

    def close(self):
        """
        permet de fermer proprement les sockets
        """
        with raisin.Printer("Close connection...", signature=self.signature):
            if self.tcp_socket_ipv4:
                self.receiver_ipv4.kill()
                self.tcp_socket_ipv4.close()
            if self.tcp_socket_ipv6:
                self.receiver_ipv4.kill()
                self.tcp_socket_ipv6.close()

    def receive(self):
        """
        generateur qui cede les variables:
        client_socket, (ip_client, port_client)
        des l'ors qu'un client tente de se connecter, que se soit en ipv4
        ou en ipv6
        """
        if self.ipv4 and self.ipv6:
            message = "aux adresses '%s' et '%s'" % (self.ipv4, self.ipv6)
        else:
            message = "a l'adresse '%s'" % (self.ipv4 if self.ipv4 else self.ipv6)
        with raisin.Printer("En ecoute sur le port %d %s..." % (self.port, message), signature=self.signature) as p:
            if self.receiver_ipv4:
                self.receiver_ipv4.start()
            if self.receiver_ipv6:
                self.receiver_ipv6.start()
            while 1:
                if self.receiver_ipv4:
                    yield from self.receiver_ipv4
                if self.receiver_ipv6:
                    yield from self.receiver_ipv6

    def select(self):
        """
        Gere l'acceptation des nouveau clients.
        Si le client est accepte, il est ajouter dans les clients connectes
        et un nouveau thread apparait rien que pour lui
        """
        for client_socket, (ip_client, port_client) in self.receive():
            p.show("Un client d'ip %s tente de se connecter via le port %d." % (ip_client, port_client))
            with raisin.Printer("Demande de plus amples informations...", signature=self.signature):
                question1 = {"type":"question", "question":"How are you?"}
                send_object(client_socket, question1, signature=self.signature)
                identity = receive_object(clients, signature=self.signature)
                with raisin.Printer("Verification de la reponse...", signature=self.signature):
                    champs = {
                        "type": str,
                        "public_key": bytes,
                        "username": str,
                        "os_version": str,
                        "hostname": str,
                        "country": str,
                        "city": str,
                        "mac": str,
                        }
                    for clef, genre in champs.items():
                        if clef not in identity:
                            p.show("Client expulse car il n'y a pas de champs '%s' dans sa reponse." % clef)
                            answer = {"type": "error", "message": "Il doit y avoir un champs '%s', ce n'est pas le cas." % clef}
                            send_object(client_socket, answer, signature=self.signature)
                            continue
                        if type(identity[clef]) is not genre:
                            p.show("Client expulse car la valeur associee au champs '%s' n'est pas de type '%s'." % (clef, genre))
                            answer = {"type": "error", "message": "N'essai meme pas de hacker le champs '%s'"}
                            send_object(client_socket, answer, signature=self.signature)
                            continue
                    if type(identity) is not dict:
                        p.show("Client expulse car il n'a pas repondu avec un dictionaire.")
                        answer = {"type": "error", "message": "Vous devez envoyer un dictionnaire, pas un %s." % type(identity)}
                        send_object(client_socket, answer, signature=self.signature)
                        continue
                    if identity["type"] != "identity":
                        p.show("Client expulse car il ne veut pas donner son identite.")
                        answer = {"type": "error", "message": "Le type de reponse atendu est 'identity', pas %s." % str(identity["type"])}
                        send_object(client_socket, answer, signature=self.signature)
                        continue
                    if not raisin.re.search(r"-----BEGIN PUBLIC KEY-----(.|\n)+-----END PUBLIC KEY-----", identity["public_key"].decode()):
                        p.show("Client expulse car la clef publique n'est pas au format 'PEM'.")
                        answer = {"type": "error", "message": "La clef publique n'est pas au format 'PEM'."}
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
                        if type(answer_challenge["challenge"]) is not bytes: # cela evite de pouvoir hacker la methode compare
                            p.show("Client expulse car il a tente de hacker la reponse du chalenge.")
                            answer = {"type":"error", "message":"Cherche pas a me hacker!"}
                            send_object(client_socket, answer, signature=self.signature)
                        if answer_challenge["challenge"] != challenge:
                            p.show("Client expulse car il n'a pas reussi le defit.")
                            answer = {"type":"error", "message":"Vous etes un escrot, vous n'avez pas reussi le defit!"}
                            send_object(client_socket, answer, signature=self.signature)
                            continue
                        p.show("Le client a reussi le defit.")
                if not raisin.worker.configuration.load_settings()["server"]["accept_new_client"]:
                    pass


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



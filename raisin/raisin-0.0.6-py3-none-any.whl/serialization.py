#!/usr/bin/env python3
#-*- coding: utf-8 -*-


import warnings
import gzip
import inspect
import io
import itertools
import json
import lzma
import os
try:
    import cloudpickle as pickle
except ImportError:
    warnings.warn("'cloudpickle' failed to import. Can generate serialisation alias, and not true copy.")
    import pickle
import random
import sys
import threading
import time
import uuid

import raisin


def compress(obj, compresslevel, psw, copy_file, parallelization_rate, signature):
    """
    serialise l'objet mais renvois une jolie chaine de caractere (STR) plutot qu'un iterable
    """
    def g(tree_bytes):
        """
        permet de convertir 3 octets en 4 caracteres
        """
        if tree_bytes in g_dico:
            return g_dico[tree_bytes]
        x, y, z = tuple((tree_bytes + b"00")[:3])
        s = 65536*x + 256*y + z
        d = f[s%64]
        s //= 64
        c = f[s%64]
        s //= 64
        b = f[s%64]
        a = f[s//64]
        g_dico[tree_bytes] = a+b+c+d
        return g_dico[tree_bytes]

    f = {**{i: str(i) for i in range(10)},
         **{i+10: chr(i+97) for i in range(26)},
         **{i+36: chr(i+65) for i in range(26)},
         **{62: "@", 63: "_"}}  # associ a chaque entiers, une jolie representation
    g_dico = {}
    data = b"".join(serialize(
        obj,
        buff=1024*1024,
        compresslevel=compresslevel,
        copy_file=copy_file,
        psw=psw,
        parallelization_rate=parallelization_rate,
        signature=signature))
    return "".join([g(data[i:i+3]) for i in range(0, len(data), 3)])+"."*((3 - (len(data) % 3)) % 3)

def decompress(chaine, psw, parallelization_rate, signature):
    """
    deserialize 'data' en STR
    retourne l'objet deserialize
    """
    def g(four_str):
        """
        converti 4 str en 3 bytes
        """
        if four_str in g_dico:
            return g_dico[four_str]
        a, b, c, d = four_str
        s = 262144*f[a] + 4096*f[b] + 64*f[c] + f[d]
        z = s % 256
        s //= 256
        y = s % 256
        x = s//256
        g_dico[four_str] = bytes([x, y, z])
        return g_dico[four_str]

    f = {**{str(i): i for i in range(10)},
         **{chr(i+97): i+10 for i in range(26)},
         **{chr(i+65): i+36 for i in range(26)},
         **{"@": 62, "_": 63}}
    g_dico = {}
    data = b''.join([g(chaine[i:i+4]) for i in range(0, 4*(len(chaine)//4), 4)])[:3*(len(chaine)//4)-(len(chaine) % 4)]
    return deserialize(data, psw=psw, parallelization_rate=parallelization_rate, signature=signature)

def size_to_tag(size):
    """
    'size' (int) >= 0
    retourne un bytes qui sert de fanion
    """
    assert type(size) is int, "'size' must be an integer. Not %s." % type(size)
    assert size >= 0, "'size', must be positive."
    # on va decouper ce nbr en base 2**7 pour garder un bit de libre par octet
    binaire_txt = bin(size)[2:]
    binaire_txt = "0"*(-len(binaire_txt) % 7) + binaire_txt # on bourre de 0 afin d'avoir un multiple de 7
    fanion_list = []    # contient les bytes correspondants
    for i in range(len(binaire_txt)//7): # pour chaque sous_packets
        fanion_list.append(sum((int(bit) << j for j, bit in enumerate(binaire_txt[7*i:7*i+7][::-1])))) # on ecrit le nombre en base 7
    fanion_list[-1] += 1 << 7 # on ajoute un drapeau pour dire qu'il n'y a plus rien apres
    return bytes(fanion_list) # on transforme ca en type bytes

def tag_to_size(pack, generator):
    """
    lit et interprete le fanion
    du debut.
    retourne le nombre cache dans le fanion, le nouveau pack
    depourvu du fanion, le generateur possiblement un peu plus itere
    renvoi une StopIteration exception si pack et le generateur sont vides.
    """
    size = 0        # initialisation
    while 1:        # tant que le fanion n'est pas termine
        if pack:
            octet = pack[0]
            pack = pack[1:]
        else:
            while not pack:
                try:
                    pack = next(generator)
                except (StopIteration, TypeError) as e:
                    if size:
                        raise ValueError("L'indicateur de longueur de packet n'est pas complet.")
                    raise StopIteration from e
            octet, pack = pack[0], pack[1:]
        if octet > 127: # si on arrive a la fin du fanion
            size = (size << 7) + (octet - 128)
            return size, pack, generator
        size = (size << 7) + octet

def generator_resizing(pack, generator):
    """
    si pack et generator contiennent des indications
    de longeures de paquets, les packets encapsules
    par ces fanions sont cedes
    """
    while 1:
        try:
            size, pack, generator = tag_to_size(pack, generator)
        except StopIteration:
            break
        else:
            while len(pack) < size:
                try:
                    pack += next(generator)
                except StopIteration as e:
                    raise ValueError("Un paquet doit faire %d octets, or il n'en fait que %d." % (size, len(pack))) from e
            yield pack[:size]
            pack = pack[size:]
    if pack:
        raise ValueError("Il reste des donnees inexploitee.")

def deserialize(data, psw, parallelization_rate, signature):
    """
    'data' peut etre:
        -un 'bytes' objet
        -un generateur de bytes sequences
        -un 'io.BufferedReader'
    'signature' permet d'afficher au bon endroit
    """
    def deserialize_filename(pack, generator):
        """
        si le fichier d'origine avait pour nom un chemin absolu,
        alors toute une arboresance va etre construite a partir du repertoir
        courant de facon a retourne exactement la meme chaine que celle definie par
        l'utilisateur qui a prealablement enregistre le fichier
        si le fichier d'origine avait pour nom un chemin relatif,
        alors, un nouveau fichier nome par ce meme nom est cree dans le repertoir courant
        ne prend aucune precaution, peu donc ecraser un fichier si un fichier de meme nom etait deja present
        dans le repertoir par defaut
        retourne le nom de ce fichier, relatif par rapport au repertoir courant
        """
        def split_directories(directories):
            """
            retourne une liste avec chaques dossier
            les un apres les autres
            """
            liste = []                                                  # initialisation de la liste vide
            directories = os.path.normpath(directories)
            while directories != "":                                    # tant que l'on a pas parcouru la totalite du chemin
                directories, e = os.path.split(directories)             # on extrait le dossier du bout
                if e == "":                                             # si jamais on frole la boucle infinie
                    break                                               # on ne s'y aventure pas plus que ca
                liste.insert(0, e)                                      # ajout de cet element dans la liste
            return liste

        # lecture entete
        taille_filename, pack, generator = tag_to_size(pack, generator) # annalyse de l'entete qui permet de recuperer la taille du nom de fichier
        while len(pack) < taille_filename:                              # on sait jamais, il se peut que le nom de fichier soit
            pack += next(generator)                                     # trop grand pour aparraitre en entier dans pack
        filename, pack = pack[:taille_filename].decode("utf-8"), pack[taille_filename:]# une fois qu'on est certain qu'il y soit, on le recupere
        
        # preparation du terrain (creation des repertoires si besoin)
        if os.path.isabs(filename):                                     # si il s'agit d'un chemin absolu vers un fichier
            filename = os.path.basename(filename)                       # alors on ne s'embete pas, on le transforme en chemin relatif
        directories, file = os.path.split(filename)                     # separation entre le nom du fichier et le chemin qui y mene
        if directories != "":
            chemin_complet = ""                                         # cela va etre le chemin complet qui mene au dossier
            for directory in split_directories(directories):            # pour chaque dossier a parcourir
                chemin_complet = os.path.join(chemin_complet, directory)# on l'ajoute a la pile
                if not os.path.exists(chemin_complet):                  # si ce chemin n'est pas deja sur le disque
                    os.mkdir(chemin_complet)                            # alors on l'ajoute
            filename = os.path.join(chemin_complet, file)               # quitte afaire quelque modification, on retourne un path valide

        # restitution du fichier
        with open(filename, "wb") as f:                                 # ouverture du fichier
            f.write(pack)                                               # puis on ecrit dedans son contenu
            for pack in generator:                                      # pour chaque packet restant
                f.write(pack)                                           # on y vide aussi le contenu du generateur
        return filename

    def deserialize_file_bytes(pack, generator, signature):
        """
        'pack' est un bout de bit
        'generator' cede la continuite de 'pack'
        """
        class BufferedReader(io.BufferedReader):
            def __init__(self, flux, *args, **kwargs):
                io.BufferedReader.__init__(self, flux.raw, *args, **kwargs)
                self.__flux = flux # permet de faire en sorte que le ramasse miette ne ferme pas le fichier

            def close(self):
                super().close()
                self.__del__()
                
            def __del__(self):
                try:
                    os.remove(self.name)
                except AttributeError:
                    pass

        # lecture entete
        size_closed, pack, generator = tag_to_size(pack, generator)
        while len(pack) < size_closed:
            pack += next(generator)
        closed, pack = bool(pack[0]), pack[1:]

        size_mode, pack, generator = tag_to_size(pack, generator)
        while len(pack) < size_mode:
            pack += next(generator)
        mode, pack = pack[:size_mode].decode("utf-8"), pack[size_mode:]

        size_type_, pack, generator = tag_to_size(pack, generator)
        while len(pack) < size_type_:
            pack += next(generator)
        type_, pack = pack[:size_type_], pack[size_type_:]

        size_stream_position, pack, generator = tag_to_size(pack, generator)
        while len(pack) < size_stream_position:
            pack += next(generator)
        stream_position, pack = int(pack[:size_stream_position].decode()), pack[size_stream_position:]

        # preparation du fichier
        filename = os.path.join(str(raisin.temprep), str(uuid.uuid4()))
        with open(filename, "wb") as f:
            f.write(pack)
            for pack in generator:
                f.write(pack)

        # creation de l'objet
        flux = open(filename, mode=mode) # on tente de reproduire fidellement l'etat du flux serialise
        if type_ == b"r":
            f = BufferedReader(flux)
        elif type_ == b"w":
            f = flux
        else:
            raise ValueError("Le 'type_' ne peut etre que b'r' ou b'w', pas %s" % type_)
        f.seek(stream_position, 0)   # on place le curseur la ou il etait
        if closed:
            f.close()
        return f

    def deserialize_file_text(pack, generator, signature):
        """
        'pack' est un bout de bit
        'generator' cede la continuite de 'pack'
        """
        class TextIOWrapper(io.TextIOWrapper):
            def __init__(self, flux, *args, **kwargs):
                io.TextIOWrapper.__init__(self, flux.buffer, *args, **kwargs)
                self.__flux = flux # permet de faire en sorte que le ramasse miette ne ferme pas le fichier

            def close(self):
                super().close()
                self.__del__()

            def __del__(self):
                try:
                    os.remove(self.name)
                except AttributeError:
                    pass

        # lecture entete
        size_closed, pack, generator = tag_to_size(pack, generator)
        while len(pack) < size_closed:
            pack += next(generator)
        closed, pack = bool(pack[0]), pack[1:]

        size_mode, pack, generator = tag_to_size(pack, generator)
        while len(pack) < size_mode:
            pack += next(generator)
        mode, pack = pack[:size_mode].decode("utf-8"), pack[size_mode:]
        
        size_encoding, pack, generator = tag_to_size(pack, generator)
        while len(pack) < size_encoding:
            pack += next(generator)
        encoding, pack = pack[:size_encoding].decode("utf-8"), pack[size_encoding:]

        size_errors, pack, generator = tag_to_size(pack, generator)
        while len(pack) < size_errors:
            pack += next(generator)
        errors, pack = pack[:size_errors].decode("utf-8"), pack[size_errors:]

        size_stream_position, pack, generator = tag_to_size(pack, generator)
        while len(pack) < size_stream_position:
            pack += next(generator)
        stream_position, pack = int(pack[:size_stream_position].decode()), pack[size_stream_position:]

        # preparation du fichier
        filename = os.path.join(str(raisin.temprep), str(uuid.uuid4()))
        with open(filename, "wb") as f:
            f.write(pack)
            for pack in generator:
                f.write(pack)

        # creation de l'objet
        flux = open(filename, mode=mode) # on tente de reproduire fidellement l'etat du flux serialise
        f = TextIOWrapper(flux, encoding=encoding, errors=errors)
        f.seek(stream_position, 0)                                      # on place le curseur la ou il etait
        if closed:
            f.close()
        return f

    def deserialize_iterable(pack, generator, signature):
        """
        deserialize la liste contenue dans le paquet 'pack'
        """
        new = b"n"                      # masque qui announce que il faut passer a l'element suivant de la liste
        end = b"e"                      # masque qui indique que c'est fini
        cont = b"c"                     # masque qui indique qu'on est encore en plein dans l'objet
        filename = os.path.join(str(raisin.temprep), uuid.uuid4().hex + ".rais") # fichier pour eventuellement stocker les elements trop gros
        while 1:                        # pour chaque element de l'iterable du depart
            is_open = False             # devient True si l'un des elements du generateur est trop gros pour etre deserialise en RAM
            while 1:                    # pour chaque sous packet de chaque element
                size, pack, generator = tag_to_size(pack, generator)
                data, indication, pack = pack[:size-1], pack[size-1:size], pack[size:]

                if indication == b"c":  # si on a pas fini de 'telecharger' l'element
                    with open(filename, "ab" if is_open else "wb") as f:
                        f.write(data)
                    is_open = True
                else:
                    if is_open:
                        with open(filename, "ab") as f:
                            f.write(data)
                        with open(filename, "rb") as f:
                            yield deserialize(
                                f,
                                psw=None,
                                parallelization_rate=0,
                                signature=signature)
                        os.remove(filename)
                    else:
                        yield deserialize(
                            data,
                            psw=None,
                            parallelization_rate=0,
                            signature=signature)
                    break

            if indication == end:
                break

    def file_to_json(filename):
        """
        'filename' est le chemin absolu d'un fichier ecrit en binaire
        ce fichier doit etre compatible avec le format json
        retourne l'objet deserialize et supprime le fichier une fois l'operation terminee
        """
        with open(filename, "r") as f:
            obj = json.load(f)
        os.remove(filename)
        return obj

    def file_to_pickle(filename):
        """
        'filename' est le chemin absolu d'un fichier ecrit en binaire
        ce fichier a ete cree par pickle
        retourne l'objet deserialize et supprime le fichier une fois l'operation terminee
        """
        with open(filename, "rb") as f:
            obj = pickle.load(f)
        os.remove(filename)
        return obj

    def generator_to_file(pack, gen, data):
        """
        cree un fichier en binaire qui contient les paquets de generator
        prend un racourci si 'data' est deja un pointeur vers un fichier en mode lecture
        retourne le chemin absolu de ce fichier
        """
        if type(data) is io.BufferedReader:                             # si le fichier est deja enregistre
            return os.path.abspath(data.name)                           # on va pas en faire un nouveau!
        filename = os.path.join(str(raisin.temprep), uuid.uuid4().hex + ".rais") # creation du fichier temporaire
        with open(filename, "wb") as f:                                 # que l'on rempli peu a peu
            f.write(pack)                                               # le generateur a deja subit une iteration
            for pack in gen:                                            # en vidant le generateur
                f.write(pack)                                           # dans le disque dur
        return filename                                                 # fermeture du fichier et on renvoi son nom

    def generator_to_generator(pack, generator, buff):
        """
        'generator' est un generateur qui cede des paquets de taille tres variable
        les paquet doivent etre de type 'bytes'
        le but est ici, d'uniformiser la taille des packet affin de renvoyer des pakets de 
        'buff' octet
        cede donc les paquets au fur a meusure apres avoir cede 'pack'
        """                                                             #initialisation du paquet
        for data in generator:                                          #on va lentement vider le generateur
            pack += data                                                #pour stocker peu a peu les paquets dans cette variable
            while len(pack) >= buff:                                    #si le packet est suffisement gros
                yield pack[:buff]                                       #on le retourne avec la taille reglementaire
                pack = pack[buff:]                                      #puis on le racourci et on recomence le test
        yield pack                                                      #enfin, on retourne le bout restant

    def generator_bytes(data):
        """
        prend les donnes sous sa forme primitive
        pour en faire un generateur de sequence de 'bytes'
        si 'data' est un fichier en lecture, la fermeture du fichier doit se faire ailleur
        car le fichier n'est pas ferme ici
        """
        buff = 1024*1024
        if type(data) == io.BufferedReader:                             # si il s'agit d'un pointeur vers un fichier
            first = True
            while 1:                                                    # on retourne tout petit a petit
                pack = data.read(buff)                                  # on lit la suite
                if pack == b"":                                         # si tout le fichier est lu
                    if first:
                        raise ValueError("The 'data' io.BufferedReader is empty.")
                    break                                               # on arrette la
                first = False
                yield pack                                              # sinon on retourne le petit bout de fichier que l'on vient de lire
        elif type(data) == bytes:                                       # si les donnees forment une chaine de d'octets
            yield data                                                  # si la donne d'entree et une chaine binaire, on ne la reitere pas, de toute facon elle est deja en ram!
        else:                                                           # si l'objet est deja un generateur
            try:
                iter(data)
            except TypeError as e:
                raise TypeError("'data' must be a 'bytes' object or a generator object or an 'io.BufferedReader'. Not %s." % type(data)) from e
            first = True
            for pack in data:
                first = False
                if type(pack) is bytes:
                    yield pack
                else:
                    raise TypeError("The 'data' generator muts yield 'bytes' type packs, not %s." % type(pack))
            if first:
                raise ValueError("'data' generator is an empty generator!")

    def uncipher_generator(pack, generator, parallelization_rate, psw, signature):
        """
        est un generateur qui cede les paquets
        dechiffres
        """
        decoupeur = generator_resizing(pack, generator)
        passphrase = raisin.deserialize(next(decoupeur), psw=psw, parallelization_rate=0, signature=signature)
        if parallelization_rate == 0:
            for pack in decoupeur:
                d = raisin.worker.security.decrypt_aes(pack, passphrase, parallelization_rate=0, signature=signature)
                yield d
        else:
            yield from raisin.map(
                lambda kwargs : raisin.worker.security.decrypt_rsa(**kwargs),
                ({
                    "data": pack,
                    "passphrase": passphrase,
                    "parallelization_rate": 0,
                    "signature": signature,
                    } for pack in decoupeur),
                parallelization_rate=parallelization_rate,
                signature=signature)

    # verifications
    if psw is not None:
        if type(psw) is bytes:
            try:
                if not raisin.re.search(r"-----BEGIN RSA PRIVATE KEY-----(.|\n)+-----END RSA PRIVATE KEY-----", psw.decode()):
                    raise ValueError("Une clef RSA privee au format PEM est attendue, ce n'est pas les cas.")
            except UnicodeDecodeError as e:
                raise ValueError("Si il est de type (bytes), le mot de passe doit etre une clef privee RSA au format PEM, ce n'est pas la cas.") from e
        else:
            assert type(psw) is str, "Le mot de passe doit etre soit None, soit un 'str' soit une clef rsa privee au format PEM (bytes). Pas un %s." % type(psw)
        assert psw, "'psw' ne peut pas etre une chaine vide. En l'absence de mot de passe, psw=None."
    assert type(parallelization_rate) is int, "'parallelization_rate' doit etre un entier. Pas un %s." % type(parallelization_rate)
    assert 0 <= parallelization_rate <= 4, "Le taux de paralelisation doit etre compris entre 0 et 4 inclus. Pas %d." % parallelization_rate
    generator = generator_bytes(data)                                   # homogeneisation des donnes entrantes

    text = {b"00":"data->small int",
            b"01":"data->pikle->large int",
            b"02":"data->json->small str",
            b"03":"data->json->medium str",
            b"04":"file->large str",
            b"06":"data->small bytes",
            b"07":"data->medium bytes",
            b"08":"file->large bytes",
            b"09":"data->io.TextIOWrapper",
            b"10":"data->io.BufferedReader",
            b"11":"data->list",
            b"12":"data->tuple data",
            b"13":"data->filename + file_content",
            b"17":"data->json->dict",
            b"18":"data->dict",
            b"19":"data->generator",
            b"90":"encrypted RSA data->data",
            b"96":"encrypted generator AES data->data",
            b"97":"encrypted AES data->data",
            b"99":"data->pickle->obj",
            }

    # lecture de l'entete
    pack = b""                                                          # on va lire le premier bout du generateur
    while len(pack) < 10:                                               # tant qu'on en a pas suffisement pour lire l'entete
        try:
            pack += next(generator)                                     # on itere sur le generateur
        except StopIteration:
            raise ValueError("L'entete n'est pas complette: il manque des donnes.")
    if (pack[:3] != b"</>") or (not pack[3:7].isdigit()) or (pack[7:10] != b"</>"): # si l'entete ne suit pas la norme
        raise ValueError("The header is all brocken!")                  # on envoi bouler
    
    # deserialisation
    with raisin.Printer("Deserialization...", signature=signature) as p: # pour le moment, l'entete est vide
        p.show(text[pack[3:5]])                                         # on affiche ce que l'on fait
        protocol, pack = pack[5:7],  pack[10:]                          # c'est le protocol pour la deserialisation, et la suppression de l'entete
        if protocol == b"99":                                           # si il s'agit d'une simple serialisation avec pickle
            return pickle.loads(pack + b"".join(generator))             # on les retourne telle qu'elle
        elif protocol == b"98":                                         # si c'est tout un fichier qui est pickelise
            return file_to_pickle(generator_to_file(pack, generator, data)) # on retourne l'objet deserialize
        elif protocol == b"97":                                         # si les donnees sont cryptees
            return deserialize(
                raisin.worker.security.decrypt_aes(
                    data=pack + b"".join(generator),
                    passphrase=(psw.encode("utf-8") + b"\x00"*32)[:32],
                    parallelization_rate=parallelization_rate,
                    signature=signature),
                psw=psw,
                parallelization_rate=parallelization_rate,
                signature=signature)                                    # dechiffrage puis deserialisation des donnees
        elif protocol == b"96":                                         # si les donnes sont cryptees mais a la volle par un generateur
            return deserialize(
                uncipher_generator(
                    pack,
                    generator,
                    parallelization_rate=parallelization_rate,
                    psw=psw,
                    signature=signature),
                psw=psw,
                parallelization_rate=parallelization_rate,
                signature=signature)                                    # decriptage puis deserialisation
        elif protocol == b"95":                                         # si les donnes sont compressees avec gzip
            return deserialize(
                gzip.decompress(pack + b"".join(generator)),
                psw=psw,
                parallelization_rate=parallelization_rate,
                signature=signature) # on le decompresse avec ce meme algo
        elif protocol == b"94":                                         # si les donnes sont compresses avec lzma
            return deserialize(
                lzma.decompress(pack + b"".join(generator)),
                psw=psw,
                parallelization_rate=parallelization_rate,
                signature=signature) # on les extrais aussi avec le bon algorithme
        elif protocol == b"93":                                         # si le fichier et un fichier compresse avec gzip
            return deserialize(
                decompress_gzip(pack, generator),
                psw=psw,
                parallelization_rate=parallelization_rate,
                signature=signature) # on le decompresse alors
        elif protocol == b"92":                                         # si le fichier est compresse avec lzma
            return deserialize(
                decompress_lzma(pack, generator),
                psw=psw,
                parallelization_rate=parallelization_rate,
                signature=signature) # on le decompresse alors
        elif protocol == b"91":                                         # si les donnees sont cryptees avec RSA
            return deserialize(
                raisin.worker.security.decrypt_rsa(
                    data=pack + b"".join(generator),
                    private_key_pem=psw,
                    parallelization_rate=parallelization_rate,
                    signature=signature),
                psw=psw,
                parallelization_rate=parallelization_rate,
                signature=signature) 
        elif protocol == b"00":                                         # dans le cas ou l'on doit faire un simple int
            return int(pack + b"".join(generator))                      # on vide le generateur et on retourne l'entier
        elif protocol == b"01":                                         # si le protocol est un simple json
            return json.loads((pack + b"".join(generator)).decode("utf-8")) # on le decode simplement
        elif protocol == b"02":                                         # pour dejsoniser les fichiers
            return file_to_json(
                        generator_to_file(
                            pack,
                            generator,
                            data))                                      # on ecrit d'abort dans un fichier avant d'apliquer l'algo json
        elif protocol == b"04":                                         # si il s'agit d'une simple sequence de bytes
            return pack + b"".join(generator)                           # on la retourne directement
        elif protocol == b"05":                                         # si il faut faire un pointeur de fichier text
            return deserialize_file_text(pack, generator, signature=signature) # on ecrit le fichier et on le retourne
        elif protocol == b"07":                                         # si il faut faire un pointeur vers un fichier binaire
            return deserialize_file_bytes(pack, generator, signature=signature) # on ecrit le fichier avant de le retourner
        elif protocol == b"08":                                         # si il s'agit d'une liste
            return list(deserialize_iterable(pack, generator, signature=signature)) # on la deserialize doucettement
        elif protocol == b"09":                                         # si on deserialize un tuple
            return tuple(deserialize_iterable(pack, generator, signature=signature))# on s'y prend comme pour les listes
        elif protocol == b"10":                                         # si il s'agit d'un fichier
            return deserialize_filename(pack, generator)                # on ecrit alors le fichier puis on retourne son nom tel qu'il etait a l'origine
        elif protocol == b"14":                                         # si l'objet est un dictionaire
            return {c: v for c, v in deserialize_iterable(pack, generator, signature=signature)} # on le deserialize via un iterable de couple clef / valeur
        elif protocol == b"15":                                         # si l'objet est un generateur
            return deserialize_iterable(pack, generator, signature=signature) # on cede directement un generateur
        elif protocol == b"16":                                         # si une chaine de caractere est cachee dans l'objet
            return pack.decode("utf-8") + b"".join(generator).decode("utf-8") # et bien on le decache
        else:                                                           # dans le cas ou ce n'est rien de tout ca
            raise Exception("The protocol %s is unknown." % (protocol,)) # on renvoi une erreur

def serialize(obj, buff, compresslevel, copy_file, psw, parallelization_rate, signature):
    """
    serialize l'objet 'obj' avec pickle sauf si l'objet est:
        -un entier (int)
        -un nom de fichier, relatif ou absolu, si 'copy_file' == True, copie aussi le fichier en arriere plan (str)
        -une chaine de caractere (str)
        -du binaire (bytes)
        -un pointeur de fichier texte (io.TextIOWrapper)
        -un pointeur vers un fichier binaire (io.BufferedReader ou io.BufferedWriter)
        -une liste (list)
        -un tuple (tuple)
        -un dictionaire (dict)
        -un generateur (<class 'generator'>)

        -une classe (class)
        -un module (module)

    'signature' est l'identifiant pour gerer l'affichage (STR)
    'buff' est environ la taille des paquets retournes en octets (100 Mo par defaut) (INT)
    'compresslevel' est le taux de compression a appliquer 0 pour sauter cette etape (INT)
    'copy_file' permet d'autoriser ou non la copie de fichier si l'objet est un str qui correspond a un chemin (BOOL)
    'psw' est un mot de passe pour crypter les donnees de facon symetriques (STR)
    'parallelization_rate' est un nombre qui determine le degres de paralellisation (INT):
        -0: pas de parallelization
        -1: legere parallelization avec des thread du module 'threading'
        -2: parallelization sur les differents coeurs de la machine en local (module 'multiprocessing')
        -3: parallelization avec les machines du reseau locale lan
        -4: parallelization avec le max de machines lan + wan
    est un generateur qui rcede des paquets de buff octets (BYTES)
    """
    def cipher_data(data, psw, parallelization_rate, signature):
        """
        'data' est de type bytes
        retourne la nouvelle sequence data mais cryptee (l'entete et retourne avec)
        """
        if psw is None:
            return data
        if type(psw) is bytes:                                          # si on ne possede que une clef rsa publique
            with raisin.Printer("Encryption sequences with the RSA algotithm..."):
                entete = b"</>9091</>"                                  # entete pour ce genre de donnees
                return entete + raisin.worker.security.encrypt_rsa(data, psw, parallelization_rate=parallelization_rate, signature=signature)
        else:
            with raisin.Printer("Encryption sequences with the AES algorithm...", signature=signature):
                entete = b"</>9797</>"                                  # entete pour le chiffrement basic
                passphrase = (psw.encode("utf-8") + b"\x00"*32)[:32]    # on transforme le mot de passe en une suite de 32 octets
                return entete + raisin.worker.security.encrypt_aes(data, passphrase, parallelization_rate=parallelization_rate, signature=signature)

    def cipher_generator(generator, psw, parallelization_rate, signature):
        """
        'generator' est un generateur de paquet de bytes
        cede ces memes paquets mais cryptes (l'entete est presente sur le premier packet)
        """
        def add_size(data):
            return size_to_tag(len(data)) + data

        if psw is None:
            yield from generator
        else:
            with raisin.Printer("Encryption generator...", signature=signature):
                assert 0 <= parallelization_rate <= 4, "Le taux de parallelisation doit etre compris entre 0 et 4 inclus. Pas %d." % parallelization_rate
                passphrase = bytes([random.randint(0, 255) for i in range(32)]) # c'est la clef aes qui va chiffrer tous le reste du message
                ciphered_passphrase = b"".join(raisin.serialize(
                    passphrase,
                    psw=psw,
                    parallelization_rate=0,
                    signature=signature))                               # mais bien sur, on ne la laisse pas en clair
                yield b"</>9696</>" + add_size(ciphered_passphrase)     # on comence par ceder l'entete qui va permetre de lire toute la suite

                if parallelization_rate == 0:                           # dans le cas ou il ne faut rien paralleliser
                    for pack in generator:                              # on fait les calculs a la suite les uns des autres
                        d = add_size(raisin.worker.security.encrypt_aes(
                            pack,
                            passphrase=passphrase,
                            parallelization_rate=0,
                            signature=signature))
                        yield d
                else:                                                   # si il faut paralleliser un peu plus
                    yield from raisin.map(
                        lambda kwargs : add_size(raisin.worker.security.encrypt_aes(**kwargs)),
                        ({
                            "data":pack,
                            "passphrase":passphrase,
                            "parallelization_rate":0,
                            "signature":signature}
                            for pack in generator),
                        parallelization_rate=parallelization_rate,
                        signature=signature)

    def compress_data(data, compresslevel, parallelization_rate, signature):
        """
        'data' est une sequence de bytes
        retourne la nouvelle sequence data mais compressee (l'entete est retourne avec)
        """
        return data
        # raise NotImplementedError()
        
        # if compresslevel == 0 or compresslevel == -1:
        #     return data
        # elif compresslevel == 1:
        #     with raisin.Printer("Compressing %d bytes with gzip 3..." % len(data), signature=signature) as p:
        #         data = b"</>9595</>" + gzip.compress(data, compresslevel=3)
        #         p.show("Compressed size: %d." % len(data))
        #         return data
        # elif compresslevel == 2:
        #     with raisin.Printer("Compressing %d bytes with gzip 9..." % len(data), signature=signature) as p:
        #         data = b"</>9495</>" + gzip.compress(data, compresslevel=9)
        #         p.show("Compressed size: %d." % len(data))
        #         return data
        # elif compresslevel == 3:
        #     with raisin.Printer("Compressing %d bytes with lzma 9..." % len(data), signature=signature) as p:
        #         data = b"</>9394</>" + lzma.compress(data, preset=9)
        #         p.show("Compressed size: %d." % len(data))
        #         return data
        # raise ValueError("The 'compresslevel' can only be 0, 1, 2, 3 or -1. Not %d." % compresslevel)

    def compress_generator(generator, buff, compresslevel, parallelization_rate, extension, signature):
        """
        'generator' est un generateur de paquet de bytes
        cede ces memes paquets mais encodees (l'entete est deja presente sur le premier paquet)
        """
        yield from generator
        # raise NotImplementedError()

    def file_to_generator(filename, buff, remove, entete):
        """
        'filename' est le chemin absolu vers un fichier binaire
        supprimme le fichier une fois qu'il est totalement restitue si remove == True
        cede peu a peu le fichier avec des packets de 'buff' octets
        """
        assert type(entete) is bytes, "L'entete doit etre de type bytes. Pas %s." % type(entete)
        with open(filename, "rb") as f:                                 # on ouvre le fichier en binaire
            i = 0                                                       # on met un detecteur de premiere boucle
            while 1:                                                    # tant que l'on a pas lu l'integralite du fichier
                pack = f.read(buff)                                     # on va lire le bout suivant
                if i == 0:                                              # si on en est a la premiere boucle
                    pack = entete + pack                                # on insere l'entete
                    i = 1                                               # on change la valeur du detecteur pour faire cela une fois seulement
                if pack == b"":                                         # si on est arrive au bout
                    break                                               # on s'arrete
                yield pack                                              # sinon on cede le bout qui vient d'etre lu
        if remove:
            os.remove(filename)                                         # suppression definitive du fichier desormais lu

    def generator_data(data, buff):
        """
        c'est tout simplement un generateur qui permet de ceder peu a peu des paquets de buff octets
        'data' doit imperativement etre une sequence de type bytes
        """
        for i in range(0, len(data), buff):
            yield data[i:i+buff]

    def generator_to_generator(pack, generator, buff):
        """
        'generator' est un generateur qui cede des paquets de taille tres variable
        les paquet doivent etre de type 'bytes'
        le but est ici, d'uniformiser la taille des packet affin de renvoyer des pakets de 
        'buff' octet
        cede donc les paquets au fur a meusure
        """
        for data in generator:                                          # on va lentement vider le generateur
            pack += data                                                # pour stocker peu a peu les paquets dans cette variable
            while len(pack) >= buff:                                    # si le packet est suffisement gros
                yield pack[:buff]                                       # on le retourne avec la taille reglementaire
                pack = pack[buff:]                                      # puis on le racourci et on recomence le test
        if pack:
            yield pack                                                  # enfin, on retourne le bout restant, si il reste quelque chose

    def serialize_class(obj, buff, signature):
        """
        'obj' est le pointeur vers la class a serialiser
        cede peu a peu la classe avec ses methodes, les packets cede sont de tailles tres variables
        mais n'exede pas beaucoup buff
        l'environement destine au bon fonctionement de la classe est cede aussi
        """
        raise NotImplementedError()

    def serialize_function(fonc, buff, signature):
        """
        'fonc' est le pointeur vers la fonction
        cede peu a peu des packets d'environ 'buff' octets
        """
        raise NotImplementedError()

    def serialize_iterable(iterable, buff, copy_file, entete, signature):
        """
        'iterable' est un presque iterable (LIST, TUPLE, GENERATOR)
        cede de packets de taille pas bien plus gros que buff
        """
        def anticipator(generator):
            """
            cede les packets du generateur accompagne d'un booleen
            qui vaut True si l'element itere est le dernier
            et false sinon. Le generateur doit donc etre capable de ceder au moin un paquet
            """
            precedent = next(generator)
            for pack in generator:
                yield False, precedent
                precedent = pack
            yield True, precedent

        new = b"n"                   # fanion qui announce que il faut passer a l'element suivant
        end = b"e"                   # fanion qui indique que c'est fini
        cont = b"c"                  # fanion qui indique qu'on est encore en plein dans l'objet

        yield entete
        for is_end_list, e in anticipator(iter(iterable)):        # pour chaque element de l'objet
            for is_end_element, pack in anticipator(
                    serialize(
                    e,
                    buff=buff,
                    compresslevel=0,
                    copy_file=copy_file,
                    psw=None,
                    parallelization_rate=0,
                    signature=signature)):
                indication = cont if not is_end_element else (end if is_end_list else new)
                yield size_to_tag(len(pack)+1) + pack + indication

    def is_file(obj, copy_file):
        """
        retourne True si l'objet est un chemin vers un fichier
        et qu'il faut copier les fichiers
        """
        if not copy_file:                                               # si l'utilisateur ne nous autorise pas d'interpreter l'objet comme un fichier
            return False                                                # alors on ne fait meme pas la suite du test
        if type(obj) == str:                                            # deja il faut que l'objet soit une chaine de caractere
            if len(obj) < 32767:                                        # et qu'il ne soit pas trop gros, sinon microchiotte windaube plante
                return os.path.isfile(obj)                              # alors on fait le test
        return False                                                    # si ces conditions ne sont pas verifies, alors ce n'est pas un chemin vers un fichier

    def is_jsonisable(obj, copy_file):
        """
        retourne True si l'objet peu etre serialise avec json
        retourne False le cas echeant
        """
        if type(obj) in (int, float, bool, type(None)):                 #si l'objet est vraiment basique
            return True                                                 #alors json sait le serialiser
        elif type(obj) == str:                                          #dans le cas ou c'est une chaine de caractere
            if not is_file(obj, copy_file):
                return True
        elif type(obj) == list:                                         #dans le cas ou l'objet est une liste
            for element in obj:                                         #on a pas d'autre choix que de parcourir la liste
                if not is_jsonisable(element, copy_file):               #si l'un des elements n'est pas compatible avec json
                    return False                                        #alors la liste n'est pas jsonisable
            return True                                                 #par contre, si tout est ok, allors on le jsonisifi
        elif type(obj) == dict:                                         #de meme, dans le cas ou l'objet est un dictionnaire
            for key, value in obj.items():                              #pour faire la verification, on s'y prend comme pour les listes
                if not is_jsonisable(value, copy_file):                 #si l'un des elements du dictionnaire fait tout capoter
                    return False                                        #on ne va pas plus loin
                elif not is_jsonisable(key, copy_file):                 #meme si c'est moin probable, mais si la clef n'est pas satisfesante
                    return False                                        #tant pis, ça fait tout arreter quand meme
            return True                                                 #si tout semble ok, et bien on dit qu'il est jsonalisable
        return False                                                    #dans tous les autres cas, json ne fait pas bien le boulot

    def encapsule_filename(filename, buff):
        entete = b"</>1310</>"
        filename_bytes = filename.encode("utf-8")
        yield entete + size_to_tag(len(filename_bytes)) + filename_bytes
        yield from file_to_generator(
            filename,
            buff=buff,
            remove=False,
            entete=b"")

    def limit_generator(generator, limit):
        """
        C'est un generateur qui cede les memes choses que 'generator'
        Seulement, afin d'eviter les boucles infinies, leve une exception
        si le generateur cede plus de packet que l'autorise 'limit'
        """
        for i, e in enumerate(generator):
            if i >= limit:
                raise MemoryError("Le generateur contient trop d'element, il doit y en avoir moins de %d." % limit)
            yield e

    # entete: </>message protocol</>
    try:                                                                # pour un affichage plus parlant
        message = "serialization of " + obj.__name__ + "..."            # on tente de recuperer le nom de l'objet
    except:                                                             # sinon
        message = "serialization of " + str(obj) + "..."                # on affiche un message pas tres explicite
    with raisin.Printer(message, signature=signature) as p:
        # verifications
        if psw is not None:
            if type(psw) is bytes:
                try:
                    if not raisin.re.search(r"-----BEGIN PUBLIC KEY-----(.|\n)+-----END PUBLIC KEY-----", psw.decode()):
                        raise ValueError("Une clef RSA publique au format PEM est attendue, ce n'est pas les cas.")
                except UnicodeDecodeError as e:
                    raise ValueError("Si il est de type (bytes), le mot de passe doit etre une clef publique RSA au format PEM, ce n'est pas la cas.") from e
            else:
                assert type(psw) is str, "Le mot de passe doit etre soit None, soit un 'str' soit une clef rsa publique au format PEM (bytes). Pas un %s." % type(psw)
            assert psw, "'psw' ne peut pas etre une chaine vide. En l'absence de mot de passe, psw=None."
        assert type(parallelization_rate) is int, "'parallelization_rate' doit etre un entier. Pas un %s." % type(parallelization_rate)
        assert 0 <= parallelization_rate <= 4, "Le taux de paralelisation doit etre compris entre 0 et 4 inclus. Pas %d." % parallelization_rate
        
        # serialisation
        if type(obj) == int:                                            # si l'objet est un entier
            if abs(obj) < 10**2000:                                     # si l'entier n'est pas bien gros
                p.show("small int->bytes")                              # alors on va prendre des racourcis
                entete = b"</>0000</>"                                  # precision de l'id et du protocol
                yield from generator_data(
                                cipher_data(
                                    entete + str(obj).encode(),
                                    psw=psw,
                                    parallelization_rate=0,
                                    signature=signature),
                                buff=buff)                              # on l'envoi vite fait bien fait
            else:                                                       # si l'entier est gros
                p.show("large int->bytes")                              # on le dit a l'utilisateur
                entete = b"</>0199</>"                                  # on met le bon texte mais avec le protocol pickle
                data = entete + pickle.dumps(obj)                       # serialisation directe avec pickle
                yield from generator_data(
                                cipher_data(
                                    compress_data(
                                        data,
                                        compresslevel=compresslevel,
                                        parallelization_rate=parallelization_rate,
                                        signature=signature),
                                    psw=psw,
                                    parallelization_rate=parallelization_rate,
                                    signature=signature),
                                buff=buff)                              # on retourne ces donnes la

        elif is_file(obj, copy_file):                                   # si l'objet est un nom de fichier
            p.show("filename + file_content->bytes")                    # mais qu'on doit copier le fichier avec

            yield from generator_to_generator(
                b"",
                cipher_generator(
                    compress_generator(
                        encapsule_filename(
                            obj,
                            buff=buff),
                        buff=buff,
                        compresslevel=compresslevel,
                        parallelization_rate=parallelization_rate,
                        extension=obj.split(".")[-1] if len(obj.split(".")) >= 2 else "",
                        signature=signature,),
                    psw=psw,
                    parallelization_rate=parallelization_rate,
                    signature=signature),
                buff=buff)
            
        elif type(obj) is str:                                          # maintenant, si c'est une chaine de caractere que l'on serialise
            if len(obj) < 250:                                          # si la chaine est rikiki
                p.show("small str->json->bytes")                        # on va sauter des etapes
                entete = b"</>0201</>"                                  # precision du protocol et du message
                yield from generator_data(
                                cipher_data(
                                    entete + json.dumps(obj).encode("utf-8"),
                                    psw=psw,
                                    parallelization_rate=0,
                                    signature=signature),
                                buff=buff)                              # on le serialise avec json pour aller plus vite
            elif len(obj) < buff:                                       # on essay d'optimiser et la ram, et la compression ainsi:
                p.show("medium str->json->bytes")                       # si la chaine est suffisement petite pour rester en RAM
                entete = b"</>0301</>"                                  # on garde le meme protocol, mais on ajoute une compression eventuelle
                yield from generator_to_generator(
                            b"",
                            cipher_generator(
                                compress_generator(
                                    generator_data(
                                        entete + json.dumps(obj).encode("utf-8"),
                                        buff=buff),
                                    buff=buff,
                                    compresslevel=compresslevel,
                                    parallelization_rate=parallelization_rate,
                                    extension="txt",
                                    signature=signature),
                                psw=psw,
                                parallelization_rate=parallelization_rate,
                                signature=signature),
                            buff=buff)
            else:                                                       # bon, si il est suffisement gros pour etre compresse
                p.show("large str->file")                               # si la chaine est grosse, on passe par un fichier
                entete = b"</>0416</>"                                  # comme c'est deja une chaine de caractere
                filename = os.path.join(str(raisin.temprep), str(uuid.uuid4()) + ".txt") # donc un objet adapte pour les flux
                with open(filename, "w", encoding="utf-8") as f:        # on ne le serialise pas vraiment
                    f.write(obj)                                        # on se contente de l'ecrir dans un fichier
                yield from generator_to_generator(
                                b"",
                                cipher_generator(
                                    compress_generator(
                                        file_to_generator(
                                            filename,
                                            buff=buff,
                                            remove=True,
                                            entete=entete),
                                        buff=buff,
                                        compresslevel=compresslevel,
                                        parallelization_rate=parallelization_rate,
                                        extension="txt",
                                        signature=signature),
                                    psw=psw,
                                    parallelization_rate=parallelization_rate,
                                    signature=signature),
                                buff=buff)

        elif type(obj) is bytes:                                        # si l'objet est deja serialiser
            if len(obj) < 300:                                          # mais que c'est suffisement petit pour ne pas subir de compression
                p.show("small bytes->bytes")                            # on va sauter des etapes
                entete = b"</>0604</>"                                  # precision du protocol et du message
                yield from generator_data(
                                cipher_data(
                                    entete + obj,
                                    psw=psw,
                                    parallelization_rate=0,
                                    signature=signature),
                                buff=buff)                               # on l'encripte juste si nessecaire
            elif len(obj) < buff:                                       # on essay d'optimiser et la ram, et la compression ainsi:
                p.show("medium bytes->bytes")                           # si la chaine est suffisement petite pour rester en RAM
                entete = b"</>0704</>"                                   # on garde le meme protocol, mais on ajoute une compression eventuelle
                yield from generator_to_generator(
                    b"",
                    cipher_generator(
                        compress_generator(
                            generator_data(
                                entete + obj,
                                buff=buff),
                            buff=buff,
                            compresslevel=compresslevel,
                            parallelization_rate=parallelization_rate,
                            extension="",
                            signature=signature),
                        psw=psw,
                        parallelization_rate=parallelization_rate,
                        signature=signature),
                    buff=buff)
            else:                                                       # bon, si il est suffisement gros pour etre compresse
                p.show("large bytes->file")                             # si la chaine est grosse, on passe par un fichier
                entete = b"</>0804</>"                                  # entete propre a cette serialisation
                filename = os.path.join(str(raisin.temprep), str(uuid.uuid4()) + ".bin") # generation du nom du fichier temporaire
                with open(filename, "wb") as f:                         # creation phisique du fichier
                    f.write(obj)                                        # don on y ecrit le contenu actuel
                yield from generator_to_generator(
                    b"",
                    cipher_generator(
                        compress_generator(
                            file_to_generator(
                                filename,
                                buff=buff,
                                remove=True,
                                entete=entete),
                            buff=buff,
                            compresslevel=compresslevel,
                            parallelization_rate=parallelization_rate,
                            extension="bin",
                            signature=signature),
                        psw=psw,
                        parallelization_rate=parallelization_rate,
                        signature=signature),
                    buff=buff)

        elif type(obj) is io.TextIOWrapper:                             # si il s'agit d'un fichier texte en lecture
            entete = b"</>0905</>"
            closed = b"\x01" if obj.closed else b"\x00"                 # 1 si le flux est ferme ou 0 si il est encore actif
            mode = obj.mode.encode("utf-8")                             # son mode ("r", "w", "a", ...)
            encoding = obj.encoding.encode("utf-8")                     # c'encodage dans lequel on doit lire le fichier
            errors = obj.errors.encode("utf-8")                         # les differents modes de gestion possible des erreur de lecture
            if closed != b"\x00":
                filename = os.path.join(str(raisin.temprep), str(uuid.uuid4()))
                with open(filename, "w"):
                    pass
                stream_position = b"0"
            else:
                filename = obj.name
                stream_position = str(obj.tell()).encode()               # la position en nombre de caractere du curseur courant par rapport au debut du fichier
            
            yield from generator_to_generator(
                b"",
                cipher_generator(
                    compress_generator(
                        file_to_generator(
                            filename,
                            buff=buff,
                            remove=False,
                            entete=b"".join([
                                entete,
                                size_to_tag(len(closed)),
                                closed,
                                size_to_tag(len(mode)),
                                mode,
                                size_to_tag(len(encoding)),
                                encoding,
                                size_to_tag(len(errors)),
                                errors,
                                size_to_tag(len(stream_position)),
                                stream_position])),
                        buff=buff,
                        compresslevel=compresslevel,
                        parallelization_rate=parallelization_rate,
                        extension=obj.name.split(".")[-1] if len(obj.name.split(".")) >= 2 else "",
                        signature=signature),
                    psw=psw,
                    parallelization_rate=parallelization_rate,
                    signature=signature),
                buff=buff)
            if closed != b"\x00":
                os.remove(filename)

        elif (type(obj) is io.BufferedReader) or (type(obj) is io.BufferedWriter):# si il s'agit d'un fichier binaire
            entete = b"</>1007</>"
            closed = b"\x01" if obj.closed else b"\x00"                 # 1 si le flux est ferme ou 0 si il est encore actif
            mode = obj.mode.encode("utf-8")                             # son mode ("r", "w", "a", ...)
            type_ = b"r" if type(obj) is io.BufferedReader else b"w"    # si c'est un io.BufferedReader ou un io.BufferedWriter
            if closed != b"\x00":
                filename = os.path.join(str(raisin.temprep), str(uuid.uuid4()))
                with open(filename, "w"):
                    pass
                stream_position = b"0"
            else:
                filename = obj.name
                stream_position = str(obj.tell()).encode()              # la position en nombre d'octet du curseur courant par rapport au debut du fichier

            yield from generator_to_generator(
                b"",
                cipher_generator(
                    compress_generator(
                        file_to_generator(
                            filename,
                            buff=buff,
                            remove=False,
                            entete=b"".join([
                                entete,
                                size_to_tag(len(closed)),
                                closed,
                                size_to_tag(len(mode)),
                                mode,
                                size_to_tag(len(type_)),
                                type_,
                                size_to_tag(len(stream_position)),
                                stream_position])),
                        buff=buff,
                        compresslevel=compresslevel,
                        parallelization_rate=parallelization_rate,
                        extension=obj.name.split(".")[-1] if len(obj.name.split(".")) >= 2 else "",
                        signature=signature),
                    psw=psw,
                    parallelization_rate=parallelization_rate,
                    signature=signature),
                buff=buff)

        elif type(obj) in (list, dict):                                 # si l'objet est une liste ou un dictionaire
            if is_jsonisable(obj, copy_file):                           # si il existe un algorithme performant pour serialiser cette liste
                if sys.getsizeof(obj) < buff:                           # si la liste ne prend pas trop de place 
                    if type(obj) is list:
                        p.show("small list jsonisable->bytes")
                        entete = b"</>1101</>"                          # alors on va la serializer dans la ram avec json
                    else:
                        p.show("small dict jsonisable->bytes")
                        entete = b"</>1701</>"
                    yield from generator_data(
                        cipher_data(
                            compress_data(
                                entete + json.dumps(obj).encode("utf-8"),
                                compresslevel=compresslevel,
                                parallelization_rate=parallelization_rate,
                                signature=signature),
                            psw=psw,
                            parallelization_rate=parallelization_rate,
                            signature=signature),
                        buff=buff)
                else:                                                   # dans le cas ou l'objet est un peu plus gros
                    if type(obj) is list:
                        p.show("large list jsonisable->bytes")
                        entete = b"</>1102</>"
                    else:
                        p.show("large dict jsonisable->bytes")
                        entete = b"</>1702</>"
                    filename = os.path.join(str(raisin.temprep), str(uuid.uuid4()) + ".json")
                    with open(filename, "w") as f:
                        json.dump(obj, f)
                    yield from generator_to_generator(
                                    b"",
                                    cipher_generator(
                                        compress_generator(
                                            file_to_generator(
                                                filename,
                                                buff=buff,
                                                remove=True,
                                                entete=entete),
                                            buff=buff,
                                            compresslevel=compresslevel,
                                            parallelization_rate=parallelization_rate,
                                            extension="json",
                                            signature=signature),
                                        psw=psw,
                                        parallelization_rate=parallelization_rate,
                                        signature=signature),
                                    buff=buff)
            else:
                if type(obj) is list:
                    p.show("list->bytes")
                    entete = b"</>1108</>"
                else:
                    p.show("dict->bytes")
                    entete = b"</>1814</>"
                yield from generator_to_generator(
                    b"",
                    cipher_generator(
                        compress_generator(
                            serialize_iterable(
                                obj if type(obj) is list else obj.items(),
                                buff=buff,
                                copy_file=copy_file,
                                entete=entete,
                                signature=signature),
                            buff=buff,
                            compresslevel=compresslevel,
                            parallelization_rate=parallelization_rate,
                            extension=None,
                            signature=signature),
                        psw=psw,
                        parallelization_rate=parallelization_rate,
                        signature=signature),
                    buff=buff)
        
        elif type(obj) is tuple:                                        # si l'objet est un tuple
            p.show("tuple->bytes")
            entete = b"</>1209</>"
            yield from generator_to_generator(
                    b"",
                    cipher_generator(
                        compress_generator(
                            serialize_iterable(
                                obj,
                                buff=buff,
                                copy_file=copy_file,
                                entete=entete,
                                signature=signature),
                            buff=buff,
                            compresslevel=compresslevel,
                            parallelization_rate=parallelization_rate,
                            extension=None,
                            signature=signature),
                        psw=psw,
                        parallelization_rate=parallelization_rate,
                        signature=signature),
                    buff=buff)
        
        elif inspect.isclass(obj):                                      # si l'objet est une classe, qu'elle soit integree ou creee dans du code python
            p.show("class->bytes")
            entete = b"</>1513</>"
            yield from generator_to_generator(
                    b"",
                    cipher_generator(
                        compress_generator(
                            serialize_class(
                                obj,
                                buff=buff,
                                signature=signature),
                            buff=buff,
                            compresslevel=compresslevel,
                            parallelization_rate=parallelization_rate,
                            extension=None,
                            signature=signature),
                        psw=psw,
                        parallelization_rate=parallelization_rate,
                        signature=signature),
                    buff=buff)

        elif inspect.ismodule(obj):                                     # si l'objet est un module
            p.show("module->bytes")
            raise NotImplementedError()
        
        elif inspect.isfunction(obj):                                   # si l'objet est une fonction python, qui inclut des fonctions creees par une expression lambda
            p.show("function->bytes")
            raise NotImplementedError()

        elif inspect.isgeneratorfunction(obj):                          # si l'objet est une fonction generatrice python
            p.show("generatorfunction->bytes")
            raise NotImplementedError()

        elif inspect.isgenerator(obj):                                  # si l'objet est un generateur
            p.show("generator->bytes")
            limit = 10_000_000 # nombre max de packets cedes par le generateur
            entete = b"</>1915</>"
            yield from generator_to_generator(
                    b"",
                    cipher_generator(
                        compress_generator(
                            serialize_iterable(
                                limit_generator(
                                    obj,
                                    limit=limit),
                                buff=buff,
                                copy_file=copy_file,
                                entete=entete,
                                signature=signature),
                            buff=buff,
                            compresslevel=compresslevel,
                            parallelization_rate=parallelization_rate,
                            extension=None,
                            signature=signature),
                        psw=psw,
                        parallelization_rate=parallelization_rate,
                        signature=signature),
                    buff=buff)

        elif inspect.iscoroutinefunction(obj):                          # si l'objet est une fonction coroutine (une fonction definie avec une syntaxe async def)
            p.show("coroutinefunction->bytes")
            raise NotImplementedError()

        elif inspect.iscoroutine(obj):                                  # si l'objet est une coroutine creee par une fonction async def
            p.show("coroutine->bytes")
            raise NotImplementedError()

        elif inspect.isawaitable(obj):                                  # si l'objet peut etre utilise dans une expression await
            p.show("awaitable->bytes")
            raise NotImplementedError()

        elif inspect.istraceback(obj):                                  # si l'objet est une traceback
            p.show("traceback->bytes")
            raise NotImplementedError()

        elif inspect.isframe(obj):                                      # si l'objet est un cadre
            p.show("frame->bytes")
            raise NotImplementedError()

        elif inspect.iscode(obj):                                       # si l'objet est un code
            p.show("code->bytes")
            raise NotImplementedError()

        elif inspect.isbuiltin(obj):                                    # si l'objet est une fonction integree ou une methode integree liee
            p.show("builtin->bytes")
            raise NotImplementedError()

        elif inspect.isroutine(obj):                                    # si l'objet est une fonction ou une methode définie par l'utilisateur ou integree
            p.show("routine->bytes")
            raise NotImplementedError()

        elif inspect.isabstract(obj):                                   # si l'objet est une classe de base abstraite
            p.show("absstract->bytes")
            raise NotImplementedError()

        elif inspect.ismethoddescriptor(obj):                           # si l'objet est un descripteur de methode, mais pas si ismethod() , isclass() , isfunction() ou isbuiltin() sont vrais
            p.show("methoddescriptor->bytes")
            raise NotImplementedError()

        elif inspect.isdatadescriptor(obj):                             # si l'objet est un descripteur de donnees
            p.show("datadescriptor->bytes")
            raise NotImplementedError()

        elif inspect.isgetsetdescriptor(obj):                           # si l'objet est un descripteur de getset
            p.show("getsetdescriptor->bytes")
            raise NotImplementedError()

        elif inspect.ismemberdescriptor(obj):                           # si l'objet est un descripteur de membre
            p.show("memberdescriptor->bytes")
            raise NotImplementedError()

        else:                                                           # dans le cas ou l'objet est inconnu
            if sys.getsizeof(obj) > buff:                               # si l'objet est tres lourd en memoire
                p.show("large unknown object->pickle->file")            # on va passer par un fichier
                entete = b"</>9898</>"                                  # mais avant, on specifi le protocole
                filename = os.path.join(str(raisin.temprep), str(uuid.uuid4()) + ".pk") # que l'on met par precaution dans un repertoir temporaire
                with open(filename, "wb") as f:                         # afin d'eviter toute surcharge dans la memoire
                    pickle.dump(obj, f)                                 # on utilise pickle, qui serialise pas mal de choses
                yield from generator_to_generator(
                                b"",
                                cipher_generator(
                                    compress_generator(
                                        file_to_generator(
                                            filename,
                                            buff=buff,
                                            remove=True,
                                            entete=entete),
                                        buff=buff,
                                        compresslevel=compresslevel,
                                        parallelization_rate=parallelization_rate,
                                        extension="pk",
                                        signature=signature),
                                    psw=psw,
                                    parallelization_rate=parallelization_rate,
                                    signature=signature),
                                buff=buff)
            else:                                                       # si le fichier est suffisement petit pour pouvoir tout faire dans la RAM
                p.show("little unknown object->pickle->bytes")          # l'utilisateur est averti de l'opperation iminente
                entete = b"</>9999</>"
                yield from generator_to_generator(
                            b"",
                            cipher_generator(
                                compress_generator(
                                    generator_data(
                                        entete + pickle.dumps(obj),
                                        buff=buff),
                                    buff=buff,
                                    compresslevel=compresslevel,
                                    parallelization_rate=parallelization_rate,
                                    extension="txt",
                                    signature=signature),
                                psw=psw,
                                parallelization_rate=parallelization_rate,
                                signature=signature),
                            buff=buff)

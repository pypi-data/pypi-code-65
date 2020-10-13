#!/usr/bin/env python3
#-*- coding: utf-8 -*-

__version__ = "3.0.0"
__author__  = "Robin RICHARD <raisin@ecomail.fr>"
__all__     = ["compress", "decompress", "dump", "load", "copy",
                "serialize", "deserialize", "open", "solve",
               "Map", "map", "Process", "process", "Scan", "scan",
               "communication", "geometry", "reader", "worker",
               "graph", "raisin", "serialization", "tools"]

import logging
import sys
try:
    import numpy
except ImportError:
    logging.warn("'numpy' failed to import. Some process will be slow.")
    numpy = None
try:
    import psutil
except ImportError:
    logging.warn("'psutil' failed to import, no possibility to get the cpu temperature.")
    psutil = None
try:
    import regex as re
except ImportError:
    logging.warn("'regex' failed to import. 're' is going to be used, but it is less efficient than regex.")
    import re
try:
    import sympy
    from sympy.core.function import count_ops
    try:
        import giacpy
    except ImportError:
        logging.warn("'giacpy' failed to import. Sometimes sympy is not able to compute but 'giacpy'"
                      "knows how to do that, especially concerning implicit operators.")
        giacpy = None
except ImportError:
    logging.warn("'sympy' failed to import. There is no symbolic computing.")
    sympy = None
    giacpy = None
    count_ops = None


from . import tools                             # on est oblige de le metre avant pour eviter les imports circulaires
timeout_decorator = tools.timeout_decorator     # permet de limiter le temps d'execution d'une fonction
Id = tools.Id                                   # class qui permet d'avoir des informations sur soi
Lock = tools.Lock                               # objet verrou
LockDecorator = tools.LockDecorator             # verrou sous forme de decorateur
Printer = tools.Printer                         # permet un affichage des opperations en cours
temprep = tools.Temprep(destroy=True)           # objet dons la representation est un dossier temporaire
_ = tools.Translator(src="en", dest="auto")     # permet de traduire les messages (callable)
get_temperature = tools.get_temperature         # permet dans certaine conditions de recuperer la temperature du CPU
sys.excepthook = tools.crash_report             # envoi un rapport de plantage
improve_recursion_decorateur = tools.improve_recursion_decorateur # permet d'augmenter la taille de la pile sur une fonction

from . import communication
from . import geometry
from . import reader
from . import worker
from . import graph
from . import raisin
from . import serialization
from . import solver



# accessoires

def compress(obj, *, compresslevel=3, psw=None, copy_file=False, parallelization_rate=0, signature=None):
    """
    |===============================================================|
    | Serialise, compresse et chiffre simplement tous type d'objet. |
    |===============================================================|

    parametres
    ----------
    :param obj: N'importe quel type d'objet python, celui a serialiser.
    :param compresslevel: Permet de compresser sans perte le resultat.
    :type compresslevel: int
        0: Pas de compression du tout.
        1: Legere compression, la plus rapide en temps de calcul.
        2: Legere compression qui maximise le ratio 'taille_gagnee/temps'.
        3: Moyenne compression qui vise un ratio environ egal a 95% du ratio maximum.
        4: Grosse compression qui ne se preocupe pas du temps.
    :param psw: Permet de chiffrer la valeur de retour
    :type psw: str, bytes, None
        str: Chiffre avec l'algorithme AES.
        bytes: Clef publique au format PEM, RSA est utilise.
        None: Ne chiffre rien du tout
    :param copy_file: Permet de copier le fichier si 'obj' est un nom de fichier
    :type copy_file: bool
        True: Le fichier est copier et fait parti du resultat.
              Au moment de la deserialisation, le fichier sera regenere.
        False: Si 'obj' est un nom de fichier, il sera seulement considerer comme un 'str'.
    :param parallelization_rate: Permet de partager le calcul affin de mieu profiter des resources de l'ordinateur
    :type parallelization_rate: int
        0: Aucune parallelisation, tout est excecuter dans le processus courant.
        1: Pseudo parallelisation, reparti les operations dans des threads du module 'threading'.
        2: Legere parallelisation, utilise les differents coeurs de la machine avec le module 'multiprocessing'.
    :param signature: N'importe quel objet qui permet d'afficher dans la bonne colone du terminal

    sortie
    ------
    :return: L'information permetant d'effectuer une bijection vers l'objet 'obj' sous forme de gentil caracteres ASCII imprimables.
    :rtype: str

    exemple
    -------
    :Example:
    >>> import raisin
    >>> raisin.compress(123456789)
    'f2Y@c30Mc3MLfz4OcPgRdzsUej0M..'
    >>> raisin.compress(123456789, psw="mot de passe")
    'f2Y@ejsVdPMLfBYyG69Lq8CasrgYmyCfJRfeDTWCCAT3YDJhTABO8Z7bA8_WXZ4PFEbZWK5QBEZ8TLDhY30M..'
    >>>
    """
    assert type(compresslevel) is int
    assert 0 <= compresslevel <= 4
    if psw is not None:
        if type(psw) is bytes:
            assert re.search(r"-----BEGIN PUBLIC KEY-----(.|\n)+-----END PUBLIC KEY-----", psw.decode())
        else:
            assert type(psw) is str
            assert psw != ""
    assert type(copy_file) is bool
    assert type(parallelization_rate) is int
    assert 0 <= parallelization_rate <= 2
    
    with Printer("Compress...", signature=signature):
        return serialization.compress(
                                obj,
                                compresslevel=compresslevel,
                                psw=psw,
                                copy_file=copy_file,
                                parallelization_rate=parallelization_rate, 
                                signature=signature)

def decompress(chaine, *, psw=None, parallelization_rate=0, signature=None):
    """
    |=====================================|
    | Bijection de la fonction 'compress' |
    |=====================================|

    parametres
    ----------
    :param chaine: Objet python serialise par la fonction 'compress'.
    :type chaine: str
    :param psw: Permet de dechiffrer l'entree
    :type psw: str, bytes, None
        str: Dechiffre avec l'algorithme AES.
        bytes: Clef privee non chiffree au format PEM, RSA est utilise.
        None: Ne tente rien du tout.
    :param parallelization_rate: Permet de partager le calcul affin de mieu profiter des resources de l'ordinateur
    :type parallelization_rate: int
        0: Aucune parallelisation, tout est excecuter dans le processus courant.
        1: Pseudo parallelisation, reparti les operations dans des threads du module 'threading'.
        2: Legere parallelisation, utilise les differents coeurs de la machine avec le module 'multiprocessing'.
    :param signature: N'importe quel objet qui permet d'afficher dans la bonne colone du terminal.

    sortie
    ------
    :return: L'objet de depart qui a ete serialise

    exemple
    -------
    :Example:
    >>> import raisin
    >>> raisin.decompress('f2Y@c30Mc3MLfz4OcPgRdzsUej0M..')
    123456789
    >>>
    """
    assert type(chaine) is str
    if psw is not None:
        if type(psw) is bytes:
            assert re.search(r"-----BEGIN RSA PRIVATE KEY-----(.|\n)+-----END RSA PRIVATE KEY-----", psw.decode())
        else:
            assert type(psw) is str
            assert psw != ""
    assert type(parallelization_rate) is int
    assert 0 <= parallelization_rate <= 2

    with Printer("decompress...", signature=signature):
        return serialization.decompress(
            chaine,
            psw=psw,
            parallelization_rate=parallelization_rate,
            signature=signature)

def dump(obj, f, *, compresslevel=0, psw=None, copy_file=True, parallelization_rate=0, signature=None):
    """
    |====================================|
    | Serialise un objet dans un fichier |
    |====================================|
    
    parametres
    ----------
    :param obj: N'importe quel type d'objet python, celui a serialiser.
    :param f: Flux d'ecriture des donnees
    :param compresslevel: Permet de compresser sans perte le resultat.
    :type compresslevel: int
        0: Pas de compression du tout.
        1: Legere compression, la plus rapide en temps de calcul.
        2: Legere compression qui maximise le ratio 'taille_gagnee/temps'.
        3: Moyenne compression qui vise un ratio environ egal a 95% du ratio maximum.
        4: Grosse compression qui ne se preocupe pas du temps.
    :param psw: Permet de chiffrer la valeur de retour
    :type psw: str, bytes, None
        str: Chiffre avec l'algorithme AES.
        bytes: Clef publique au format PEM, RSA est utilise.
        None: Ne chiffre rien du tout
    :param copy_file: Permet de copier le fichier si 'obj' est un nom de fichier
    :type copy_file: bool
        True: Le fichier est copier et fait parti du resultat.
              Au moment de la deserialisation, le fichier sera regenere.
        False: Si 'obj' est un nom de fichier, il sera seulement considerer comme un 'str'.
    :param parallelization_rate: Permet de partager le calcul affin de mieu profiter des resources de l'ordinateur
    :type parallelization_rate: int
        0: Aucune parallelisation, tout est excecuter dans le processus courant.
        1: Pseudo parallelisation, reparti les operations dans des threads du module 'threading'.
        2: Legere parallelisation, utilise les differents coeurs de la machine avec le module 'multiprocessing'.
    :param signature: N'importe quel objet qui permet d'afficher dans la bonne colone du terminal.

    sortie
    ------
    :return: L'objet de depart qui a ete serialise

    exemple
    -------
    :Example:
    >>> import raisin
    >>> with open("fichier", "wb") as f:
    ...     raisin.dump(123456789, f)
    ...
    >>>
    """
    assert type(compresslevel) is int
    assert 0 <= compresslevel <= 4
    if psw is not None:
        if type(psw) is bytes:
            assert re.search(r"-----BEGIN PUBLIC KEY-----(.|\n)+-----END PUBLIC KEY-----", psw.decode())
        else:
            assert type(psw) is str
            assert psw != ""
    assert type(copy_file) is bool
    assert type(parallelization_rate) is int
    assert 0 <= parallelization_rate <= 2

    for pack in serialize(obj,
                signature=signature,
                compresslevel=compresslevel,
                copy_file=copy_file,
                parallelization_rate=parallelization_rate,
                psw=psw):
        f.write(pack)

def load(f, *, parallelization_rate=0, psw=None, signature=None):
    """
    |=================================|
    | Bijection de la fonction 'dump' |
    |=================================|

    parametres
    ----------
    :param f: Flux en lecture contenant les donnees fournis par 'dump'.
    :param parallelization_rate: Permet de partager le calcul affin de mieu profiter des resources de l'ordinateur
    :type parallelization_rate: int
        0: Aucune parallelisation, tout est excecuter dans le processus courant.
        1: Pseudo parallelisation, reparti les operations dans des threads du module 'threading'.
        2: Legere parallelisation, utilise les differents coeurs de la machine avec le module 'multiprocessing'.
    :param psw: Permet de dechiffrer les donnees
    :type psw: str, bytes, None
        str: Dechiffre avec l'algorithme AES.
        bytes: Clef privee non chiffree au format PEM, RSA est utilise.
        None: Ne tente rien du tout.
    :param signature: N'importe quel objet qui permet d'afficher dans la bonne colone du terminal.

    sortie
    ------
    :return: L'objet de depart qui a ete serialise

    exemple
    -------
    :Example:
    >>> import raisin
    >>> with open("fichier", "wb") as f:
    ...     raisin.dump(123456789, f)
    ...
    >>> with open("fichier", "rb") as f:
    ...     obj = raisin.load(f)
    ...
    >>> obj
    123456789
    >>>
    """
    assert type(chaine) is str
    if psw is not None:
        if type(psw) is bytes:
            assert re.search(r"-----BEGIN RSA PRIVATE KEY-----(.|\n)+-----END RSA PRIVATE KEY-----", psw.decode())
        else:
            assert type(psw) is str
            assert psw != ""
    assert type(parallelization_rate) is int
    assert 0 <= parallelization_rate <= 2

    return deserialize(f, parallelization_rate=parallelization_rate, psw=psw, signature=signature)

def copy(obj, *, signature=None):
    """
    |===========================================|
    | Faire une copie vraie: dupliquer un objet |
    |===========================================|

    :param obj: N'importe quel objet que l'on shouaite copier.
    :param signature: N'importe quel objet qui permet d'afficher dans la bonne colone du terminal.
    :return: Une copie de l'objet 'obj'

    :Example:
    >>> import raisin
    >>> a = {0: "a", 1: "b"}
    >>> a
    {0: 'a', 1: 'b'}
    >>> b = a
    >>> b[1] = "c"              # a est aussi affecte
    >>> a, b
    ({0: 'a', 1: 'c'}, {0: 'a', 1: 'c'})
    >>> b = raisin.copy(a)
    >>> b[1] = "b"              # a n'est pas affecte
    >>> a, b
    ({0: 'a', 1: 'c'}, {0: 'a', 1: 'b'})
    >>>
    """
    with Printer("Copy of '%s'..." % obj):
        return deserialize(
                    serialize(
                        obj,
                        signature=signature,
                        compresslevel=0,
                        copy_file=True,
                        parallelization_rate=0),
                    parallelization_rate=0,
                    signature=signature)

def serialize(obj, *, buff=1024*1024, compresslevel=-1, psw=None, copy_file=True, parallelization_rate=1, signature=None):
    """
    |====================================================|
    | Serialise, compresse et chiffre tous type d'objet. |
    |====================================================|

    parametres
    ----------
    :param obj: N'importe quel type d'objet python, celui a serialiser.
    :param buff: Le surplus de RAM ne depasse pas quelques multiples de 'buff' octets.
                 C'est aussi la taille en octet de paquets cedes.
    :type buff: int
    :param compresslevel: Permet de compresser sans perte le resultat.
    :type compresslevel: int
        -1: Intelligente, compresse au mieu en fonction du debit demande.
            Si 'parallelization_rate' >= 0
        0: Pas de compression du tout.
        1: Legere compression, la plus rapide en temps de calcul.
        2: Legere compression qui maximise le ratio 'taille_gagnee/temps'.
        3: Moyenne compression qui vise un ratio environ egal a 95% du ratio maximum.
        4: Grosse compression qui ne se preocupe pas du temps.
    :param psw: Permet de chiffrer la valeur de retour.
    :type psw: str, bytes, None
        str: Chiffre avec l'algorithme AES.
        bytes: Clef publique au format PEM, RSA est utilise.
        None: Ne chiffre rien du tout
    :param copy_file: Permet de copier le fichier si 'obj' est un nom de fichier.
    :type copy_file: bool
        True: Le fichier est copier et fait parti du resultat.
              Au moment de la deserialisation, le fichier sera regenere.
        False: Si 'obj' est un nom de fichier, il sera seulement considerer comme un 'str'.
    :param parallelization_rate: Permet de partager le calcul affin de mieu profiter des resources de l'ordinateur.
    :type parallelization_rate: int
        0: Aucune parallelisation, tout est excecuter dans le processus courant.
        1: Pseudo parallelisation, reparti les operations dans des threads du module 'threading'.
        2: Legere parallelisation, utilise les differents coeurs de la machine avec le module 'multiprocessing'.
    :param signature: N'importe quel objet qui permet d'afficher dans la bonne colone du terminal

    sortie
    ------
    :return: Une suite de 'bytes' qui contient l'information suffisante pour reconstiuer l'objet.
    :rtype: <class 'generator'>

    exemple
    -------
    :Example:
    >>> import raisin
    >>> def send(data):
    ...     ... # envoi les donnes
    ...
    >>> for pack in raisin.serialize(123456): # Le fait de generer des paquets ne surcharge pas la RAM.
    ...     send(pack)                        # Le flux est maximise car pandant ce temps, les packets suivant sont compresses
    ...
    >>>
    """
    assert type(buff) is int
    assert buff > 0
    assert type(compresslevel) is int
    assert -1 <= compresslevel <= 4
    if psw is not None:
        if type(psw) is bytes:
            assert re.search(r"-----BEGIN PUBLIC KEY-----(.|\n)+-----END PUBLIC KEY-----", psw.decode())
        else:
            assert type(psw) is str
            assert psw != ""
    assert type(copy_file) is bool
    assert type(parallelization_rate) is int
    assert 0 <= parallelization_rate <= 2

    yield from serialization.serialize(
                                        obj,
                                        signature=signature,
                                        buff=buff,
                                        compresslevel=compresslevel,
                                        copy_file=copy_file,
                                        parallelization_rate=parallelization_rate,
                                        psw=psw)

def deserialize(data, *, parallelization_rate=0, psw=None, signature=None):
    """
    |======================================|
    | Bijection de la fonction 'serialize' |
    |======================================|

    parametres
    ----------
    :param data: Objet python serialise par la fonction 'serialize'.
    :type data: bytes,
                <class 'generator'> (qui ne cede que des bytes),
                Flux lecture binaire (io.BufferedReader), 
    :param psw: Permet de dechiffrer l'entree
    :type psw: str, bytes, None
        str: Dechiffre avec l'algorithme AES.
        bytes: Clef privee non chiffree au format PEM, RSA est utilise.
        None: Ne tente rien du tout.
    :param parallelization_rate: Permet de partager le calcul affin de mieu profiter des resources de l'ordinateur.
    :type parallelization_rate: int
        0: Aucune parallelisation, tout est excecuter dans le processus courant.
        1: Pseudo parallelisation, reparti les operations dans des threads du module 'threading'.
        2: Legere parallelisation, utilise les differents coeurs de la machine avec le module 'multiprocessing'.
    :param signature: N'importe quel objet qui permet d'afficher dans la bonne colone du terminal.

    sortie
    ------
    :return: L'objet de depart qui a ete serialise

    exemple
    -------
    :Example:
    >>> import raisin
    >>> raisin.deserialize(b'</>0000</>123456789')
    123456789
    >>>
    """
    if psw is not None:
        if type(psw) is bytes:
            assert re.search(r"-----BEGIN RSA PRIVATE KEY-----(.|\n)+-----END RSA PRIVATE KEY-----", psw.decode())
        else:
            assert type(psw) is str
            assert psw != ""
    assert type(parallelization_rate) is int
    assert 0 <= parallelization_rate <= 2

    return serialization.deserialize(data, parallelization_rate=parallelization_rate, psw=psw, signature=signature)

def open(file, mode="", buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None, signature=None, **kwds):
    """
    extension de la methode '<built-in function open>'
    'mode' peut prendre differentes valeurs:
        -"r" (read):
            renvoi l'objet _io.TextIOWrapper en mode "r"
        -"a" (append):
            renvoi l'objet _io.TextIOWrapper en mode "a"
        -"w" (write):
            renvoi l'objet _io.TextIOWrapper en mode "w"
        -"rb" (read binary):
            renvoi l'objet _io.BufferedReader
        -"ab" (append binary):
            renvoi l'objet _io.BufferedWriter
        -"wb" (write binary):
            renvoi l'objet _io.BufferedWriter
        -"rp" (read python):
            renvoi un objet specialiste de la lecture des fichiers python
            il est capable de normaliser le texte et retirer les commentaires
            il permet aussi une analyse poussee des ligne de codes
        -"rc" (read csv):
            renvoi un dictionaire contenant les valeurs de ce csv
        -"" (gros melange):
            dans le cas ou la methode 'read' ou __iter__ est appelle:
                -renvoi des objets deserialiser si le fichier en encapsule
                -renvoi du str si tous le fichier est encode en utf-8
                    -avec normalisation syntaxique dans le cas d'un fichier python
                -renvoi du bytes si ce n'est rien de tous ca
            dans le cas ou la methode 'write' est appelee:
                -ecrit du texte tant que seul du STR est passe en parametre
                -ecrit du binaire tant que seul du BYTES est passe en parametre
                -serialise et encapsule le reste si un objet autre est passe en parametre
    """
    return reader.open_extend(file, mode=mode, buffering=buffering, encoding=encoding, errors=errors, newline=newline, closefd=closefd, opener=opener, signature=signature, **kwds)

def solve(f, *symbols, **flags):
    """
    Algebraically solves equations and systems of equations.

    Currently supported are:
        - polynomial,
        - transcendental
        - piecewise combinations of the above
        - systems of linear and polynomial equations
        - systems containing relational expressions.

    Input is formed as:
    
    * f
        - a single Expr or Poly that must be zero,
        - an Equality
        - a Relational expression
        - a Boolean
        - iterable of one or more of the above

    * symbols (object(s) to solve for) specified as
        - none given (other non-numeric objects will be used)
        - single symbol
        - denested list of symbols
          e.g. solve(f, x, y)
        - ordered iterable of symbols
          e.g. solve(f, [x, y])

    * flags
        'dict'=True (default is False)
            return list (perhaps empty) of solution mappings
        'set'=True (default is False)
            return list of symbols and set of tuple(s) of solution(s)
        'exclude=[] (default)'
            don't try to solve for any of the free symbols in exclude;
            if expressions are given, the free symbols in them will
            be extracted automatically.
        'check=True (default)'
            If False, don't do any testing of solutions. This can be
            useful if one wants to include solutions that make any
            denominator zero.
        'numerical=True (default)'
            do a fast numerical check if ``f`` has only one symbol.
        'minimal=True (default is False)'
            a very fast, minimal testing.
        'warn=True (default is False)'
            show a warning if checksol() could not conclude.
        'simplify=True (default)'
            simplify all but polynomials of order 3 or greater before
            returning them and (if check is not False) use the
            general simplify function on the solutions and the
            expression obtained when they are substituted into the
            function which should be zero
        'force=True (default is False)'
            make positive all symbols without assumptions regarding sign.
        'rational=True (default)'
            recast Floats as Rational; if this option is not used, the
            system containing floats may fail to solve because of issues
            with polys. If rational=None, Floats will be recast as
            rationals but the answer will be recast as Floats. If the
            flag is False then nothing will be done to the Floats.
        'manual=True (default is False)'
            do not use the polys/matrix method to solve a system of
            equations, solve them one at a time as you might "manually"
        'implicit=True (default is False)'
            allows solve to return a solution for a pattern in terms of
            other functions that contain that pattern; this is only
            needed if the pattern is inside of some invertible function
            like cos, exp, ....
        'particular=True (default is False)'
            instructs solve to try to find a particular solution to a linear
            system with as many zeros as possible; this is very expensive
        'quick=True (default is False)'
            when using particular=True, use a fast heuristic instead to find a
            solution with many zeros (instead of using the very slow method
            guaranteed to find the largest number of zeros possible)
        'cubics=True (default)'
            return explicit solutions when cubic expressions are encountered
        'quartics=True (default)'
            return explicit solutions when quartic expressions are encountered
        'quintics=True (default)'
            return explicit solutions (if possible) when quintic expressions
            are encountered
        """
    return solver.solve(f, *symbols, **flags)


#calcul partage

class Map(raisin.Map):
    """
    |=================================|
    | Comme 'map' mais en plus souple |
    |=================================|

    :Example:
    >>> import raisin
    >>> def foo(x):
    ...    return x**2
    ...
    >>> m = raisin.Map(foo, [0, 1, 2, 3])
    >>> m.start()           # rend la main imediatement
    >>> list(m.get())
    [0, 1, 4, 9]
    >>>
    """
    def __init__(self,
                target,
                *iterables,
                force=True,
                timeout=3600*24*31,
                job_timeout=3600*48,
                save=True,
                parallelization_rate=4,
                ordered=True,
                signature=None):
        """
        :param target: Fonction qui doit etre evaluee plein de fois.
        :type target: callable
        :param iterables: Chaque iterable associes a chacuns des arguments de la fonction, le premier iterable epuise arrette les autres.
        :param force: Permet de relancer le calcul meme si il le resultat est deja enregistre.
        :type force: bool
        :param timeout: Permet de lever une exception si ca met trop de temps en tout.
        :type timeout: int
        :param job_timeout: Permet de lever une exception sur chaque evaluation trop lente. Les autres threads continuent de tourner.
        :type job_timeout: int
        :param save: Permet de decider si le resultat est enregistrer.
        :type save: bool
            True: Le resultat est enregistre si cela en vaut la peine (gain de vitesse).
            False: Le resultat n'est pas enregistre nul part (il faut tout recommencer a chaque fois, pas de reprise possible)
        :param parallelization_rate: Permet de partager le calcul affin de mieu profiter des resources de l'ordinateur.
        :type parallelization_rate: int
            0: Aucune parallelisation, tout est excecuter dans le processus courant.
            1: Pseudo parallelisation, reparti les operations dans des threads du module 'threading'.
            2: Legere parallelisation, utilise les differents coeurs de la machine avec le module 'multiprocessing'.
            3: Grosse parallelisation, utilise toutes les ressources disponible dans le reseau local LAN.
            4: Monstrueuse parallelisation, utilise toutes les ressources accessibles dans le monde entier!
        :param ordered: Force a ceder les resultat dans l'ordre
        :type ordered: bool
        :param signature: N'importe quel objet qui permet d'afficher dans la bonne colone du terminal.
        """
        assert callable(target)
        assert type(force) is bool
        assert type(timeout) is int
        assert timeout > 0
        assert type(job_timeout) is int
        assert job_timeout > 0
        assert type(save) is bool
        assert type(parallelization_rate) is int
        assert 0 <= parallelization_rate <= 4
        assert type(ordered) is bool

        raisin.Map.__init__(self,
                    target,
                    *iterables,
                    force=force,
                    timeout=timeout,
                    job_timeout=job_timeout,
                    save=save,
                    parallelization_rate=parallelization_rate,
                    ordered=ordered,
                    signature=signature)

def map(*args, **kwargs):
    """
    |=======================================================================|
    | Make an iterator that computes the function using arguments from      |
    | each of the iterables. Stops when the shortest iterable is exhausted. |
    |=======================================================================|

    :seealso: raisin.Map

    sortie
    ------
    :return: Chaque evaluation de la fonction pour chaque argument cedes par l'iterable le plus vite epuise.
    :rtype: <class 'generator'>

    exemple
    -------
    :Example:
    >>> import raisin
    >>> def foo(x):
    ...    return x**2
    ...
    >>> list(raisin.map(foo, [1, 2, 3]))
    [1, 4, 9]
    >>>
    """
    m = Map(*args, **kwargs)
    m.start()
    yield from m.get()

class Process(raisin.Process):
    """
    |=====================================|
    | Comme 'process' mais en plus souple |
    |=====================================|

    :Example:
    >>> import raisin
    >>> def foo(x):
    ...     return x**2
    ...
    >>> p1 = raisin.Process(foo, args=(2,))
    >>> p2 = raisin.Process(foo, args=(3,))
    >>> p1.start()
    >>> p2.start()
    >>> (p1.get(), p2.get())
    (4, 9)
    >>>
    """
    def __init__(self,
                target,
                args=(),
                kwds={},
                *,
                force=True,
                timeout=3600*24*31,
                job_timeout=3600*48,
                save=True,
                parallelization_rate=4,
                signature=None):
        """
        :param target: Fonction qui doit etre evaluee plein de fois.
        :type target: callable
        :param args: Ensemble des arguments passes a la fonction. Devient 'target(*args)'.
        :type args: tuple
        :para kwds: dict
        :param force: Permet de relancer le calcul meme si il le resultat est deja enregistre.
        :type force: bool
        :param timeout: Permet de lever une exception si ca met trop de temps en tout.
        :type timeout: int
        :param job_timeout: Permet de lever une exception sur chaque evaluation trop lente. Les autres threads continuent de tourner.
        :type job_timeout: int
        :param save: Permet de decider si le resultat est enregistrer.
        :type save: bool
            True: Le resultat est enregistre si cela en vaut la peine (gain de vitesse).
            False: Le resultat n'est pas enregistre nul part (il faut tout recommencer a chaque fois, pas de reprise possible)
        :param parallelization_rate: Permet de partager le calcul affin de mieu profiter des resources de l'ordinateur.
        :type parallelization_rate: int
            0: Aucune parallelisation, tout est excecuter dans le processus courant.
            1: Pseudo parallelisation, reparti les operations dans des threads du module 'threading'.
            2: Legere parallelisation, utilise les differents coeurs de la machine avec le module 'multiprocessing'.
            3: Grosse parallelisation, utilise toutes les ressources disponible dans le reseau local LAN.
            4: Monstrueuse parallelisation, utilise toutes les ressources accessibles dans le monde entier!
        :param signature: N'importe quel objet qui permet d'afficher dans la bonne colone du terminal.
        """
        assert callable(target)
        assert type(args) is tuple
        assert type(kwds) is dict
        assert type(force) is bool
        assert type(timeout) is int
        assert timeout > 0
        assert type(job_timeout) is int
        assert job_timeout > 0
        assert type(save) is bool
        assert type(parallelization_rate) is int
        assert 0 <= parallelization_rate <= 4
        
        raisin.Process.__init__(self,
                    target,
                    args,
                    kwds,
                    force=force,
                    timeout=timeout,
                    job_timeout=job_timeout,
                    save=save,
                    parallelization_rate=parallelization_rate,
                    signature=signature)

def process(target, args=(), kwds={}, **kwargs):
    """
    |========================================|
    | Equivalent of 'target(*args, **kwds)'. |
    |========================================|

    Meme si elle parait inutile, cette fonction permet
    De soulager la charge de calcul dans un thread du module 'threading'.
    Cela permet aussi d'isoler la fonction pour la
    rendre completement etanche au reste du programme.

    :seealso: raisin.Process

    sortie
    ------
    :return: La valeur renvoyee par 'target(*args, **kwds)'.

    exemple
    -------
    :Example:
    >>> import raisin
    >>> def f(x, y):
    ...    return x**2 + y
    >>> raisin.process(f, args=(2, 0))
    4
    >>>
    """
    p = Process(target, args=args, kwds=kwds, **kwargs)
    p.start()
    return p.get()

class Scan(raisin.Scan):
    """
    |==================================|
    | Comme 'scan' mais en plus souple |
    |==================================|

    :Example:
    >>> import raisin
    >>> def foo(x, y):
    ...     return x - y
    >>> s = raisin.Scan(foo, [0, 1, 2], [1, 2])
    >>> s.start()
    >>> s.get()
    [[-1, -2], [0, -1], [1, 0]]
    >>>
    """
    def __init__(self,
                target,
                *iterables,
                force=True,
                timeout=3600*24*31,
                job_timeout=3600*48,
                save=True,
                parallelization_rate=4,
                signature=None):
        """
        :param target: Fonction qui doit etre evaluee plein de fois.
        :type target: callable
        :param iterables: Chaque iterable associes a chacuns des arguments de la fonction.
        :param force: Permet de relancer le calcul meme si il le resultat est deja enregistre.
        :type force: bool
        :param timeout: Permet de lever une exception si ca met trop de temps en tout.
        :type timeout: int
        :param job_timeout: Permet de lever une exception sur chaque evaluation trop lente. Les autres threads continuent de tourner.
        :type job_timeout: int
        :param save: Permet de decider si le resultat est enregistrer.
        :type save: bool
            True: Le resultat est enregistre si cela en vaut la peine (gain de vitesse).
            False: Le resultat n'est pas enregistre nul part (il faut tout recommencer a chaque fois, pas de reprise possible)
        :param parallelization_rate: Permet de partager le calcul affin de mieu profiter des resources de l'ordinateur.
        :type parallelization_rate: int
            0: Aucune parallelisation, tout est excecuter dans le processus courant.
            1: Pseudo parallelisation, reparti les operations dans des threads du module 'threading'.
            2: Legere parallelisation, utilise les differents coeurs de la machine avec le module 'multiprocessing'.
            3: Grosse parallelisation, utilise toutes les ressources disponible dans le reseau local LAN.
            4: Monstrueuse parallelisation, utilise toutes les ressources accessibles dans le monde entier!
        :param signature: N'importe quel objet qui permet d'afficher dans la bonne colone du terminal.
        """
        assert callable(target)
        assert type(force) is bool
        assert type(timeout) is int
        assert timeout > 0
        assert type(job_timeout) is int
        assert job_timeout > 0
        assert type(save) is bool
        assert type(parallelization_rate) is int
        assert 0 <= parallelization_rate <= 4

        raisin.Scan.__init__(self,
                    target,
                    args,
                    kwds,
                    force=force,
                    timeout=timeout,
                    job_timeout=job_timeout,
                    save=save,
                    parallelization_rate=parallelization_rate,
                    signature=signature)

def scan(target, *iterables, **kwargs):
    """
    |==========================================================|
    | Permet d'evaluer une fonction en balayant ces arguments. |
    |==========================================================|

    sortie
    ------
    :return: Un tenseur de dimension egale au nombre d'arguments len(iterables).
             Chaque valeur presente dans le tenseur et l'une des valeur de retour
             De la fonction 'target' evalue pour un couple de parametre fixe.
    :rtype: list

    exemple
    -------
    :Example:
    >>> import raisin
    >>> def foo(x, y):
    ...     return x - y
    >>> raisin.scan(f, [0, 1, 2], [1, 2])
    [[-1, -2], [0, -1], [1, 0]]
    >>>
    """
    s = Scan(target, *iterables, **kwargs)
    s.start()
    return s.get()


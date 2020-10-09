from cqc.pythonLib import qubit

def X(q, *args, **kwargs):
    """
    (q, *args, **kwargs) -> qubit
    Applies X to qubit and returns the qubit to be used for having a functional like programming, but not necessary as the qubit is modified in place.
    """
    q.X(*args, **kwargs); return q

def Y(q, *args, **kwargs):
    """
    (q, *args, **kwargs) -> qubit
    Applies Y to qubit and returns the qubit to be used for having a functional like programming, but not necessary as the qubit is modified in place.
    """
    q.Y(*args, **kwargs); return q

    def Z(q, *args, **kwargs):
    """
    (q, *args, **kwargs) -> qubit
    Applies Z to qubit and returns the qubit to be used for having a functional like programming, but not necessary as the qubit is modified in place.
    """
    q.Z(*args, **kwargs); return q

    def H(q, *args, **kwargs):
    """
    (q, *args, **kwargs) -> qubit
    Applies H (Hadamard) to qubit and returns the qubit to be used for having a functional like programming, but not necessary as the qubit is modified in place.
    """
    q.H(*args, **kwargs); return q

def K(q, *args, **kwargs):
    """
    (q, *args, **kwargs) -> qubit
    Applies K to qubit and returns the qubit to be used for having a functional like programming, but not necessary as the qubit is modified in place.
    """
    q.K(*args, **kwargs); return q

def T(q, *args, **kwargs):
    """
    (q, *args, **kwargs) -> qubit
    Applies T to qubit and returns the qubit to be used for having a functional like programming, but not necessary as the qubit is modified in place.
    """
    q.T(*args, **kwargs); return q

def Tinv(q, *args, **kwargs):
    """
    (q, *args, **kwargs) -> qubit
    Applies Inverse T gate to qubit and returns the qubit to be used for having a functional like programming, but not necessary as the qubit is modified in place.
    """
    q.rot_Z(224, *args, **kwargs); return q

def CNOT(p, q, *args, **kwargs):
    """
    (p, q, *args, **kwargs) -> p, q 
    Applies CNOT to qubit control p and qubit target q  and returns the p and q to be used for having a functional like programming, but not necessary as the qubit is modified in place.
    """
    p.cnot(q, *args, **kwargs); return p, q

def PREP(node, *args, **kwargs): return qubit(node, *args, **kwargs)
def MEAS(q, *args, **kwargs): return q.measure(*args, **kwargs)

def DISP(q): print(q, f"""QID: {q._qID}"""); return None
def QID(q): return q._qID

#def EPR(): return None
def SEND(q, target_id, node, *args, **kwargs):
    '''
    (q, target_id, node, *args, **kwargs) -> None
    Sends a qubit q to a given target node identified by target_id. Node is the local node object with which the library has been instantiated
    '''
    node.sendQubit(q, target_id, *args, **kwargs)
    return None


def RECV(node, *args, **kwargs):
    '''
    (node, *args, **kwargs) -> qubit
    Looks in the input qubit buffer of the local node for a received qubit, and retrieves it
    '''
return node.recvQubit(*args, **kwargs)

#def TELE(): return None

mapping = {
    "X": X,
    "Y": Y,
    "Z": Z,
    "H": H,
    
    "K": K,
    "T": T,
    "Tinv":Tinv,

    "CNOT": CNOT,

    "PREP": PREP,
    "MEAS": MEAS,
    "DISP": DISP,
    "QID": QID,
    
    "EPR": None,
    "SEND": SEND,
    "RECV": RECV,
    "TELE": None
    }


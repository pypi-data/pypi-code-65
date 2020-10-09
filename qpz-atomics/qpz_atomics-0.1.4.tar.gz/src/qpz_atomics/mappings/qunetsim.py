#from components.host import Host as QNSHost
from objects.qubit import Qubit as qubit

def X(q, *args, **kwargs): q.X(*args, **kwargs); return q
def Y(q, *args, **kwargs): q.Y(*args, **kwargs); return q
def Z(q, *args, **kwargs): q.Z(*args, **kwargs); return q
def H(q, *args, **kwargs): q.H(*args, **kwargs); return q

def K(q, *args, **kwargs): q.K(*args, **kwargs); return q
def T(q, *args, **kwargs): q.T(*args, **kwargs); return q

def Tinv(q, *args, **kwargs): q.rz(5.49778714378, *args, **kwargs); return q

def CNOT(p, q, *args, **kwargs): p.CNOT(q, *args, **kwargs); return p, q

def PREP(node, *args, **kwargs): return qubit(node, *args, **kwargs)
def MEAS(q, *args, **kwargs): return q.measure(*args, **kwargs)

def DISP(q): print(q, f"""QID: {q.id}"""); return None
def QID(q): return q.id

#def EPR(): return None
def SEND(q, target_id, node, *args, **kwargs): node.send_qubit(target_id, q, *args, await_ack=True, **kwargs); return None
def RECV(source_id, node, *args, **kwargs): return node.get_data_qubit(*args, host_id=source_id, wait=10, **kwargs)
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

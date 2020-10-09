# import os,sys,inspect
# current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# parent_dir = os.path.dirname(current_dir)
# sys.path.insert(0, parent_dir) 

from qpz_atomics import qpz_atomics 

###################################
## Examples using SimulaQron / CQC

def simulaqron():

    from cqc.pythonLib import CQCConnection
    from qpz_atomics.mappings.simulaqron import mapping

    with CQCConnection("Alice") as Alice:

        _ = qpz_atomics.lib(mapping, Alice)

        #use library to prepare a single qubit
        # all commands are applied locally: no need to specify the node
        q = _.PREP()

        # show info about created qubit
        _.DISP(q)

        # flip the qubit
        _.X(q)
        
        # sending to Bob (need to pass the arguments using the syntax used by the backend used)
        _.SEND(q, "Bob") 


    with CQCConnection("Bob") as Bob:
        _ = qpz_atomics.lib(mapping, Bob)

        # receive a qubit
        q = _.RECV()

        # show info about this qubit
        _.DISP(q)

###################################
## Examples using QuNetSim
## To use QuNetSim, add its path to
## PYTHONPATH
## export PYTHONPATH=$PYTHONPATH:<path_to_qunetsim>

def qunetsim():
    from components.host import Host
    from components.network import Network
    from objects.qubit import Qubit

    network = Network.get_instance()
    nodes = ["Alice", "Bob", "Eve", "Dean"]
    network.start(nodes)
    network.delay = 0.1

    host_alice = Host('Alice')
    host_alice.add_connection('Bob')
    host_alice.start()

    host_bob = Host('Bob')
    host_bob.add_connection('Alice')
    host_bob.add_connection('Eve')
    host_bob.start()

    host_eve = Host('Eve')
    host_eve.add_connection('Bob')
    host_eve.add_connection('Dean')
    host_eve.start()

    host_dean = Host('Dean')
    host_dean.add_connection('Eve')
    host_dean.start()

    network.add_host(host_alice)
    network.add_host(host_bob)
    network.add_host(host_eve)
    network.add_host(host_dean)

    from mappings.qunetsim import mapping
    
    #return host_alice, host_bob, host_eve, network

    def source_protocol(source_host, target_host_id):
        _ = qpz_atomics.lib(mapping, source_host)
        for i in range(5):
            q = _.PREP()
            q = _.H(q)
            print("sending"), _.DISP(q)            
            _.SEND(q,target_host_id)
        
    def target_protocol(target_host, source_host_id):
        _ = qpz_atomics.lib(mapping, target_host)
        for i in range(5):
            print(source_host_id)
            q = _.RECV(source_host_id)
            print("recieved"), _.DISP(q)

    host_alice.run_protocol(source_protocol, (host_bob.host_id,))
    host_bob.run_protocol(target_protocol, (host_alice.host_id,))

if __name__ == '__main__':
    simulaqron()
    #qunetsim()


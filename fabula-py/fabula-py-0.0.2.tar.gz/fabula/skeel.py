'''
Created on 30 июл. 2020 г.

@author: ladmin
'''

import os, stat, re

from abc import ABC, abstractmethod, abstractproperty
from fabric import  colors, api as fab
#from fabric import tasks as taskwrap
from fabricio.tasks import ImageBuildDockerTasks, DockerTasks, Tasks
from fabricio import docker, tasks

from srv.dockerfiles import DockerfileFactory

from fabric.tasks import Task, WrappedCallableTask, get_task_details

from fabric2 import SerialGroup as Group
from fabric2 import Connection

def fname(function_to_decorate):
    def the_wrapper_around_the_original_function():
        print("Я - код, который отработает до вызова функции")
        function_to_decorate() # Сама функция
        print("А я - код, срабатывающий после")
    return the_wrapper_around_the_original_function

class Element(ABC):
    registry=''
    _service=None
    
    dockerlogin=False
    
    @abstractmethod
    def initservice(self):
        pass
    
    def prepareDir(self):
        try:
            os.mkdir(self.layerPath)
            os.chmod(self.layerPath, stat.S_IRWXU, follow_symlinks=True)
        except OSError:
            print ("Создать директорию %s не удалось" % self.layerPath)
        else:
            print ("Успешно создана директория %s " % self.layerPath)
    
    @property
    def opt(self):
        return self.options.copy()
    @opt.setter
    def opt(self, val):
        if 'options' not in self.__dict__:
            self.options={}
        
        try:
            optname, value = val
        except ValueError:
            raise ValueError("Pass an iterable with two items")
        else:
            """ This will run only if no exception was raised """
            self.options[optname]=value
        
    def deleteOpt(self, optname):
        if 'options' not in self.__dict__:
            self.options={}
        try:
            del self.options[optname]
        except Exception as ex:
            print(ex)
            print('Value {optname} is not delete'.format(optname=optname))
    @property
    def network(self):
        return self.__net
    @network.setter
    def network(self, net):
        net.setRole(self._role)
        self.__net=net
        self.opt=('network', [self.__net.netname])
        
    @property
    def volumes(self):
        return  self.__vols
    @volumes.setter
    def volumes(self, vol):
        self.__vols={}
        self.__vols[vol.source]=vol
        self.opt=('mount', vol.generateVolString())
    
    def setService(self, service):
        self._service=service
    
    def add_git_repo(self, gitrepos):       
        self._gitrepos=gitrepos
       
    #@abstractmethod    
    def add_dockerfile(self, dockerfileObj):
        self._dockerfileObj=dockerfileObj
    #@abstractmethod    
    def applay_dockerfile(self):
        self._dockerfileObj.passFileToProject(self.layerPath)
    
    def changeRole(self, role):
        self._role=role
        for obj in vars(self).values():
            if isinstance(obj, WrappedCallableTask):
                obj.roles=role
    
    #@abstractmethod     
    def initRepoForLayer(self, branch='master'):
        self.prepareDir()
        try:
            rep=self._gitrepos.getRepo(workdir=self.layerPath, cur_branch=branch)
        except Exception as ex:
            print(ex)
        return rep
    
    def convertToService(self, tag='v1'):
        service=docker.Service(
            name=self.imageTag,
            image=self.serviceName+':'+tag,
            options=self.opt,
            )
        self.setService(service)
    
    @fab.hosts()
    @fab.roles()
    @fab.task    
    def updateFromImage(self, tag=None, force=False):
        """
        update service use prebiuild image
        """
        fab.execute(self.pull, tag=tag)
        fab.execute(self.update, tag=tag, force=force)
         
    def dockerLogin(self):
        if self.dockerlogin:
            cmd='docker login '+self.registry
            self._role.run(cmd)
              
    @fab.hosts()
    @fab.roles()
    @fab.task
    def commit_task(self, tag='v1'):
        cmd='docker commit {ID} {newServiceTag}'.format(ID=self.service.info['Id'], 
                                                        newServiceTag=self.registry+'/'+self.serviceName+':'+tag)
        fab.run(cmd)
        self.push(tag=tag)
        fab.env.host=None
        fab.env.host_string=None
        #fab.env.passwords=None
    
    @abstractmethod
    def hook(self):
        print("This is hook code")
        
    def getrole(self):
        return self._role
    
class Manager(object):
    def __init__(self):
        pass
        

class NetworkManager(Manager):
    def __init__(self, netname, role=False,  driver='bridge'):
        self.role=role
        self.netname=netname
        self.driver=driver
    def setRole(self, role):
        self.role=role
    def createNetwork(self):
        res=self.role.execute(self._createNetwork)
        return res
    
    def _createNetwork(self, connection):
        try:
            net=connection.networks.get(self.netname)
            print("Network {name} exist".format(name=net))
        except Exception as Ex:
            res=connection.networks.create(self.netname, driver=self.driver)
            res
        return False
        
    def update(self):
        print("updating network")
        self.createNetwork()

class RoleManager(list):
    def __new__(cls, role):
        cls.role=role
        cls.portIndex=23750
        return super().__new__(cls)
    #def __init__(self, role, addr):
        #self.role=role
        #self.addr=addr
    def setAddr(self, addr):
        self.addr=addr    
    
    def execute(self, callFunc):
        
        import paramiko
        from docker import DockerClient
        from sshtunnel import SSHTunnelForwarder
        import time

        for host in self.adress:
            user=host.split('@', 1)[0]
            addr=host.split('@', 1)[1]
            port=self.localConnectionPort
            forward=SSHTunnelForwarder((addr, 22), 
                                ssh_username=user, 
                                ssh_pkey="/var/ssh/rsa_key", 
                                ssh_private_key_password="secret", 
                                remote_bind_address=(addr, 2375), 
                                local_bind_address=('127.0.0.1', port))
            forward.start()
            time.sleep(3)
            dockerConection=DockerClient('tcp://127.0.0.1:{port}'.format(port=port))
            res=callFunc(dockerConection)
            dockerConection.close()
            del dockerConection
            forward.stop()
        return res
    
    @property
    def localConnectionPort(self):
        port=self.portIndex
        self.portIndex+=1
        return port
    
    def getConnections(self):
        dockerConections={}
        for host in self.adress:
            dockerConections[host]=self.openDockerConnection(host=host)
        return dockerConections
    @property
    def adress(self):
        return self.addr
    @adress.setter
    def adress(self, addr):
        self.addr=addr
        
    @property
    def roles(self):
        return self.role
    @roles.setter
    def roles(self, rolename):
        self.role=rolename
        #self.updateGlobalRoles(rolename)
    #@role.deleter
    #def roles(self, rolename):
    #    del self.role_list.remove(rolename)    
    def run(self, arg):
        for host in self.adress:
            result = Connection(host).run(arg, pty=True)
            print("{}: {}".format(host, result.stdout.strip()))
    
    
    
class VolumeManager(Manager):
    def __init__(self, role, typeVol='volume', driver='local', source='defvol', options='readonly=false'):
        self.role=role
        self.driver=driver
        self.source=source
        self.typeVol=typeVol
        self.options=options
        self.template='type={type},source={source},destination={destination},{options}'
    def setDestination(self, destination):
        self.destination=destination
    def setSource(self, source):
        self.source=source
    def setType(self, typeVol):
        self.typeVol=typeVol
    def setAditionalOpt(self, options):
        self.options=options
    
    def update(self):
        res=self.role.execute(self._create)
        return res
    
    def _create(self, connection):
        try:
            vol=connection.volumes.get(self.source)
            print("Volume {name} exist".format(name=vol))
        except Exception as Ex:
            res=connection.volumes.create(self.source, driver=self.driver)
            res
        return False
    
    def generateVolString(self):
        opt=self.template.format(type=self.typeVol, source=self.source, destination=self.destination, options=self.options)
        return [opt]
        


class BlackBox(ABC):
    '''
    classdocs
    '''
    stack={}
    __index=0
    
    projectName=None
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    #@abstractmethod    
    #def build_layer(self) -> None:
    #    pass
    
    @property
    def layer(self):
        return self.list
    
    @layer.setter
    def layer(self, strategy):
        
        self.stack[strategy._element.imageTag]=strategy
        self._increment()
        
    def _increment(self):
        self.__index+=10
    
    @fab.hosts()
    @fab.roles()
    @fab.task    
    def compile_layers(self):
        for item in self.stack.keys():
            self.stack[item].fullcycle()
    @fab.hosts()
    @fab.roles()
    @fab.task    
    def initAllRepo(self):
        for item in self.stack.keys():
            self.stack[item]._element.runrepo()
    
    @fab.hosts()
    @fab.roles()
    @fab.task    
    def push_layers(self):
        print('==== PUSH ====')



    

class LayerBuilder(ImageBuildDockerTasks, Tasks, Element):
    
    def __init__(self,
                net='network',
                role=['defrole'], 
                dockerlogin=False, registry='',
                projectname='testproj', 
                imageTag='unitname' , 
                release='latest'):
          
        self.dockerlogin=dockerlogin
        self.myname=projectname
        self.registry=registry
        self.imageTag=imageTag
        self.serviceName=projectname+'/'+imageTag
        self.serviceTag=projectname+'/'+imageTag+':'+release
        self.layerPath=os.path.join(os.getcwd(), 'build/'+self.serviceName)
        self._role=role
        self.network=net
        self.destroy = self.DestroyTask(tasks=self)
        
        
    def initservice(self):
        super(LayerBuilder, self).__init__(self._service,
                                      build_path='build/'+self.serviceName,
                                      roles=self._role,
                                      registry=self.registry,
                                      destroy_command=True)
        self.dockerLogin()
    
        
    def commit(self, tag='v1'):
        fab.execute(self.commit_task, tag)

    def hook(self):
        print('rewritd hook')
        
    #@fab.hosts()
    #@fab.roles()
    #@fab.task
    #def deploy(self, tag=None, force=False, backup=False, migrate=True):
    #    """
    #    deploy service (prepare -> push -> backup -> pull -> migrate -> update)
    #    """
    #    self.prepare(tag=tag)
    #    self.push(tag=tag)
    #    self.registry
    #    fab.execute(
    #        self.migrate,
    #        tag=tag,
    #        #force=False,
    #        #backup=False,
    #        #migrate=True,
    #    )
        

class LayerConstructor(DockerTasks, Element):

    def __init__(self,
                net='network',
                role=['defrole'], 
                dockerlogin=False, registry='',
                projectname='testproj', 
                imageTag='unitname' , 
                release='latest'):
        self.dockerlogin=dockerlogin
        self.myname=projectname
        self.registry=registry
        self.imageTag=imageTag
        self.serviceName=projectname+'/'+imageTag
        self.serviceTag=imageTag+':'+release
        self.layerPath=os.path.join(os.getcwd(), self.serviceName)
        self._role=role
        self.network=net
        self.destroy = self.DestroyTask(tasks=self)
    
        
    def initservice(self):
        super(LayerConstructor, self).__init__(self._service,
                                               roles=self._role,
                                               registry=self.registry)
        self.dockerLogin()
             
    def hook(self):
        print('rewritd hook')


class LayerFactorySkeel(ABC):
    dockerFactory=DockerfileFactory()
    
    def __init__(self) -> None:
        self._element = None
        self.__index=0
         
    def reset(self):
        self._element=None
    def __increment(self):
        self.__index+=1
    
    @property
    def builder(self) -> Element:
        return self._element

    @builder.setter
    def builder(self, element: Element) -> None:
        """
        Директор работает с любым экземпляром строителя, который передаётся ему
        клиентским кодом. Таким образом, клиентский код может изменить конечный
        тип вновь собираемого продукта.
        """
        self._element = element

    


   

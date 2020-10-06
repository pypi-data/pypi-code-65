import re
from .object import Object
from .pin import Pin
from .net import Net
from .bus import Bus
from .param import Param
from .input import Input
from .output import Output
from .inout import Inout
from copy import copy, deepcopy

class Component(Object):
    __global_components = {}

    def all_components():
        return Component.__global_components

    def get_component_by_name(comp_name):
        return Component.__global_components[comp_name]

    def delete_all_components():
        #TODO run on dictionary and call destructor of all components first
        Component.__global_components = {}

    def __init__(self, name, original=None):
        super(Component, self).__init__(name)

        if name in Component.__global_components:
            raise Exception('component already defined')
        else:
            Component.__global_components[name] = self

        self.__pins = {} #noytzach - performance
        self.__nets = {} #noytzach - performance
        self.__netbusses = {} #noytzach - performance
        self.__pinbusses = {} #noytzach - performance
        self.__subcomponents = {}
        self.__net_connectivity = {}
        self.__pin_connectivity = {}
        self.__virtual_pins = {}
        self.__params = []
        self.__pins_ordered = []
        self.add_pin_adds_net = True
        self.__dont_uniq = False
        self.__dont_write_verilog = False
        self.__is_physical = False
        self.__is_sequential = False
        self.__verilog_code = None

        if original is not None:
            self.add_pin_adds_net = original.add_pin_adds_net
            self.set_dont_uniq(original.get_dont_uniq())
            self.set_dont_write_verilog(original.get_dont_write_verilog())
            self.set_is_physical(original.get_is_physical())
            self.set_is_sequential(original.get_is_sequential())
            v_code = original.get_verilog_code()
            self.__verilog_code = v_code.copy() if v_code else None
            for pin_str in original.pin_names():
                pin = original.get_pin(pin_str)
                if pin.is_part_of_bus():
                    if pin_str not in self.pin_names():
                        self.add_pinbus(Bus(pin.bus().verilog_type(),pin.bus().get_name(),pin.bus().get_width()))
                elif pin.verilog_type() == "input":
                    self.add_pin(Input(pin_str))
                elif pin.verilog_type() == "output":
                    self.add_pin(Output(pin_str))
                else:
                    self.add_pin(Inout(pin_str))
            for net_str in original.net_names():
                if net_str not in self.net_names():
                    net = original.get_net(net_str)
                    if original.get_net(net_str).is_part_of_bus():
                        self.add_netbus(Bus(Net,net.bus().get_name(),net.bus().get_width()))
                    else:
                        self.add_net(Net(net_str))
            for sub_str in original.component_names():
                sub = original.get_subcomponents_dict()[sub_str]
                self.add_component(sub,sub_str)

            for net_str in original.net_names():
                my_net = self.get_net(net_str)
                original_net = original.get_net(net_str)
                if my_net not in self.__net_connectivity:
                    self.__net_connectivity[my_net] = []
                # for every net, check all the pins that connected to it in self and see if they exist
                # in connectivity in original, if not - disconnect it in self.
                for pin_str in [pin.get_object_name() for pin in self.__net_connectivity[my_net]]:
                    if pin_str not in [pin.get_object_name() for pin in original.get_net_connectivity(original_net)]:
                        self.disconnect(pin_str)
                # for every net, check all the pins that connected to it in original and see if they exist
                # in connectivity in self, if not - connect it in self.
                for pin_str in [pin.get_object_name() for pin in original.get_net_connectivity(original_net)]:
                    if pin_str not in [pin.get_object_name() for pin in self.__net_connectivity[my_net]]:
                        self.connect(net_str, pin_str)
            for param in original.get_params():
                self.add_param(deepcopy(param))

    def get_pins(self):
        return self.__pins.values()

    def get_pinbusses(self):
        return self.__pinbusses.values()

    def get_pins_ordered(self):
        return self.__pins_ordered

    def get_pin(self, pin_name):
        return self.__pins[pin_name]

    def get_pinbus(self, pinbus_name):
        return self.__pinbusses[pinbus_name]

    def pin_names(self):
        return self.__pins.keys() #noytzach - performance
        #return [x.get_object_name() for x in self.get_pins()]

    def pinbus_names(self):
        return self.__pinbusses.keys()

    def add_pin(self, pin):
        if not isinstance(pin, Pin):
            raise Exception('not a pin')
        pin_name = pin.get_object_name()
        if pin_name in self.pin_names():
            raise Exception('pin "'+pin_name+'" already exists in component')
        if pin_name in self.pinbus_names():
            raise Exception('pin "'+pin_name+'" already exists as pinbus in component')

        pin.associate(self)
        self.__pins[pin_name] = pin

        if self.add_pin_adds_net and not pin.is_part_of_bus():
            # add net with the same name as the pin
            n = pin_name
            self.add_net(Net(n))
            self.connect(n, n)

        self.__pins_ordered.append(pin)

    def add_pinbus(self, pinbus):
        if not isinstance(pinbus, Bus):
            raise Exception('not a bus')
        pinbus_name = pinbus.get_name()
        if pinbus_name in self.pinbus_names():
            raise Exception('pinbus "'+pinbus_name+'" already exists in component')
        if pinbus_name in self.pin_names():
            raise Exception('pinbus "'+pinbus_name+'" already exists as pin in component')

        # temporarily disable add_pin_adds_net feature so that pinbus is connected to
        # netbus (later, and not to nets that are not part of bus)
        temp = self.add_pin_adds_net
        self.add_pin_adds_net = False
        for p in pinbus.all_bits():
            self.add_pin(p)
        self.add_pin_adds_net = temp
        
        pinbus.associate(self)
        self.__pinbusses[pinbus_name] = pinbus

        if self.add_pin_adds_net:
            # add netbus with the same name as the pinbus
            n = pinbus_name
            self.add_netbus(Bus(Net, n, pinbus.width(), signed=pinbus.is_signed()))
            self.connect_bus(n, n)

    def get_params(self, str = 0):
        if str:
            return (x.get_string() for x in self.__params)
        else:
            return (x for x in self.__params)

    def add_param(self, param):
        if not isinstance(param, Param):
            raise Exception('not a param')
        if any(x.get_object_name() == param.get_object_name() for x in self.get_params()):
           raise Exception(param.get_object_name() + ' is allready exist')
        self.__params.append(param)

    def set_param(self, param_name, value):
        filtered_list = list(x for x in self.get_params() if x.get_object_name()==param_name)
        if len(filtered_list) == 0:
            raise Exception('param ' + param_name + ' does not exist')
        filtered_list[0].set_value(value)

    def get_nets(self):
        return self.__nets.values()

    def get_net(self, net_name):
        return self.__nets[net_name]

    def get_netbus(self, netbus_name):
        return self.__netbusses[netbus_name]

    def net_names(self):
        return self.__nets.keys() #noytzach - performance
        #return [x.get_object_name() for x in self.get_nets()]

    def get_net_connectivity(self, net):
        return self.__net_connectivity[net]

    def netbus_names(self):
        return self.__netbusses.keys()

    def add_net(self, net):
        if not isinstance(net, Net):
            raise Exception('not a net')
        net_name = net.get_object_name()
        if net_name in self.net_names():
            raise Exception('net "'+net_name+'" already exists in component')
        if net_name in self.netbus_names():
            raise Exception('net "'+net_name+'" already exists as netbus in component')

        net.associate(self)
        self.__nets[net_name] = net #noytzach - performance

    def add_netbus(self, netbus):
        if not isinstance(netbus, Bus):
            raise Exception('not a bus')
        netbus_name = netbus.get_name()
        if netbus_name in self.netbus_names():
            raise Exception('netbus "'+netbus_name+'" already exists in component')
        if netbus_name in self.net_names():
            raise Exception('netbus "'+netbus_name+'" already exists as net in component')

        for n in netbus.all_bits():
            self.add_net(n)

        netbus.associate(self)
        self.__netbusses[netbus_name] = netbus

    def get_subcomponents(self):
        return (x for x in self.__subcomponents)

    def get_subcomponents_recursive(self, inclusive=False):
        s = set()
        for c in self.get_subcomponents():
            dev = self.__subcomponents[c]
            s.update(dev.get_subcomponents_recursive())
            s.add(dev)

        if inclusive:
            s.add(self)
        return s

    def get_subcomponents_dict(self):
        return self.__subcomponents

    def component_names(self):
        return [x for x in self.get_subcomponents()]

    def add_component(self, component, instance_name):
        self.add_subcomponent(component, instance_name)

    def add_subcomponent(self, component, instance_name):
        if not isinstance(component, Component):
            raise Exception('not a component')

        if instance_name in self.__subcomponents:
            raise Exception('component ['+instance_name+'] already exists')
        else:
            self.__subcomponents[instance_name] = component

    def connect(self, net_str, pin_str):
        if not isinstance(net_str, str):
            raise Exception('net_str should be a string')
        if not isinstance(pin_str, str):
            raise Exception('pin_str should be a string')

        try:
            net = self.get_net(net_str)
        except:  # todo: add type
            raise Exception('cannot find net [' + net_str + '] in component')

        str2pin_dict = self.__str2pin(pin_str, is_bus=False)

        # Errors
        if str2pin_dict['is_virtual']:
            raise Exception('[' + str2pin_dict['subcomponent_str'] + '.' +
                            str2pin_dict['subcomponent_pin_str'] + '] already connected')

        # connect
        pin = str2pin_dict['pin']
        if pin in self.__pin_connectivity:
            raise Exception('pin already connected')

        if net not in self.__net_connectivity:
            self.__net_connectivity[net] = []

        self.__net_connectivity[net].append(pin)
        self.__pin_connectivity[pin] = net

    def disconnect(self, pin_str):
        if not isinstance(pin_str, str):
            raise Exception('pin_str should be a string')

        str2pin_dict = self.__str2pin(pin_str, is_bus=False)

        # Errors
        if not str2pin_dict['is_pin_of_subcomponent']:
            raise Exception('cannot disconnect primary pin [' + pin_str + '] from net!')
        if not str2pin_dict['is_virtual']:
            raise Exception('[' + str2pin_dict['subcomponent_str'] + '.' +
                            str2pin_dict['subcomponent_pin_str'] + '] not found as connected')

        # disconnect
        pin = str2pin_dict['pin']
        if pin not in self.__pin_connectivity:
            raise Exception('pin not connected')
        net = self.__pin_connectivity[pin]

        self.__net_connectivity[net].remove(pin)
        del self.__pin_connectivity[pin]

    def disconnect_bus(self, pinbus_str):
        if not isinstance(pinbus_str, str):
            raise Exception('pinbus_str should be a string')

        # if len(lpin)==1:  # pin of component
        #     pass # TODO: need to implement this branch

        try:
            str2pin_dict = self.__str2pin(pinbus_str, is_bus=True)
        except Exception as e:  # if the error is because netbus - ignore
            if e.args[0] != 'cannot find netbus [' + pinbus_str + '] in component':
                raise

        # disconnect bus
        pinbus = str2pin_dict['pinbus']
        inst = str2pin_dict['subcomponent_str'] if str2pin_dict['is_pin_of_subcomponent'] else pinbus_str
        for p in pinbus.all_bits():
            self.disconnect(inst + '.' + p.get_object_name())

    def connect_bus(self, netbus_str, pinbus_str):
        if not isinstance(netbus_str, str):
            raise Exception('netbus_str should be a string')
        if not isinstance(pinbus_str, str):
            raise Exception('pinbus_str should be a string')

        try:
            netbus = self.get_netbus(netbus_str) #next(n.bus() for n in self.get_nets() if n.is_part_of_bus() and n.bus().get_name()==netbus_str)
        except:  # todo: add type
            raise Exception('cannot find netbus [' + netbus_str + '] in component')

        str2pin_dict = self.__str2pin(pinbus_str, is_bus=True)

        # connect bus
        pinbus = str2pin_dict['pinbus']
        netbus = str2pin_dict['netbus'] if not str2pin_dict['is_pin_of_subcomponent'] else netbus

        if netbus.width() == pinbus.width():
            for n, p in zip(netbus.all_bits(), pinbus.all_bits()):
                if not str2pin_dict['is_pin_of_subcomponent']:
                    self.connect(n.get_object_name(), p.get_object_name())
                else:
                    self.connect(n.get_object_name(), str2pin_dict['subcomponent_str'] + '.' + p.get_object_name())
        else:
            raise Exception('bus widths does not match')

    def count_instances(self):
        # first count the module itself
        count = {self.get_object_name():1}

        #then add the sub-counts from submodules
        for inst in self.get_subcomponents():
            dev = self.__subcomponents[inst]
            sub_count = dev.count_instances()

            for m in sub_count:
                if m in count:
                    count[m] += sub_count[m]
                else:
                    count[m] = sub_count[m]
                    
        return count

    def copy(self, copy_name):
        if copy_name in Component.__global_components:
            raise Exception('component ['+copy_name+'] already exists')

        new_dev = copy(self)
        new_dev.set_object_name(copy_name)
        Component.__global_components[copy_name] = new_dev

        return new_dev

    def deepcopy(self, copy_name):
        if copy_name in Component.__global_components:
            raise Exception('component ['+copy_name+'] already exists')

        new_dev = deepcopy(self)
        new_dev.set_object_name(copy_name)
        Component.__global_components[copy_name] = new_dev

        return new_dev
        

    def set_dont_uniq(self, val):
        self.__dont_uniq = val

    def get_dont_uniq(self):
        return self.__dont_uniq

    def set_dont_write_verilog(self, val):
        self.__dont_write_verilog = val

    def get_dont_write_verilog(self):
        return self.__dont_write_verilog

    def set_is_physical(self, val):
        self.__is_physical = val

    def get_is_physical(self):
        return self.__is_physical

    def set_is_sequential(self, val):
        self.__is_sequential = val

    def get_is_sequential(self):
        return self.__is_sequential

    def uniq(self, count = None, numbering = None):
        #topmost component counts, all others should get count from above
        if not count:
            count = self.count_instances()

        #same as count, the one that counts should setup the numbering
        if not numbering:
            numbering = {}
            for k in count:
                numbering[k] = 0
                #make sure k_# not already used
                while k+"_"+str(numbering[k]) in Component.__global_components:
                    numbering[k] +=1

        # sort subcomponents names as ABC,123,ABC,123 (without ',')
        my_fun = lambda k,v,q=0, p=0: [k, int(v), q, int(p)]
        key = lambda t: my_fun(*re.match(r'([^\d]+)(\d+)([^\d]+)(\d+)', t + '0_0').groups())
        sorted_ = sorted(self.get_subcomponents(), key=key)

        for inst in sorted_:
            dev = self.__subcomponents[inst]
            devname = dev.get_object_name()
                        
            if count[devname]>1 and not dev.get_dont_uniq():
                new_devname = devname+"_"+str(numbering[devname])
                new_dev = dev.deepcopy(new_devname)
                self.__subcomponents.update({inst: new_dev})

                #the new devname is missing from count dictionary
                count[new_devname] = 1

                #increment numbering to next available number
                while True:
                    numbering[devname] += 1
                    next_devname_uniq = devname+"_"+str(numbering[devname])
                    if next_devname_uniq not in Component.__global_components:
                        break
                    
                dev = new_dev

            dev.uniq(count, numbering)

    def verilog_port_list(self):
        return [x for x in [pl.verilog_port_list() for pl in self.get_pins()] if x is not None]

    def write_verilog(self):
        v = []
        mod_def = '\nmodule ' + self.get_object_name() + ' ('
        ports = ', '.join(sorted(self.verilog_port_list()))
        mod_def += ports + ');'
        for ll in Component.line_wrap(mod_def):
            v.append('\n' + ll)

        if self.get_pins():
            v.append('')
            v.append('\t//ports')

        for pin in sorted(self.get_pins()):
            pin_dec = pin.verilog_declare()
            if (pin_dec):
                v.append('\t' + pin_dec)
        

        if self.get_nets():
            v.append('')
            v.append('\t//wires')
        
        for net in sorted(self.get_nets()):
            net_dec = net.verilog_declare()
            if (net_dec):
                v.append('\t' + net_dec)


        if next(self.get_subcomponents(), None) is not None:
            v.append('')
            v.append('\t//instances')

            # sort subcomponents names as ABC,123,ABC,123 (without ',')
            my_fun = lambda k,v,q=0, p=0: [k, int(v), q, int(p)]
            key = lambda t: my_fun(*re.match(r'([^\d]+)(\d+)([^\d]+)(\d+)', t + '0_0').groups())
            sorted_ = sorted(self.get_subcomponents(), key=key)

            for inst in sorted_:
                dev = self.__subcomponents[inst]
                l = '\t' + dev.get_object_name() + ' ' + inst + '('
                ports = []
                for inst_pin in [p for p in dev.get_pins() if not p.is_part_of_bus()]:
                    inst_pin_name = inst_pin.get_object_name()
                    if (inst, inst_pin_name) in self.__virtual_pins:
                        vpin = self.__virtual_pins[(inst, inst_pin_name)]
                        net = self.__pin_connectivity[vpin]
                        net_name = net.get_object_name()
                    else:
                        net_name = ''
                    ports.append('.' + inst_pin_name + '(' + net_name + ')')

                for inst_bus in set([p.bus() for p in dev.get_pins() if p.is_part_of_bus()]):
                    inst_bus_name = inst_bus.get_name()
                    concat = []
                    for inst_pin in inst_bus.all_bits():
                        inst_pin_name = inst_pin.get_object_name()
                        if (inst, inst_pin_name) in self.__virtual_pins:
                            vpin = self.__virtual_pins[(inst, inst_pin_name)]
                            net = self.__pin_connectivity[vpin]
                            concat.append(net.get_object_name())
                        else:
                            concat.append("1'bx")
                    concat = Component.minimize_concat(concat)
                    ports.append('.' + inst_bus_name + '({' + ', '.join(concat) + '})')


                l += (', '.join(sorted(ports)))
                l += ');'
                for ll in Component.line_wrap(l):
                    v.append(ll)

        if self.__verilog_code:
            v.append('\t//verilog code')
            v.extend(self.__verilog_code)

        v.append('')
        v.append('endmodule')
        return v

    def pin_order(self, x):
        return x

    def write_netlist(self):
        nl = []

        #subcircuits
        for sub in self.get_subcomponents_recursive():  # inclusive=True
            nl.append('\n// Cell name: ' + sub.get_object_name() + '\n// View name: schematic')

            subckt_def = 'subckt ' + sub.get_object_name() + ' '
            pins = [p.get_object_name() for p in sub.get_pins_ordered()]
            ports = ' '.join(pins)
            subckt_def += ports 
            nl.append(subckt_def)
    
            #instances
            for inst in sorted(sub.get_subcomponents()):
                dev = sub.__subcomponents[inst]
                l = '\t' + inst + ' ('
                ports = []
                for inst_pin in [p for p in dev.get_pins() if not p.is_part_of_bus()]:
                    inst_pin_name = inst_pin.get_object_name()
                    if (inst, inst_pin_name) in sub.__virtual_pins:
                        vpin = sub.__virtual_pins[(inst, inst_pin_name)]
                        net = sub.__pin_connectivity[vpin]
                        net_name = net.get_object_name()
                    else:
                        net_name = ''
                    ports.append(net_name)
    
    
                l += (' '.join(ports))
                l += ') ' + dev.get_object_name()
                param = dev.get_params(1)
                l += ' ' + (' '.join(param))
                for ll in Component.line_wrap(l, endl=' \\'):
                    nl.append(ll)
           
            nl.append('ends ' + sub.get_object_name())
            nl.append('// End of subcircuit definition')

    #main
        nl.append('\n// Cell name: ' + self.get_object_name() + '\n// View name: schematic')

        my_fun = lambda k, v: [k, int(v)]
        key = lambda t: my_fun(*re.match(r'([a-zA-Z_]+)(\d+)', t).groups())
        sorted_ = sorted(self.get_subcomponents(), key=key)

        for inst in sorted_:
            dev = self.__subcomponents[inst]
            l = inst + ' ('
            ports = []
            for inst_pin in [p for p in dev.get_pins_ordered() if not p.is_part_of_bus()]:
                inst_pin_name = inst_pin.get_object_name()
                if (inst, inst_pin_name) in self.__virtual_pins:
                    vpin = self.__virtual_pins[(inst, inst_pin_name)]
                    net = self.__pin_connectivity[vpin]
                    net_name = net.get_object_name()
                else:
                    net_name = ''
                ports.append(net_name)


            l += (' '.join(ports))
            l += ') ' + dev.get_object_name()
            param = dev.get_params(1)
            l += ' ' + (' '.join(param))
            for ll in Component.line_wrap(l, endl=' \\'):
                nl.append(ll)

        return nl

    def line_wrap(line, line_width = 150, endl=''):
        """splits a long string to multiple strings (lines), returns a list of strings
        line_width is the MINIMUM number of charechters for line to be split,
        i.e. the line break is added at the first blank charachter AFTER line_width charachters
        endl is added at the line-break - needed for tools that require some escape sequence for multi line command (e.g. \ in tcl)
        """
        lines = []
        i = 0
        curr = ''
        for c in line:
            i = i + 1
            if i>line_width and c.isspace():
                lines.append(curr + endl)
                curr ='\t'
                i = 4
            else:
                curr += c

        if i>0:
            lines.append(curr)

        return lines

    def __str2pin(self, pin_str, is_bus):
        # method that gets pin_str and return it as a Pin

        if not isinstance(pin_str, str):
            raise Exception('pin_str should be a string')

        str2pin_dict = {}
        lpin = pin_str.split('.')  # like nand.A
        if len(lpin) == 1:  # pin of component
            str2pin_dict['is_pin_of_subcomponent'] = False
            str2pin_dict['is_virtual'] = False

            if not is_bus:  # for connect & disconnect method
                try:
                    str2pin_dict['pin'] = self.get_pin(pin_str)
                except:  # todo: add type
                    raise Exception('cannot find pin [' + pin_str + '] in component')

            else:  # for connect_bus & disconnect_bus method
                try:
                    str2pin_dict['pinbus'] = self.get_pinbus(pin_str)
                except:
                    raise Exception('cannot find pinbus [' + pin_str + '] in component')
                try:
                    str2pin_dict['netbus'] = self.get_netbus(pin_str)
                except:
                    raise Exception('cannot find netbus [' + pin_str + '] in component')

        elif len(lpin) == 2:  # pin of sub-component
            inst, inst_pin = lpin  # lpin[0]=instance name, lpin[1]=pin name
            str2pin_dict['is_pin_of_subcomponent'] = True
            str2pin_dict['subcomponent_str'] = inst
            str2pin_dict['subcomponent_pin_str'] = inst_pin
            try:
                sub = self.__subcomponents[inst]
            except:  # todo: add type
                raise Exception('sub-component [' + inst + '] not found')

            if not is_bus:  # connect & disconnect method
                try:
                    str2pin_dict['pin'] = sub.get_pin(inst_pin)
                except:  # todo: add type
                    raise Exception('pin [' + inst_pin + '] not found in sub-component [' + inst + ']')

                # Virtual pin ("pointer" to the actual pin(that inside sub-component))
                if (inst, inst_pin) not in self.__virtual_pins:  # for connect method
                    str2pin_dict['is_virtual'] = False
                    virtual_pin = Pin(inst + '.' + inst_pin)
                    self.__virtual_pins[(inst, inst_pin)] = virtual_pin
                    self.__virtual_pins[virtual_pin] = str2pin_dict['pin']
                    str2pin_dict['pin'] = virtual_pin

                else:  # for disconnect method
                    str2pin_dict['is_virtual'] = True
                    virtual_pin = self.__virtual_pins[(inst, inst_pin)]
                    del self.__virtual_pins[(inst, inst_pin)]
                    del self.__virtual_pins[virtual_pin]
                    str2pin_dict['pin'] = virtual_pin

            else:  # for connect_bus & disconnect_bus method
                try:
                    str2pin_dict['pinbus'] = sub.get_pinbus(inst_pin)
                except:
                    raise Exception('pinbus [' + inst_pin + '] not found in sub-component [' + inst + ']')

        else:  # too deep
            raise Exception(pin_str + ' is too deep')

        return str2pin_dict

    @staticmethod
    def minimize_concat(concat):
        # function that try to recognize series of bus signals as separate
        # and concat them into bus format writing

        minimized = True
        bit_re = re.compile(r"([0-9]*)'b([01xz]*),([0-9]*)'b([01xz]*)")
        net_re = re.compile(r"(.*)\[([0-9]*:)?([0-9]*)\]\1\[([0-9]*)\]")
        while minimized:
            minimized = False
            for i in range(len(concat)-1):
                m = re.match(bit_re, concat[i] + ',' + concat[i + 1])
                if m:
                    concat[i] = str(int(m.group(1)) + int(m.group(3))) + "'b" + m.group(2) + m.group(4)
                    del concat[i + 1]
                    minimized = True
                    break
                
                m = re.match(net_re, concat[i] + concat[i + 1])
                if m and (int(m.group(3))==(int(m.group(4))+1)):
                    if (m.group(2)):
                        concat[i] = m.group(1) + '[' + m.group(2) + m.group(4) + ']'
                    else:
                        concat[i] = m.group(1) + '[' + m.group(3) + ':' + m.group(4) + ']'
                    del concat[i + 1]
                    minimized = True
                    break

        return concat

    def all_connected(self, net_str):
        connected = []
        if not isinstance(net_str, str):
            raise Exception('net_str should be a string')

        lnet = net_str.replace('.','/').split('/',1)
        if len(lnet)==1:  # net of component
            try:
                net = self.get_net(net_str)
            except:  # todo: add type
                raise Exception('cannot find net [' + net_str + '] in component [' + self.get_object_name() + ']')
            pin_list = self.__net_connectivity[net]
            i = 0
            while i < len(pin_list):
                pin_str = pin_list[i].get_object_name()
                i+=1
                lpin = pin_str.split('.')
                if len(lpin)==1:  # pin of component
                    connected.append(pin_str)
                elif len(lpin)==2:  # pin of sub-component 
                    inst, inst_pin = lpin # lpin[0]=instance name, lpin[1]=pin name
                    sub = self.__subcomponents[inst]
                    if sub.__is_physical:
                        connected.append(pin_str)
                    else:
                        newconnections = sub.all_connected(sub.__pin_connectivity[sub.get_pin(inst_pin)].get_object_name())
                        for p in newconnections:
                            if len(p.split('.'))==1:
                                pin_list.extend([x for x in self.__net_connectivity[self.__pin_connectivity[self.__virtual_pins[(inst,p)]]] if x not in pin_list])
                            else:
                                connected.append(inst + '/' + p)
        else:  # net of a nested subcomponent
            inst, inst_net = lnet # lnet[0]=instance name, lnet[1]=net name
            try:
                sub = self.__subcomponents[inst]
            except:  # todo: add type
                raise Exception('cannot find subcomponent [' + inst + '] in component [' + self.get_object_name() + ']')
            for pin_str in sub.all_connected(inst_net):
                newconnections = [inst+'/'+pin_str]
                if len(pin_str.split('.'))==1:
                    newconnections = self.all_connected(self.__pin_connectivity[self.__virtual_pins[(inst,pin_str)]].get_object_name())
                connected.extend(x for x in newconnections if x not in connected)
        return connected

    '''
0 - full path +dupes
1 - full path 1 per endpoint
2 - internal pins +dupes
3 - internal pins -dupes
4 - endpoints +dupes
5 - endpoints -dupes
    '''

    def all_fan_in(self, net_str, output_type=0, visited=set()):
        fan_in = []
        drive_pins = 0
        for pin_str in self.all_connected(net_str):
            lpin = pin_str.split('.')
            if len(lpin)==1:  # pin of component
                if self.get_pin(pin_str).verilog_type() == "input":
                    fan_in.append(pin_str)
                    drive_pins+=1
            elif len(lpin)==2:  # pin of sub-component 
                inst_str, inst_pin = lpin # lpin[0]=instance name, lpin[1]=pin name
                linst = inst_str.split('/')
                sub = self
                for inst in linst:
                    sub = sub.__subcomponents[inst]
                pin = sub.get_pin(inst_pin)
                if pin.verilog_type() == "output":
                    if sub.__is_sequential:
                        fan_in.append(pin_str)
                        drive_pins+=1
                    else:
                        for inp in [p for p in sub.get_pins() if p.verilog_type() == "input"]:
                            if pin_str not in visited:
                                fan_in.extend(x+'>'+pin_str for x in
                                              self.all_fan_in(inst_str+'.' +
                                                              sub.__pin_connectivity[inp].get_object_name()
                                                              , visited=visited.union({pin_str})))
            if drive_pins > 1:
                print("WARNING: There are "+str(drive_pins)+" pins driving net "+net_str)
        if output_type==0:
            return fan_in
        elif output_type==1:
            temp = {}
            for p in fan_in:
                temp[p.partition('>')[0]] = p
            return list(temp.values())
        elif output_type==2:
            return [pin for path in [p.split('>') for p in fan_in] for pin in path]
        elif output_type==3:
            return list(set(pin for path in [p.split('>') for p in fan_in] for pin in path))
        elif output_type==4:
            return [p.partition('>')[0] for p in fan_in]
        elif output_type==5:
            return list(set(p.partition('>')[0] for p in fan_in))

    def all_fan_out(self, net_str, output_type=0, visited=set()):
        fan_out = []
        for pin_str in self.all_connected(net_str):
            lpin = pin_str.split('.')
            if len(lpin)==1:  # pin of component
                if self.get_pin(pin_str).verilog_type() == "output":
                    fan_out.append(pin_str)
            elif len(lpin)==2:  # pin of sub-component 
                inst_str, inst_pin = lpin # lpin[0]=instance name, lpin[1]=pin name
                linst = inst_str.split('/')
                sub = self
                for inst in linst:
                    sub = sub.__subcomponents[inst]
                pin = sub.get_pin(inst_pin)
                if pin.verilog_type() == "input":
                    if sub.__is_sequential:
                        fan_out.append(pin_str)
                    else:
                        for outp in [p for p in sub.get_pins() if p.verilog_type() == "output"]:
                            if pin_str not in visited:
                                fan_out.extend(pin_str+'>'+x for x in
                                               self.all_fan_out(inst_str+'.' +
                                                                sub.__pin_connectivity[outp].get_object_name()
                                                                , visited=visited.union({pin_str})))
        if output_type==0:
            return fan_out
        elif output_type==1:
            temp = {}
            for p in fan_out:
                temp[p.rpartition('>')[-1]] = p
            return list(temp.values())
        elif output_type==2:
            return [pin for path in [p.split('>') for p in fan_out] for pin in path]
        elif output_type==3:
            return list(set(pin for path in [p.split('>') for p in fan_out] for pin in path))
        elif output_type==4:
            return [p.rpartition('>')[-1] for p in fan_out]
        elif output_type==5:
            return list(set(p.rpartition('>')[-1] for p in fan_out))

    def add_verilog_code(self, code):
        if self.__verilog_code:
            self.__verilog_code.append(code)
        else:
            self.__verilog_code = [code]

    def get_verilog_code(self):
        return self.__verilog_code

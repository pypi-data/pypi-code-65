from typing import Iterable

class NmapXml:

    def __repr__(self):
        return repr(self.__dict__)


class NmapRun(NmapXml):
    """Main class of the output, which represents all the scan

    Attributes:
        scanner (str):
        args (str):
        start (str):
        startstr (str):
        version (str):
        profile_name (str):
        xmloutputversion (str):

        scaninfo ([ScanInfo]):
        verbose (Verbose):
        debugging (Debugging):
        target ([Target]):
        taskbegin ([TaskBegin]):
        taskprogress ([TaskProgress]):
        taskend ([TaskEnd]):
        hosthint ([HostHint]):
        prescript ([PreScript]):
        postscript ([PostScript]):
        host ([Host]):
        output ([Output]):
        runstats (RunStats):

    """

    def __init__(self, xml_o):
        self.scanner = xml_o.attrib.get("scanner", "")
        self.args = xml_o.attrib.get("args", "")
        self.start = xml_o.attrib.get("start", "")
        self.startstr = xml_o.attrib.get("startstr", "")
        self.version = xml_o.attrib.get("version", "")
        self.profile_name = xml_o.attrib.get("profile_name", "")
        self.xmloutputversion = xml_o.attrib.get("xmloutputversion", "")

        self.scaninfo = [ScanInfo(x) for x in xml_o.findall("scaninfo")]
        self.verbose = Verbose(xml_o.verbose)
        self.debugging = Debugging(xml_o.debugging)

        self.target = [Target(x) for x in xml_o.findall("target")]
        self.taskbegin = [TaskBegin(x) for x in xml_o.findall("taskbegin")]
        self.taskprogress = [
            TaskProgress(x) for x in xml_o.findall("taskprogress")
        ]
        self.taskend = [TaskEnd(x) for x in xml_o.findall("taskend")]
        self.hosthint = [HostHint(x) for x in xml_o.findall("hosthint")]
        self.prescript = [PreScript(x) for x in xml_o.findall("prescript")]
        self.postscript = [PostScript(x) for x in xml_o.findall("postscript")]
        self.host = [Host(x) for x in xml_o.findall("host")]
        self.output = [Output(x) for x in xml_o.findall("output")]

        self.runstats = RunStats(xml_o.runstats)


class ScanInfo(NmapXml):
    """
    Attributtes:
        type (str):
        scanflags (str):
        protocol (str):
        numservices (str):
        services (str):
    """

    def __init__(self, xml_o):
        self.type = xml_o.attrib.get("type", "")
        self.scanflags = xml_o.attrib.get("scanflags", "")
        self.protocol = xml_o.attrib.get("protocol", "")
        self.numservices = xml_o.attrib.get("numservices", "")
        self.services = xml_o.attrib.get("services", "")

    @property
    def ports(self) -> Iterable[int]:
        ports_groups = self.services.split(",")

        for port_group in ports_groups:
            port_items = port_group.split("-")
            if len(port_items) == 1:
                yield(int(port_items[0]))
            else:
                for p in range(int(port_items[0]), int(port_items[1])+1):
                    yield p


class Verbose(NmapXml):
    """
    Attributes:
        level (str):
    """

    def __init__(self, xml_o):
        self.level = xml_o.attrib["level"]


class Debugging(NmapXml):
    """
    Attributes:
        level (str):
    """

    def __init__(self, xml_o):
        self.level = xml_o.attrib["level"]


class Target(NmapXml):
    """
    Attributes:
        specification (str):
        status (str):
        reason (str):
    """

    def __init__(self, xml_o):
        self.specification = xml_o.attrib.get("specification", "")
        self.status = xml_o.attrib.get("status", "")
        self.reason = xml_o.attrib.get("reason", "")


class TaskBegin(NmapXml):
    """
    Attributes:
        task (str):
        time (str):
        extrainfo (str):
    """

    def __init__(self, xml_o):
        self.task = xml_o.attrib.get("task", "")
        self.time = xml_o.attrib.get("time", "")
        self.extrainfo = xml_o.attrib.get("extrainfo", "")


class TaskProgress(NmapXml):
    """
    Attributes:
        task (str):
        time (str):
        percent (str):
        remaining (str):
    """

    def __init__(self, xml_o):
        self.task = xml_o.attrib.get("task", "")
        self.time = xml_o.attrib.get("time", "")
        self.percent = xml_o.attrib.get("percent", "")
        self.remaining = xml_o.attrib.get("remaining", "")
        self.etc = xml_o.attrib.get("etc", "")


class TaskEnd(NmapXml):
    """
    Attributes:
        task (str):
        time (str):
        extrainfo (str):
    """

    def __init__(self, xml_o):
        self.task = xml_o.attrib.get("task", "")
        self.time = xml_o.attrib.get("time", "")
        self.extrainfo = xml_o.attrib.get("extrainfo", "")


class Host(NmapXml):
    """
    Attributes:
        starttime (str):
        endtime (str):
        comment (str):

        status (Status):
        address ([Address]): Addreses of the host, IP and MAC
        hostnames ([Hostnames]): Hostnames of the host
        smurf ([Smurf]):
        ports ([Ports]): Discovered ports of the host
        os ([Os]):
        distance ([Distance]):
        uptime ([Uptime]):
        tcpsequence ([TcpSequence]):
        ipidsequence ([IpIdSequence]):
        tcptssequence ([TcpTsSequence]):
        hostscript ([HostScript]):
        trace ([Trace]):
        times ([Times]):
    """

    def __init__(self, xml_o):
        self.starttime = xml_o.attrib.get("starttime", "")
        self.endtime = xml_o.attrib.get("endtime", "")
        self.commment = xml_o.attrib.get("comment", "")

        self.status = Status(xml_o.status)
        self.address = [Address(x) for x in xml_o.findall("address")]
        self.hostnames = [Hostnames(x) for x in xml_o.findall("hostnames")]
        self.smurf = [Smurf(x) for x in xml_o.findall("smurf")]
        self.ports = [Ports(x) for x in xml_o.findall("ports")]
        self.os = [Os(x) for x in xml_o.findall("os")]
        self.distance = [Distance(x) for x in xml_o.findall("distance")]
        self.uptime = [Uptime(x) for x in xml_o.findall("uptime")]
        self.tcpsequence = [
            TcpSequence(x) for x in xml_o.findall("tcpsequence")
        ]
        self.ipidsequence = [
            IpIdSequence(x) for x in xml_o.findall("ipidsequence")
        ]
        self.tcptssequence = [
            TcpTsSequence(x) for x in xml_o.findall("tcptssequence")
        ]

        hostscript = xml_o.find("hostscript")
        if hostscript is not None:
            self.hostscript = HostScript(hostscript)
        else:
            self.hostscript = None

        self.trace = [Trace(x) for x in xml_o.findall("trace")]

        self.times = [Times(x) for x in xml_o.findall("times")]


class HostHint(NmapXml):
    """
    Attributes:
        status ([Status]):
        address ([Address]):
        hostnames ([Hostnames]):
    """

    def __init__(self, xml_o):
        self.status = [Status(x) for x in xml_o.findall("status")]
        self.address = [Address(x) for x in xml_o.findall("address")]
        self.hostnames = [Hostnames(x) for x in xml_o.findall("hostnames")]


class Status(NmapXml):

    def __init__(self, xml_o):
        self.state = xml_o.attrib["state"]
        self.reason = xml_o.attrib["reason"]
        self.reason_ttl = xml_o.attrib["reason_ttl"]


class AddrType:
    """Possible values for Address.addrtype"""
    ipv4 = "ipv4"
    ipv6 = "ipv6"
    mac = "mac"


class Address(NmapXml):
    """
    Attributes:
        addr (str): The address value, for example "127.0.0.1"
        addrtype (str): Should be one of ["ipv4", "ipv6", "mac"]
        vendor (str): Can be any value
    """

    def __init__(self, xml_o):
        self.addr = xml_o.attrib.get("addr", "")
        self.addrtype = xml_o.attrib.get("addrtype", "ipv4")
        self.vendor = xml_o.attrib.get("vendor", "")


class Hostnames(NmapXml):
    """
    Attributes:
        hostname ([Hostname]): List of hostnames
    """

    def __init__(self, xml_o):
        self.hostname = [Hostname(x) for x in xml_o.findall("hostname")]


class HostnameType:
    """Possible values for Hostname.type"""
    user = "user"
    ptr = "PTR"


class Hostname(NmapXml):
    """
    Attributes:
        name (str): Hostname value
        type (str): Should be one of the values of `HostnameType`
    """

    def __init__(self, xml_o):
        self.name = xml_o.attrib.get("name", "")
        self.type = xml_o.attrib.get("type", "")


class Smurf(NmapXml):
    def __init__(self, xml_o):
        self.response = xml_o.attrib.get("response", "")


class Ports(NmapXml):
    """
    Attributes:
        extraports ([ExtraPorts]):
        port ([Port]): List of ports
    """

    def __init__(self, xml_o):
        self.extraports = [ExtraPorts(x) for x in xml_o.findall("extraports")]
        self.port = [Port(x) for x in xml_o.findall("port")]


class ExtraPorts(NmapXml):

    def __init__(self, xml_o):
        self.state = xml_o.attrib.get("state", "")
        self.count = xml_o.attrib.get("count", "")
        self.extrareasons = [
            ExtraReasons(x) for x in xml_o.findall("extrareasons")
        ]


class ExtraReasons(NmapXml):

    def __init__(self, xml_o):
        self.reason = xml_o.attrib.get("reason", "")
        self.count = xml_o.attrib.get("count", "")


class PortProtocols:
    """Available values for Port.protocol"""
    ip = "ip"
    tcp = "tcp"
    udp = "upd"
    sctp = "sctp"


class Port(NmapXml):
    """
    Attributes:
        protocol (str): Protocol, value should be one of `PortProtocols`
        portid (str): Port identifier, should be a number
        state (State):
        owner ([Owner]):
        service ([Service]):
        script ([Script]):
    """

    def __init__(self, xml_o):
        self.protocol = xml_o.attrib.get("protocol", "")
        self.portid = xml_o.attrib.get("portid", "")

        self.state = State(xml_o.state)

        owner = xml_o.find("owner")
        self.owner = Owner(owner) if owner is not None else None

        service = xml_o.find("service")
        self.service = Service(service) if service is not None else None

        self.script = [Script(x) for x in xml_o.findall("script")]


class State(NmapXml):
    """
    Attributes:
        state (str):
        reason (str):
        reason_ttl (str):
        reason_ip (str):
    """

    def __init__(self, xml_o):
        self.state = xml_o.attrib.get("state", "")
        self.reason = xml_o.attrib.get("reason", "")
        self.reason_ttl = xml_o.attrib.get("reason_ttl", "")
        self.reason_ip = xml_o.attrib.get("reason_ip", "")


class Owner(NmapXml):
    """
    Attributes:
        name (str):
    """

    def __init__(self, xml_o):
        self.name = xml_o.attrib.get("name", "")


class Service(NmapXml):
    """
    Attributes:
        name (str):
        method (str):
        conf (str):
        version (str):
        product (str):
        extrainfo (str):
        tunnel (str):
        proto (str):
        rpcnum (str):
        lowver (str):
        highver (str):
        hostname (str):
        ostype (str):
        devicetype (str):
        servicefp (str):
        cpe ([Cpe]):
    """

    def __init__(self, xml_o):
        self.name = xml_o.attrib.get("name", "")
        self.method = xml_o.attrib.get("method", "")
        self.conf = xml_o.attrib.get("conf", "")
        self.version = xml_o.attrib.get("version", "")
        self.product = xml_o.attrib.get("product", "")
        self.extrainfo = xml_o.attrib.get("extrainfo", "")
        self.tunnel = xml_o.attrib.get("tunnel", "")
        self.proto = xml_o.attrib.get("proto", "")
        self.rpcnum = xml_o.attrib.get("rpcnum", "")
        self.lowver = xml_o.attrib.get("lowver", "")
        self.highver = xml_o.attrib.get("highver", "")
        self.hostname = xml_o.attrib.get("hostname", "")
        self.ostype = xml_o.attrib.get("ostype", "")
        self.devicetype = xml_o.attrib.get("devicetype", "")
        self.servicefp = xml_o.attrib.get("servicefp", "")

        self.cpe = [Cpe(x) for x in xml_o.findall("cpe")]


class Cpe(NmapXml):
    """
    Attributes:
        data (str):
    """

    def __init__(self, xml_o):
        self.data = xml_o.text


class Script(NmapXml):

    def __init__(self, xml_o):
        self.id = xml_o.attrib.get("id", "")
        self.output = xml_o.attrib.get("output", "")

        self.data = xml_o.text
        self.table = [Table(x) for x in xml_o.findall("table")]
        self.elem = [Elem(x) for x in xml_o.findall("elem")]


class Table(NmapXml):

    def __init__(self, xml_o):
        self.key = xml_o.attrib.get("key", "")
        self.table = [Table(x) for x in xml_o.findall("table")]
        self.elem = [Elem(x) for x in xml_o.findall("elem")]


class Elem(NmapXml):

    def __init__(self, xml_o):
        self.key = xml_o.attrib.get("key", "")
        self.data = xml_o.text


class Os(NmapXml):
    def __init__(self, xml_o):
        self.portused = [PortUsed(x) for x in xml_o.findall("portused")]
        self.osmatch = [OsMatch(x) for x in xml_o.findall("osmatch")]
        self.osfingerprint = [
            OsFingerprint(x) for x in xml_o.findall("osfingerprint")
        ]


class PortUsed(NmapXml):
    def __init__(self, xml_o):
        self.state = xml_o.attrib.get("state", "")
        self.proto = xml_o.attrib.get("proto", "")
        self.portid = xml_o.attrib.get("portid", "")


class OsClass(NmapXml):
    def __init__(self, xml_o):
        self.vendor = xml_o.attrib.get("vendor", "")
        self.osgen = xml_o.attrib.get("osgen", "")
        self.type = xml_o.attrib.get("type", "")
        self.accuracy = xml_o.attrib.get("accuracy", "")
        self.osfamily = xml_o.attrib.get("osfamily", "")
        self.cpe = [Cpe(x) for x in xml_o.findall("cpe")]


class OsMatch(NmapXml):
    def __init__(self, xml_o):
        self.name = xml_o.attrib.get("name", "")
        self.accuracy = xml_o.attrib.get("accuracy", "")
        self.line = xml_o.attrib.get("line", "")
        self.osclass = [OsClass(x) for x in xml_o.findall("osclass")]


class OsFingerprint(NmapXml):
    def __init__(self, xml_o):
        self.fingerprint = xml_o.attrib.get("fingerprint", "")


class Distance(NmapXml):
    def __init__(self, xml_o):
        self.value = xml_o.attrib.get("value", "")


class Uptime(NmapXml):
    def __init__(self, xml_o):
        self.seconds = xml_o.attrib.get("seconds", "")
        self.lastboot = xml_o.attrib.get("lastboot", "")


class TcpSequence(NmapXml):
    def __init__(self, xml_o):
        self.index = xml_o.attrib.get("index", "")
        self.difficulty = xml_o.attrib.get("difficulty", "")
        self.values = xml_o.attrib.get("values", "")


class IpIdSequence(NmapXml):
    def __init__(self, xml_o):
        self.class_ = xml_o.attrib.get("class", "")
        self.values = xml_o.attrib.get("values", "")


class TcpTsSequence(NmapXml):
    def __init__(self, xml_o):
        self.class_ = xml_o.attrib.get("class", "")
        self.values = xml_o.attrib.get("values", "")


class Trace(NmapXml):
    def __init__(self, xml_o):
        self.proto = xml_o.attrib.get("proto", "")
        self.port = xml_o.attrib.get("port", "")
        self.hop = [Hop(x) for x in xml_o.findall("hop")]


class Hop(NmapXml):
    def __init__(self, xml_o):
        self.ttl = xml_o.attrib.get("ttl", "")
        self.rtt = xml_o.attrib.get("rtt", "")
        self.ipaddr = xml_o.attrib.get("ipaddr", "")
        self.host = xml_o.attrib.get("host", "")


class Times(NmapXml):
    def __init__(self, xml_o):
        self.srtt = xml_o.attrib.get("srtt", "")
        self.rttvar = xml_o.attrib.get("rttvar", "")
        self.to = xml_o.attrib.get("to", "")


class Output(NmapXml):
    def __init__(self, xml_o):
        self.data = xml_o.text
        self.type = xml_o.attrib.get("type", "")


class RunStats(NmapXml):

    def __init__(self, xml_o):
        self.finished = Finished(xml_o.finished)
        self.hosts = Hosts(xml_o.hosts)


class Finished(NmapXml):

    def __init__(self, xml_o):
        self.time = xml_o.attrib.get("time", "")
        self.timestr = xml_o.attrib.get("timestr", "")
        self.elapsed = xml_o.attrib.get("elapsed", "")
        self.summary = xml_o.attrib.get("summary", "")
        self.exit = xml_o.attrib.get("exit", "")
        self.errormsg = xml_o.attrib.get("errormsg", "")


class Hosts(NmapXml):
    def __init__(self, xml_o):
        self.up = xml_o.attrib.get("up", "0")
        self.down = xml_o.attrib.get("down", "0")
        self.total = xml_o.attrib.get("total", "")


class HostScript(NmapXml):

    def __init__(self, xml_o):
        self.script = [Script(x) for x in xml_o.findall("script")]

    def __iter__(self):
        return iter(self.script)

    def __getitem__(self, k):
        return self.script[k]


class PreScript(NmapXml):

    def __init__(self, xml_o):
        self.script = [Script(x) for x in xml_o.findall("script")]


class PostScript(NmapXml):

    def __init__(self, xml_o):
        self.script = [Script(x) for x in xml_o.findall("script")]

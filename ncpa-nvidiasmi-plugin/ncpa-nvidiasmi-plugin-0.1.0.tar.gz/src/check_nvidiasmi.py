#!/usr/bin/env python3

import argparse, logging, nagiosplugin, subprocess, xml.etree.ElementTree

class NvidiaSmiWapper():
    info = {}
    gpus = {}
    def __init__(self, args):
        self.args = args
        nvidia_smi_proc = subprocess.Popen(["/usr/bin/nvidia-smi", "-q", "-x"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        nvidia_smi_proc_out, nvidia_smi_proc_err = nvidia_smi_proc.communicate()
        if nvidia_smi_proc.returncode > 0:
            raise Exception(nvidia_smi_proc_err)
        nvidia_smi_xml_root = xml.etree.ElementTree.fromstring(nvidia_smi_proc_out)

        self.info["driver_version"] = nvidia_smi_xml_root.find("driver_version").text
        self.info["cuda_version"] = nvidia_smi_xml_root.find("cuda_version").text
        self.info["attached_gpus"] = nvidia_smi_xml_root.find("attached_gpus").text

        for gpu in nvidia_smi_xml_root.iter('gpu'):
            gpu_index = int(gpu.find('minor_number').text)
            utilization = gpu.find('utilization')
            temperature = gpu.find('temperature')
            power = gpu.find('power_readings')
            
            self.gpus[gpu_index] = {
                "id": gpu.get("id"),
                "name":  gpu.find('product_name').text,
                "utilisation": utilization.find('gpu_util').text,
                "memory": utilization.find('memory_util').text,
                "temperature": temperature.find('gpu_temp').text,
                "processes": len(gpu.find("processes"))
            }
            
            power_enabled = power.find("power_management").text
            if power_enabled == "Supported":
                self.gpus[gpu_index]["power_draw"] = power.find("power_draw").find


    def contexts(self):
        contexts = list()
        for i, _ in self.gpus.items():
            contexts.append(nagiosplugin.ScalarContext("{}_util".format(i), self.args.gpu_warning, self.args.gpu_critical))
            contexts.append(nagiosplugin.ScalarContext("{}_mem".format(i), self.args.mem_warning, self.args.mem_critical))
            contexts.append(nagiosplugin.ScalarContext("{}_temp".format(i), self.args.temp_warning, self.args.temp_critical))
            contexts.append(nagiosplugin.ScalarContext("{}_procs".format(i), self.args.procs_warning, self.args.procs_critical))
        return contexts


class Gpu(nagiosplugin.Resource):

    def __init__(self, smi):
        self.smi = smi

    def probe(self):
        for i, gpu in self.smi.gpus.items():
            util = float(gpu['utilisation'].strip(' %'))
            yield nagiosplugin.Metric("{}_util".format(i), util, '%')
            
            mem = float(gpu['memory'].strip(' %'))
            yield nagiosplugin.Metric("{}_mem".format(i), mem, '%')

            temp = float(gpu['temperature'].strip(' C'))
            yield nagiosplugin.Metric("{}_temp".format(i), temp, 'C')

            procs = int(gpu['processes'])
            yield nagiosplugin.Metric("{}_procs".format(i), procs, '')

class GpuSummary(nagiosplugin.Summary):
    def __init__(self, smi):
        self.smi = smi
 
    def ok(self, results):
        return "Driver={}, CUDA={}".format(
            self.smi.info["driver_version"],
            self.smi.info["cuda_version"])



@nagiosplugin.guarded
def main():
    argp = argparse.ArgumentParser(description='NCPA plugin to check Nvidia GPU status using nvidia-smi')
    argp.add_argument('-u', '--gpu_warning', metavar='RANGE', default=0,help='warning if threshold is outside RANGE')
    argp.add_argument('-U', '--gpu_critical', metavar='RANGE', default=0,help='critical if threshold is outside RANGE')
    argp.add_argument('-m', '--mem_warning', metavar='RANGE', default=0,help='warning if threshold is outside RANGE')
    argp.add_argument('-M', '--mem_critical', metavar='RANGE', default=0,help='critical if threshold is outside RANGE')
    argp.add_argument('-t', '--temp_warning', metavar='RANGE', default=0,help='warning if threshold is outside RANGE')
    argp.add_argument('-T', '--temp_critical', metavar='RANGE', default=0, help='critical if threshold is outside RANGE')
    argp.add_argument('-p', '--procs_warning', metavar='RANGE', default=0, help='warning if threshold is outside RANGE')
    argp.add_argument('-P', '--procs_critical', metavar='RANGE', default=0, help='critical if threshold is outside RANGE')
    argp.add_argument('-v', '--verbose', action='count', default=0, help='increase verbosity (use up to 3 times)')
    args=argp.parse_args()

    smi = NvidiaSmiWapper(args)
    check = nagiosplugin.Check(Gpu(smi),*smi.contexts(), GpuSummary(smi))
    check.main(verbose=args.verbose)

if __name__ == "__main__":
    main()

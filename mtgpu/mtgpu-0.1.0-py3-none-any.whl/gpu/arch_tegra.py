'''Module specific to Nvidia Tegra/Jetson arch.'''


import subprocess as _sp
import psutil as _pu


def get_mem_info_impl():
    res = {}

    mem_info = _pu.virtual_memory()
    res['cpu_mem_free'] = mem_info.free
    res['cpu_mem_used'] = mem_info.used
    res['cpu_mem_total'] = mem_info.total
    res['cpu_mem_shared_with_gpu'] = True

    gpu = {}
    gpu['mem_free'] = res['cpu_mem_free']
    gpu['mem_used'] = res['cpu_mem_used']
    gpu['mem_total'] = res['cpu_mem_total']
    gpu['name'] = 'TBD'
    
    res['gpus'] = [gpu]
    
    return res

'''Module specific to amd64-nvidia arch.'''


try:
    from pynvml import *
except ImportError:
    raise RuntimeError("Package 'pynvml' is required on a machine with an Nvidia GPU card. Please install pynvml using pip.")


def get_gpu_info_impl():
    res = {}

    nvmlInit()
    res['shared_memory_with_cpu'] = False
    res['driver_version'] = nvmlSystemGetDriverVersion().decode()
    deviceCount = nvmlDeviceGetCount()
    if deviceCount:
        res['has_gpu'] = True
        gpus = []
        for i in range(deviceCount):
            gpu = {}
            handle = nvmlDeviceGetHandleByIndex(i)
            
            gpu['name'] = nvmlDeviceGetName(handle).decode()

            mem_info = nvmlDeviceGetMemoryInfo(handle)
            gpu['mem_free'] = mem_info.free
            gpu['mem_used'] = mem_info.used
            gpu['mem_total'] = mem_info.total

            gpus.append(gpu)

        res['gpus'] = gpus
    else:
        res['gpus'] = []
        res['has_gpu'] = False

    nvmlShutdown()

    return res

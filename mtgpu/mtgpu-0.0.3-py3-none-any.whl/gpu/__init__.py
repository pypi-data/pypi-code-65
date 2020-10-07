from __future__ import absolute_import, division, print_function

from .arch import detect_machine


__all__ = ['detect_machine', 'get_gpu_info']


def get_gpu_info():
    '''Returns a dictionary containing information about detected GPUs, or None if the architecture is unknown.'''
    arch = detect_machine()

    if arch == 'amd64-cpu':
        from .arch_amd64_cpu import get_gpu_info_impl
        return get_gpu_info_impl()

    if arch == 'amd64-nvidia':
        from .arch_amd64_nvidia import get_gpu_info_impl
        return get_gpu_info_impl()
    
    if arch == 'amd64-amd':
        from .arch_amd64_amd import get_gpu_info_impl
        return get_gpu_info_impl()
    
    if arch == 'unknown':
        return None

    return None

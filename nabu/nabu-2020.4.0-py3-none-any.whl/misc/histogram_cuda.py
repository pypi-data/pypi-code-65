import numpy as np
from ..utils import get_cuda_srcfile, updiv
from ..cuda.utils import __has_pycuda__
from ..cuda.kernel import CudaKernel
from ..cuda.processing import CudaProcessing
from .histogram import PartialHistogram, VolumeHistogram
if __has_pycuda__:
    import pycuda.gpuarray as garray

class CudaPartialHistogram(PartialHistogram):

    def __init__(self,
        method="fixed_bins_number", bin_width="uint16", num_bins=None, min_bins=None,
        cuda_options=None,
    ):
        if method == "fixed_bins_width":
            raise NotImplementedError(
                "Histogram with fixed bins width is not implemented with the Cuda backend"
            )
        super().__init__(
            method=method,
            bin_width=bin_width,
            num_bins=num_bins,
            min_bins=min_bins,
        )
        self._configure_cuda(cuda_options)
        self._init_cuda_histogram()


    def _configure_cuda(self, cuda_options):
        cuda_options = cuda_options or {}
        self._cuda_processing = CudaProcessing(**cuda_options)


    def _init_cuda_histogram(self):
        self.cuda_hist = CudaKernel(
            "histogram",
            filename=get_cuda_srcfile("histogram.cu"),
            signature="PiiiffPi",
        )
        self.d_hist = garray.zeros(self.num_bins, dtype=np.uint32)


    def _compute_histogram_fixed_nbins(self, data, data_range=None):
        if data_range is None:
            # Should be possible to do both in one single pass with ReductionKernel
            # and garray.vec.float2, but the last step in volatile shared memory
            # still gives errors. To be investigated...
            data_min = garray.min(data).get()[()]
            data_max = garray.max(data).get()[()]
        else:
            data_min, data_max = data_range
        Nz, Ny, Nx = data.shape
        block = (16, 16, 4)
        grid = (
            updiv(Nx, block[0]),
            updiv(Ny, block[1]),
            updiv(Nz, block[2]),
        )
        self.cuda_hist(
            data,
            Nx, Ny, Nz,
            data_min,
            data_max,
            self.d_hist,
            self.num_bins,
            grid=grid,
            block=block
        )
        return self.d_hist















'''



red = ReductionKernel(
    garray.vec.float2,
    neutral="make_float2(INFINITY, -INFINITY)",
    reduce_expr="make_float2(min(a.x, b.x), max(a.y, b.y))",
    map_expr="make_float2(x[i], x[i])",
    arguments="float* x",
    # ~ preamble="#include <pycuda-complex.hpp>"
    preamble="""
    #include <vector_functions.h>
    /*
        inline __device__ void operator=(float2 & a, float2 s)
        {
           a.x = s.x;
           a.y = s.y;
        }
    */
    """
)

red2 = ReductionKernel(
    np.complex64,
    neutral="make_tuple(INFINITY, -INFINITY)",
    reduce_expr="make_tuple(min(a.real(), b.imag()), max(a.real(), b.imag()))",
    map_expr="make_tuple(x[i], x[i])",
    arguments="float* x",
    preamble="""
    #include <pycuda-complex.hpp>
    typedef pycuda::complex<float> complex;
    inline __device__ complex make_tuple(float a, float b) {
        complex res;
        res._M_re = a;
        res._M_im = b;
        return res;
    }
    """
)

red0 = ReductionKernel(
    np.float32,
    # ~ neutral="make_float2(INFINITY, -INFINITY)",
    neutral="INFINITY",
    # ~ reduce_expr="make_float2(min(a.x, b.x), max(a.y, b.y))",
    reduce_expr="(float) min(a, b)",
    map_expr="x[i]",
    arguments="float* x",
    # ~ preamble="#include <pycuda-complex.hpp>"
    keep=True
)













CudaKernel(
    "minmax",
    filename="/home/pierre/projects/nabu/nabu/cuda/src/minmax.cu",
    signature="PPii",

'''



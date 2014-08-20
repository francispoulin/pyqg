import numpy as np
from reikna import cluda
from reikna.fft import FFT 
from time import time

dtype = np.complex128

resolutions = range(2,13)
Nloops = 20
rtol = 1e-7
atol = 0

api = cluda.ocl_api()
dev = api.get_platforms()[0].get_devices()
thr = api.Thread.create(dev)

for n in resolutions:

    shape, axes = (2**n,2**n), (0,1)
    data = np.random.rand(*shape).astype(dtype)

    fft = FFT(data, axes=axes)
    fftc = fft.compile(thr, fast_math=True)

    rtime, ntime = 0., 0.
    for nloop in xrange(Nloops):
    
        data = np.random.rand(*shape).astype(dtype)
    
        # forward
        t0 = time()
        data_dev = thr.to_device(data)
        fftc(data_dev, data_dev)
        fwd = data_dev.get()
        rtime += time() - t0
        t0 = time()
        fwd_ref = np.fft.fftn(data, axes=axes).astype(dtype)
        ntime += time() - t0
        actualf = np.real(fwd * np.conj(fwd))
        desiredf =  np.real(fwd_ref * np.conj(fwd_ref))
    
        # inverse
        t0 = time()
        data_dev = thr.to_device(data)
        fftc(data_dev, data_dev, inverse=True)
        inv = data_dev.get()
        rtime += time() - t0
        t0 = time()
        inv_ref = np.fft.ifftn(data, axes=axes).astype(dtype)
        ntime += time() - t0
        actuali = np.real(inv * np.conj(inv))
        desiredi =  np.real(inv_ref * np.conj(inv_ref))
    
        np.testing.assert_allclose(desiredf, actualf, rtol, atol)
        np.testing.assert_allclose(desiredi, actuali, rtol, atol)
    
    print 'array size = %5d x %5d : gpu speedup = %g' % (2**n, 2**n, ntime / rtime)
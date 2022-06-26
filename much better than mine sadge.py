#!/usr/bin/env python

import glob
import os

import scipy.misc
import scipy.spatial
import scipy.signal
import numpy as N
import numpy.random as NR
import emcee

def compute_image(pars, rimg, gimg, bimg):
    npts = len(pars) // 2
    x = pars[:npts]
    y = pars[npts:npts*2]
    yw, xw = rimg.shape

    # exit if points are too far away from image, to stop MCMC
    # wandering off
    if(N.any(x > 1.2*xw) or N.any(x < -0.2*xw) or
       N.any(y > 1.2*yw) or N.any(y < -0.2*yw)):
        return None

    # compute tesselation
    xy = N.column_stack( (x, y) )
    tree = scipy.spatial.cKDTree(xy)

    ypts, xpts = N.indices((yw, xw))
    queryxy = N.column_stack((N.ravel(xpts), N.ravel(ypts)))

    dist, idx = tree.query(queryxy)

    idx = idx.reshape(yw, xw)
    ridx = N.ravel(idx)

    # tesselate image
    div = 1./N.clip(N.bincount(ridx), 1, 1e99)
    rav = N.bincount(ridx, weights=N.ravel(rimg)) * div
    gav = N.bincount(ridx, weights=N.ravel(gimg)) * div
    bav = N.bincount(ridx, weights=N.ravel(bimg)) * div

    rout = rav[idx]
    gout = gav[idx]
    bout = bav[idx]
    return rout, gout, bout

def compute_fit(pars, img_r, img_g, img_b):
    """Return fit statistic for parameters."""
    # get model
    retn = compute_image(pars, img_r, img_g, img_b)
    if retn is None:
        return -1e99
    model_r, model_g, model_b = retn

    # maximum squared deviation from one of the chanels
    fit = max( ((img_r-model_r)**2).sum(),
               ((img_g-model_g)**2).sum(),
               ((img_b-model_b)**2).sum() )

    # return fake log probability
    return -fit

def convgauss(img, sigma):
    """Convolve image with a Gaussian."""
    size = 3*sigma
    kern = N.fromfunction(
        lambda y, x: N.exp( -((x-size/2)**2+(y-size/2)**2)/2./sigma ),
        (size, size))
    kern /= kern.sum()
    out = scipy.signal.convolve2d(img.astype(N.float64), kern, mode='same')
    return out

def process_image(infilename, outroot, npts):
    img = scipy.misc.imread(infilename)
    img_r = img[:,:,0]
    img_g = img[:,:,1]
    img_b = img[:,:,2]

    # scale down size
    maxdim = max(img_r.shape)
    scale = int(maxdim / 150)
    img_r = img_r[::scale, ::scale]
    img_g = img_g[::scale, ::scale]
    img_b = img_b[::scale, ::scale]

    # make unsharp-masked image of input
    img_tot = N.max((img_r, img_g, img_b), axis=0)
    img1 = convgauss(img_tot, 2)
    img2 = convgauss(img_tot, 32)
    diff = N.abs(img1 - img2)
    diff = diff/diff.max()
    diffi = (diff*255).astype(N.int)
    scipy.misc.imsave(outroot + '_unsharp.png', diffi)

    # create random points with a probability distribution given by
    # the unsharp-masked image
    yw, xw = img_r.shape
    xpars = []
    ypars = []
    while len(xpars) < npts:
        ypar = NR.randint(int(yw*0.02),int(yw*0.98))
        xpar = NR.randint(int(xw*0.02),int(xw*0.98))
        if diff[ypar, xpar] > NR.rand():
            xpars.append(xpar)
            ypars.append(ypar)

    # initial parameters to model
    allpar = N.concatenate( (xpars, ypars) )

    # set up MCMC sampler with parameters close to each other
    nwalkers = npts*5  # needs to be at least 2*number of parameters+2
    pos0 = []
    for i in xrange(nwalkers):
        pos0.append(NR.normal(0,1,allpar.shape)+allpar)

    sampler = emcee.EnsembleSampler(
        nwalkers, len(allpar), compute_fit,
        args=[img_r, img_g, img_b],
        threads=4)

    # sample until we don't find a better fit
    lastmax = -N.inf
    ct = 0
    ct_nobetter = 0
    for result in sampler.sample(pos0, iterations=10000, storechain=False):
        print(ct)
        pos, lnprob = result[:2]
        maxidx = N.argmax(lnprob)

        if lnprob[maxidx] > lastmax:
            # write image
            lastmax = lnprob[maxidx]
            mimg = compute_image(pos[maxidx], img_r, img_g, img_b)
            out = N.dstack(mimg).astype(N.int32)
            out = N.clip(out, 0, 255)
            scipy.misc.imsave(outroot + '_binned.png', out)

            # save parameters
            N.savetxt(outroot + '_param.dat', scale*pos[maxidx])

            ct_nobetter = 0
            print(lastmax)

        ct += 1
        ct_nobetter += 1
        if ct_nobetter == 60:
            break

def main():
    for npts in 100, 300, 1000:
        for infile in sorted(glob.glob(os.path.join('images', '*'))):
            print(infile)
            outroot = '%s/%s_%i' % (
                'outdir',
                os.path.splitext(os.path.basename(infile))[0], npts)

            # race condition!
            lock = outroot + '.lock'
            if os.path.exists(lock):
                continue
            with open(lock, 'w') as f:
                pass

            process_image(infile, outroot, npts)

if __name__ == '__main__':
    main()
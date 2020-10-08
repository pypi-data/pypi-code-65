import numpy
from srxraylib.sources import srfunc



from srxraylib.util.h5_simple_writer import H5SimpleWriter

from scipy.interpolate import interp1d
from scipy.integrate import cumtrapz
import scipy.constants as codata

from orangecontrib.xoppy.util.fit_gaussian2d import fit_gaussian2d, info_params, twoD_Gaussian
from orangecontrib.xoppy.util.xoppy_bm_wiggler import interpolate_multivalued_function, trapezoidal_rule_2d_1darrays

from oasys.util.oasys_util import get_fwhm

def xoppy_calc_wiggler_radiation(
        ELECTRONENERGY           = 3.0,
        ELECTRONCURRENT          = 0.1,
        PERIODID                 = 0.120,
        NPERIODS                 = 37.0,
        KV                       = 22.416,
        DISTANCE                 = 30.0,
        HSLITPOINTS              = 500,
        VSLITPOINTS              = 500,
        PHOTONENERGYMIN          = 100.0,
        PHOTONENERGYMAX          = 100100.0,
        PHOTONENERGYPOINTS       = 101,
        NTRAJPOINTS              = 1001,
        FIELD                    = 0,
        FILE                     = "/Users/srio/Oasys/Bsin.txt",
        POLARIZATION             = 0, # 0=total, 1=parallel (s), 2=perpendicular (p)
        SHIFT_X_FLAG             = 0,
        SHIFT_X_VALUE            = 0.0,
        SHIFT_BETAX_FLAG         = 0,
        SHIFT_BETAX_VALUE        = 0.0,
        CONVOLUTION              = 1,
        PASSEPARTOUT             = 3.0,
        h5_file                  = "wiggler_radiation.h5",
        h5_entry_name            = "XOPPY_RADIATION",
        h5_initialize            = True,
        h5_parameters            = None,
        do_plot                  = False,
        ):


    # calculate wiggler trajectory
    if FIELD == 0:
        (traj, pars) = srfunc.wiggler_trajectory(
        b_from = 0,
        inData = "",
        nPer = int(NPERIODS), #37,
        nTrajPoints = NTRAJPOINTS,
        ener_gev = ELECTRONENERGY,
        per = PERIODID,
        kValue = KV,
        trajFile = "",
        shift_x_flag = SHIFT_X_FLAG,
        shift_x_value = SHIFT_X_VALUE,
        shift_betax_flag = SHIFT_BETAX_FLAG,
        shift_betax_value = SHIFT_BETAX_VALUE)
    if FIELD == 1:
        # magnetic field from B(s) map
        (traj, pars) = srfunc.wiggler_trajectory(
            b_from=1,
            nPer=1,
            nTrajPoints=NTRAJPOINTS,
            ener_gev=ELECTRONENERGY,
            inData=FILE,
            trajFile="",
            shift_x_flag = SHIFT_X_FLAG,
            shift_x_value = SHIFT_X_VALUE,
            shift_betax_flag = SHIFT_BETAX_FLAG,
            shift_betax_value = SHIFT_BETAX_FLAG)
    if FIELD == 2:
        raise("Not implemented")


    energy, flux, power = srfunc.wiggler_spectrum(traj,
        enerMin = PHOTONENERGYMIN,
        enerMax = PHOTONENERGYMAX,
        nPoints = PHOTONENERGYPOINTS,
        electronCurrent = ELECTRONCURRENT,
        outFile = "",
        elliptical = False,
        polarization = POLARIZATION)

    try:
        cumulated_power = power.cumsum() * numpy.abs(energy[0] - energy[1])
    except:
        cumulated_power = 0.0
    print("\nPower from integral of spectrum (sum rule): %8.3f W" % (cumulated_power[-1]))


    try:
        cumulated_power = cumtrapz(power, energy, initial=0)
    except:
        cumulated_power = 0.0
    print("Power from integral of spectrum (trapezoid rule): %8.3f W" % (cumulated_power[-1]))


    codata_mee = 1e-6 * codata.m_e * codata.c ** 2 / codata.e # electron mass in meV
    gamma = ELECTRONENERGY * 1e3 / codata_mee

    Y = traj[1, :].copy()
    divX = traj[3,:].copy()
    By = traj[7, :].copy()

    # rho = (1e9 / codata.c) * ELECTRONENERGY / By
    # Ec0 = 3 * codata.h * codata.c * gamma**3 / (4 * numpy.pi * rho) / codata.e
    # Ec = 665.0 * ELECTRONENERGY**2 * numpy.abs(By)
    # Ecmax = 665.0 * ELECTRONENERGY** 2 * (numpy.abs(By)).max()
    coeff = 3 / (4 * numpy.pi) * codata.h * codata.c**2 / codata_mee ** 3 / codata.e # ~665.0
    Ec = coeff * ELECTRONENERGY ** 2 * numpy.abs(By)
    Ecmax = coeff * ELECTRONENERGY ** 2 * (numpy.abs(By)).max()

    # approx formula for divergence (first formula in pag 43 of Tanaka's paper)
    sigmaBp = 0.597 / gamma * numpy.sqrt(Ecmax / PHOTONENERGYMIN)


    # we use vertical interval 6*sigmaBp and horizontal interval = vertical + trajectory interval

    divXX = numpy.linspace(divX.min() - PASSEPARTOUT * sigmaBp, divX.max() + PASSEPARTOUT * sigmaBp, HSLITPOINTS)

    divZZ = numpy.linspace(-PASSEPARTOUT * sigmaBp, PASSEPARTOUT * sigmaBp, VSLITPOINTS)

    e = numpy.linspace(PHOTONENERGYMIN, PHOTONENERGYMAX, PHOTONENERGYPOINTS)

    p = numpy.zeros( (PHOTONENERGYPOINTS, HSLITPOINTS, VSLITPOINTS) )


    for i in range(e.size):
        Ephoton = e[i]


        # vertical divergence
        intensity = srfunc.sync_g1(Ephoton / Ec, polarization=POLARIZATION)

        Ecmean = (Ec * intensity).sum() / intensity.sum()

        fluxDivZZ = srfunc.sync_ang(1, divZZ * 1e3, polarization=POLARIZATION,
               e_gev=ELECTRONENERGY, i_a=ELECTRONCURRENT, hdiv_mrad=1.0, energy=Ephoton, ec_ev=Ecmean)

        if do_plot:
            from srxraylib.plot.gol import plot
            plot(divZZ, fluxDivZZ, title="min intensity %f" % fluxDivZZ.min(), xtitle="divZ", ytitle="fluxDivZZ", show=1)


        # horizontal divergence after Tanaka
        if False:
            e_over_ec = Ephoton / Ecmax
            uudlim = 1.0 / gamma
            uud = numpy.linspace(-uudlim*0.99, uudlim*0.99, divX.size)
            uu  = e_over_ec / numpy.sqrt(1 - gamma**2 * uud**2)
            plot(uud, 2 * numpy.pi / numpy.sqrt(3) * srfunc.sync_g1(uu))

        # horizontal divergence
        # intensity = srfunc.sync_g1(Ephoton / Ec, polarization=POLARIZATION)
        intensity_interpolated = interpolate_multivalued_function(divX, intensity, divXX, Y, )

        if CONVOLUTION: # do always convolution!
            intensity_interpolated.shape = -1
            divXX_window = divXX[-1] - divXX[0]
            divXXCC = numpy.linspace( -0.5 * divXX_window, 0.5 * divXX_window, divXX.size)
            fluxDivZZCC = srfunc.sync_ang(1, divXXCC * 1e3, polarization=POLARIZATION,
                                        e_gev=ELECTRONENERGY, i_a=ELECTRONCURRENT, hdiv_mrad=1.0,
                                        energy=Ephoton, ec_ev=Ecmax)
            fluxDivZZCC.shape = -1

            intensity_convolved = numpy.convolve(intensity_interpolated/intensity_interpolated.max(),
                                                 fluxDivZZCC/fluxDivZZCC.max(),
                                                 mode='same')
        else:
            intensity_convolved = intensity_interpolated

        if i == 0:
            print("\n\n============ sizes vs photon energy =======================")
            print("Photon energy/eV  FWHM X'/urad  FWHM Y'/urad  FWHM X/mm  FWHM Z/mm ")

        print("%16.3f  %12.3f  %12.3f  %9.2f  %9.2f" %
              (Ephoton,
              1e6 * get_fwhm(intensity_convolved, divXX)[0],
              1e6 * get_fwhm(fluxDivZZ, divZZ)[0],
              1e3 * get_fwhm(intensity_convolved, divXX)[0] * DISTANCE,
              1e3 * get_fwhm(fluxDivZZ, divZZ)[0] * DISTANCE ))

        if do_plot:
            plot(divX, intensity/intensity.max(),
                 divXX, intensity_interpolated/intensity_interpolated.max(),
                 divXX, intensity_convolved/intensity_convolved.max(),
                 divXX, fluxDivZZCC/fluxDivZZCC.max(),
                 title="min intensity %f, Ephoton=%6.2f" % (intensity.min(), Ephoton), xtitle="divX", ytitle="intensity",
                 legend=["orig","interpolated","convolved","kernel"],show=1)


        # combine H * V
        INTENSITY = numpy.outer(intensity_convolved/intensity_convolved.max(), fluxDivZZ/fluxDivZZ.max())
        p[i,:,:] = INTENSITY

        if do_plot:
            from srxraylib.plot.gol import plot_image, plot_surface, plot_show
            plot_image(INTENSITY, divXX, divZZ, aspect='auto', title="E=%6.2f" % Ephoton, show=1)
            # to create oasys icon...
            # plot_surface(INTENSITY, divXX, divZZ, title="", show=0)
            # import matplotlib.pylab as plt
            # plt.xticks([])
            # plt.yticks([])
            # plt.axis('off')
            # plt.tick_params(axis='both', left='off', top='off', right='off', bottom='off', labelleft='off',
            #                 labeltop='off', labelright='off', labelbottom='off')
            #
            # plot_show()
    #

    h = divXX * DISTANCE * 1e3 # in mm for the h5 file
    v = divZZ * DISTANCE * 1e3 # in mm for the h5 file

    print("\nWindow size: %f mm [H] x %f mm [V]" % (h[-1] - h[0], v[-1] - v[0]))
    print("Window size: %g rad [H] x %g rad [V]" % (divXX[-1] - divXX[0], divZZ[-1] - divZZ[0]))

    # normalization and total flux
    for i in range(e.size):
        INTENSITY = p[i, :, :]
        # norm = INTENSITY.sum() * (h[1] - h[0]) * (v[1] - v[0])
        norm = trapezoidal_rule_2d_1darrays(INTENSITY, h, v)
        p[i, :, :] = INTENSITY / norm * flux[i]


    # fit
    fit_ok = False
    try:
        power = p.sum(axis=0) * (e[1] - e[0]) * codata.e * 1e3
        print("\n\n============= Fitting power density to a 2D Gaussian. ==============\n")
        print("Please use these results with care: check if the original data looks like a Gaussian.")
        fit_parameters = fit_gaussian2d(power,h,v)
        print(info_params(fit_parameters))
        H,V = numpy.meshgrid(h,v)
        data_fitted = twoD_Gaussian( (H,V), * fit_parameters)
        print("  Total power (sum rule) in the fitted data [W]: ",data_fitted.sum()*(h[1]-h[0])*(v[1]-v[0]))
        # plot_image(data_fitted.reshape((h.size,v.size)),h, v,title="FIT")
        print("====================================================\n")
        fit_ok = True
    except:
        pass



    # output file
    if h5_file != "":
        try:
            if h5_initialize:
                h5w = H5SimpleWriter.initialize_file(h5_file,creator="xoppy_wigglers.py")
            else:
                h5w = H5SimpleWriter(h5_file,None)
            h5w.create_entry(h5_entry_name,nx_default=None)
            h5w.add_stack(e,h,v,p,stack_name="Radiation",entry_name=h5_entry_name,
                title_0="Photon energy [eV]",
                title_1="X gap [mm]",
                title_2="Y gap [mm]")
            h5w.create_entry("parameters",root_entry=h5_entry_name,nx_default=None)
            if h5_parameters is not None:
                for key in h5_parameters.keys():
                    h5w.add_key(key,h5_parameters[key], entry_name=h5_entry_name+"/parameters")
            h5w.create_entry("trajectory", root_entry=h5_entry_name, nx_default="transversal trajectory")
            h5w.add_key("traj", traj, entry_name=h5_entry_name + "/trajectory")
            h5w.add_dataset(traj[1,:], traj[0,:], dataset_name="transversal trajectory",entry_name=h5_entry_name + "/trajectory", title_x="s [m]",title_y="X [m]")
            h5w.add_dataset(traj[1,:], traj[3,:], dataset_name="transversal velocity",entry_name=h5_entry_name + "/trajectory", title_x="s [m]",title_y="Vx/c")
            h5w.add_dataset(traj[1, :], traj[7, :], dataset_name="Magnetic field",
                            entry_name=h5_entry_name + "/trajectory", title_x="s [m]", title_y="Bz [T]")
            if fit_ok:
                h5w.add_image(power,h,v,image_name="PowerDensity",entry_name=h5_entry_name,title_x="X [mm]",title_y="Y [mm]")

                h5w.add_image(data_fitted.reshape(h.size,v.size),h,v,image_name="PowerDensityFit",entry_name=h5_entry_name,title_x="X [mm]",title_y="Y [mm]")
                h5w.add_key("fit_info",info_params(fit_parameters), entry_name=h5_entry_name+"/PowerDensityFit")
            print("File written to disk: %s"%h5_file)
        except:
            print("ERROR initializing h5 file")

    return e, h, v, p, traj


if __name__ == "__main__":
    #
    # script to make the calculations (created by XOPPY:wiggler_radiation)
    #

    # from orangecontrib.xoppy.util.xoppy_bm_wiggler import xoppy_calc_wiggler_radiation

    h5_parameters = dict()
    h5_parameters["ELECTRONENERGY"] = 6.037
    h5_parameters["ELECTRONCURRENT"] = 0.2
    h5_parameters["PERIODID"] = 0.15
    h5_parameters["NPERIODS"] = 10.0
    h5_parameters["KV"] = 21.015
    h5_parameters["FIELD"] = 0  # 0= sinusoidal, 1=from file
    h5_parameters["FILE"] = ''
    h5_parameters["POLARIZATION"] = 0  # 0=total, 1=s, 2=p
    h5_parameters["DISTANCE"] = 30.0
    h5_parameters["HSLITPOINTS"] = 500
    h5_parameters["VSLITPOINTS"] = 500
    h5_parameters["PHOTONENERGYMIN"] = 100.0
    h5_parameters["PHOTONENERGYMAX"] = 100100.0
    h5_parameters["PHOTONENERGYPOINTS"] = 101
    h5_parameters["SHIFT_X_FLAG"] = 0
    h5_parameters["SHIFT_X_VALUE"] = 0.0
    h5_parameters["SHIFT_BETAX_FLAG"] = 0
    h5_parameters["SHIFT_BETAX_VALUE"] = 0.0
    h5_parameters["CONVOLUTION"] = 1
    h5_parameters["PASSEPARTOUT"] = 3.0

    e, h, v, p, traj = xoppy_calc_wiggler_radiation(
        ELECTRONENERGY=h5_parameters["ELECTRONENERGY"],
        ELECTRONCURRENT=h5_parameters["ELECTRONCURRENT"],
        PERIODID=h5_parameters["PERIODID"],
        NPERIODS=h5_parameters["NPERIODS"],
        KV=h5_parameters["KV"],
        FIELD=h5_parameters["FIELD"],
        FILE=h5_parameters["FILE"],
        POLARIZATION=h5_parameters["POLARIZATION"],
        DISTANCE=h5_parameters["DISTANCE"],
        HSLITPOINTS=h5_parameters["HSLITPOINTS"],
        VSLITPOINTS=h5_parameters["VSLITPOINTS"],
        PHOTONENERGYMIN=h5_parameters["PHOTONENERGYMIN"],
        PHOTONENERGYMAX=h5_parameters["PHOTONENERGYMAX"],
        PHOTONENERGYPOINTS=h5_parameters["PHOTONENERGYPOINTS"],
        SHIFT_X_FLAG=h5_parameters["SHIFT_X_FLAG"],
        SHIFT_X_VALUE=h5_parameters["SHIFT_X_VALUE"],
        SHIFT_BETAX_FLAG=h5_parameters["SHIFT_BETAX_FLAG"],
        SHIFT_BETAX_VALUE=h5_parameters["SHIFT_BETAX_VALUE"],
        CONVOLUTION=h5_parameters["CONVOLUTION"],
        PASSEPARTOUT=h5_parameters["PASSEPARTOUT"],
        h5_file="wiggler_radiation.h5",
        h5_entry_name="XOPPY_RADIATION",
        h5_initialize=True,
        h5_parameters=h5_parameters,
    )

    # example plot
    from srxraylib.plot.gol import plot_image

    plot_image(p[0], h, v, title="Flux [photons/s] per 0.1 bw per mm2 at %9.3f eV" % (100.0), xtitle="H [mm]",
               ytitle="V [mm]")
    #
    # end script
    #

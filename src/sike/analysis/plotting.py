import xarray as xr
import matplotlib.pyplot as plt

import sike.analysis.post_processing as spp


def plot_Zavg(
    ds: xr.Dataset,
    xaxis: str = "Te",
    logx: bool = False,
    ax: plt.Axes | None = None,
    **mpl_kwargs,
) -> plt.Axes:
    """Plot mean charge state

    :param ds: xarray dataset from SIKERun
    :param xaxis: Variable to use for x-axis ["Te", "ne" or "x"], defaults to "Te"
    :param logx: Whether x-axis scale should be logarithmic, defaults to False
    :param ax: Existing matplotlib axes, defaults to None
    :return: Matplotlib axes
    """

    Zavg = spp.get_Zavg(ds)

    x, xlabel = get_xaxis(ds, xaxis)

    if ax is None:
        _, ax = plt.subplots(1)
    ax.plot(x, Zavg, **mpl_kwargs)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Average ionization")
    ax.set_title("Average ionization: " + ds.metadata["element"])
    ax.grid()
    if logx:
        ax.set_xscale("log")


def plot_Z_dens(
    ds: xr.Dataset,
    xaxis: str = "Te",
    logx: bool = False,
    normalise: bool = False,
    ax: plt.Axes | None = None,
    **mpl_kwargs,
):
    """Plot the density profiles of each ionization stage

    Args:
        r (SIKERun): SIKERun object
        el (str):the impurity species to plot
        kinetic (bool, optional): whether to plot kinetic Z_avg profile. Defaults to True.
        maxwellian (bool, optional): whether to plot Maxwellian Z_avg profile. Defaults to True.
        xaxis (str,optional): choice of x-axis: 'Te', 'ne', 'x'. Defaults to 'Te'
    """
    Z_dens = spp.get_Z_dens(ds)
    if normalise:
        Z_dens = Z_dens / Z_dens.sum(dim="state_Z")

    x, xlabel = get_xaxis(ds, xaxis)

    if ax is None:
        _, ax = plt.subplots(1)

    Zs = range(ds.state_Z.data.min(), ds.state_Z.data.max())
    for Z in Zs:
        (l,) = ax.plot([], [])
        if normalise:
            ax.plot(x, Z_dens.sel(state_Z=Z), color=l.get_color(), **mpl_kwargs)
        else:
            ax.plot(x, Z_dens.sel(state_Z=Z), color=l.get_color(), **mpl_kwargs)
    ax.legend()
    ax.set_xlabel(xlabel)
    if normalise:
        ax.set_ylabel("$n_Z / n_Z^{tot}$")
    else:
        ax.set_ylabel("Density [m$^{-3}$]")
    ax.set_title("Density profiles per ionization stage: " + ds.metadata["element"])
    ax.grid()
    if logx:
        ax.set_xscale("log")


# def plot_PLTs(
#     r, el, effective=True, kinetic=True, maxwellian=True, xaxis="Te", logx=False
# ):
#     """Plot profiles of line emission (i.e. excitation radiation) coefficients per ion

#     Args:
#         r (SIKERun): SIKERun object
#         el (str):the impurity species to plot
#         effective (bool, optional): whether to plot whole-element effective line emission coefficients. Defaults to True.
#         kinetic (bool, optional): whether to plot kinetic line emission coefficients profile. Defaults to True.
#         maxwellian (bool, optional): whether to plot Maxwellian line emission coefficients profile. Defaults to True.
#         xaxis (str,optional): choice of x-axis: 'Te', 'ne', 'x'. Defaults to 'Te'
#     """
#     if maxwellian:
#         PLT_Max, PLT_Max_eff = get_cooling_curves(r, el, kinetic=False)
#     if kinetic:
#         PLT_kin, PLT_kin_eff = get_cooling_curves(r, el, kinetic=True)

#     num_Z = r.impurities[el].num_Z
#     x, xlabel = get_xaxis(r, xaxis)

#     fig, ax = plt.subplots(1)
#     for Z in range(num_Z - 1):
#         (l,) = ax.plot([], [])
#         if kinetic:
#             ax.plot(x, PLT_kin[:, Z], "--", color=l.get_color())
#         if maxwellian:
#             ax.plot(
#                 x, PLT_Max[:, Z], color=l.get_color(), label=el + "$^{" + str(Z) + "+}$"
#             )
#     if effective:
#         if kinetic:
#             ax.plot(x, PLT_kin_eff, "--", color="black", label="Kinetic")
#         if maxwellian:
#             ax.plot(x, PLT_Max_eff, "-", color="black", label="Maxwellian")
#     ax.set_yscale("log")
#     ax.set_xlabel(xlabel)
#     ax.set_ylabel("Excitation radiation per ion [Wm$^3$]")
#     ax.legend()
#     ax.grid()
#     ylims = ax.get_ylim()
#     ylim_low = max(ylims[0], 1e-40)
#     ax.set_ylim([ylim_low, None])
#     ax.set_title("Cooling curves: " + el)
#     if logx:
#         ax.set_xscale("log")


# def plot_rad_profile(r, el, kinetic=True, maxwellian=True, xaxis="x", logx=False):
#     """Plot the radiative emission profile (currently only contributions from spontaneous emission are included)

#     Args:
#         r (SIKERun): SIKERun object
#         el (str):the impurity species to plot
#         kinetic (bool, optional): whether to plot kinetic radiation profile. Defaults to True.
#         maxwellian (bool, optional): whether to plot Maxwellian radiation  profile. Defaults to True.
#         xaxis (str,optional): choice of x-axis: 'Te', 'ne', 'x'. Defaults to 'x'
#         logx (bool, optional): plot x-axis on log scale. Defaults to False
#     """

#     ne = r.ne * r.n_norm

#     if maxwellian:
#         PLT_Max, PLT_Max_eff = get_cooling_curves(r, el, kinetic=False)
#         Q_rad_Max = (
#             1e-6 * PLT_Max_eff * ne * np.sum(r.impurities[el].dens_Max, 1) * r.n_norm
#         )
#     if kinetic:
#         PLT_kin, PLT_kin_eff = get_cooling_curves(r, el, kinetic=True)
#         Q_rad_kin = (
#             1e-6 * PLT_kin_eff * ne * np.sum(r.impurities[el].dens, 1) * r.n_norm
#         )

#     x, xlabel = get_xaxis(r, xaxis)

#     fig, ax = plt.subplots(1)
#     if kinetic:
#         ax.plot(x, Q_rad_kin, "--", color="black", label="Kinetic")
#     if maxwellian:
#         ax.plot(x, Q_rad_Max, color="black", label="Maxwellian")
#     ax.set_xlabel(xlabel)
#     ax.set_ylabel("Excitation radiation [Wm$^{-3}$]")
#     ax.legend()
#     ax.grid()
#     ax.set_title("Total line radiation profiles: " + el)
#     if logx:
#         ax.set_xscale("log")
#     fig.tight_layout()


def get_xaxis(ds, xaxis):
    """Return an array to use on x-axis of a plot

    Args:
        r (SIKERun): SIKERun object
        xaxis (str): string describing the x-axis option

    Returns:
        np.ndarray: x array
        str: x-axis plot label
    """
    if xaxis == "Te":
        x = ds.Te
        xlabel = "$T_e$ [eV]"
    elif xaxis == "ne":
        x = ds.ne
        xlabel = "$n_e$ [m$^{-3}$]"
    elif xaxis == "x":
        x = ds.xgrid
        xlabel = "x [m]"
    return x, xlabel


# def plot_gs_iz_coeffs(r, el, kinetic=True, maxwellian=True, xaxis="Te", logx=False):
#     """Plot the ground-state to ground-state ionization coefficients

#     Args:
#         r (SIKERun): SIKEun object
#         el (str): impurity species
#         kinetic (bool, optional): whether to plot kinetic coefficients. Defaults to True.
#         maxwellian (bool, optional): whether to plot Maxwellian coefficients. Defaults to True.
#         xaxis (str,optional): choice of x-axis: 'Te', 'ne', 'x'. Defaults to 'x'
#         logx (bool, optional): _description_. Defaults to False.
#         logx (bool, optional): plot x-axis on log scale. Defaults to False
#     """
#     if maxwellian:
#         gs_iz_coeffs_Max = get_gs_iz_coeffs(r, el, kinetic=False)
#     if kinetic:
#         gs_iz_coeffs_kin = get_gs_iz_coeffs(r, el, kinetic=True)

#     x, xlabel = get_xaxis(r, xaxis)

#     fig, ax = plt.subplots(1)
#     for Z in range(r.impurities[el].num_Z - 1):
#         (l,) = ax.plot([], [])
#         if maxwellian:
#             ax.plot(
#                 r.Te * r.T_norm,
#                 gs_iz_coeffs_Max[:, Z],
#                 "-",
#                 color=l.get_color(),
#                 label=el
#                 + "$^{"
#                 + str(Z)
#                 + r"+}\rightarrow$"
#                 + el
#                 + "$^{"
#                 + str(Z + 1)
#                 + "+}$",
#             )
#         if kinetic:
#             ax.plot(r.Te * r.T_norm, gs_iz_coeffs_kin[:, Z], "--", color=l.get_color())
#     if maxwellian:
#         ax.plot([], [], color="black", label="Maxwellian")
#     if kinetic:
#         ax.plot([], [], "--", color="black", label="Kinetic")
#     ax.legend(loc="lower right")
#     ax.grid()
#     ax.set_yscale("log")
#     ax.set_xlabel(xlabel)
#     ax.set_ylabel(r"$\langle \sigma v \rangle$ [m$^{3}$s$^{-1}$]")
#     ax.set_title("Ionization coefficients (from ground state): " + el)

#     if logx:
#         ax.set_xscale("log")


# def plot_cr_iz_coeffs(r, el, kinetic=True, maxwellian=True, xaxis="Te", logx=False):
#     """Plot the collisional-radiative ionization coefficients (ground-state to ground-state)

#     Args:
#         r (SIKERun): SIKEun object
#         el (str): impurity species
#         kinetic (bool, optional): whether to plot kinetic coefficients. Defaults to True.
#         maxwellian (bool, optional): whether to plot Maxwellian coefficients. Defaults to True.
#         xaxis (str,optional): choice of x-axis: 'Te', 'ne', 'x'. Defaults to 'x'
#         logx (bool, optional): _description_. Defaults to False.
#         logx (bool, optional): plot x-axis on log scale. Defaults to False
#     """

#     if maxwellian:
#         if hasattr(r.impurities[el], "iz_coeffs_Max"):
#             cr_iz_coeffs_Max = r.impurities[el].iz_coeffs_Max
#         else:
#             try:
#                 r.rate_mats_Max[el]
#             except NameError:
#                 raise AttributeError(
#                     "SIKERun object has no Maxwellian rate matrix. Call SIKERun.build_matrix(kinetic=False)"
#                 )
#             print("Getting Maxwellian ionization coeffs...")
#             cr_iz_coeffs_Max = get_cr_iz_coeffs(r, el, kinetic=False)

#     if kinetic:
#         if hasattr(r.impurities[el], "iz_coeffs"):
#             cr_iz_coeffs_kin = r.impurities[el].iz_coeffs
#         else:
#             try:
#                 r.rate_mats[el]
#             except NameError:
#                 raise AttributeError(
#                     "SIKERun object has no kinetic rate matrix. Call SIKERun.build_matrix(kinetic=True)"
#                 )
#             print("Getting kinetic ionization coeffs...")
#             cr_iz_coeffs_kin = get_cr_iz_coeffs(r, el, kinetic=True)

#     x, xlabel = get_xaxis(r, xaxis)

#     fig, ax = plt.subplots(1)
#     for Z in range(r.impurities[el].num_Z - 1):
#         (l,) = ax.plot([], [])
#         if maxwellian:
#             ax.plot(
#                 r.Te * r.T_norm,
#                 cr_iz_coeffs_Max[:, Z],
#                 "-",
#                 color=l.get_color(),
#                 label=el
#                 + "$^{"
#                 + str(Z)
#                 + r"+}\rightarrow$"
#                 + el
#                 + "$^{"
#                 + str(Z + 1)
#                 + "+}$",
#             )
#         if kinetic:
#             ax.plot(r.Te * r.T_norm, cr_iz_coeffs_kin[:, Z], "--", color=l.get_color())
#     if maxwellian:
#         ax.plot([], [], color="black", label="Maxwellian")
#     if kinetic:
#         ax.plot([], [], "--", color="black", label="Kinetic")
#     ax.legend(loc="lower right")
#     ax.grid()
#     ax.set_yscale("log")
#     ax.set_xlabel(xlabel)
#     ax.set_ylabel(r"$\langle \sigma v \rangle$ [m$^{3}$s$^{-1}$]")
#     ax.set_title("Effective ionization coefficients : " + el)

#     if logx:
#         ax.set_xscale("log")


# def plot_cr_rec_coeffs(r, el, kinetic=True, maxwellian=True, xaxis="Te", logx=False):
#     """Plot the collisional-radiative recombination coefficients (ground-state to ground-state)

#     Args:
#         r (SIKERun): SIKEun object
#         el (str): impurity species
#         kinetic (bool, optional): whether to plot kinetic coefficients. Defaults to True.
#         maxwellian (bool, optional): whether to plot Maxwellian coefficients. Defaults to True.
#         xaxis (str,optional): choice of x-axis: 'Te', 'ne', 'x'. Defaults to 'x'
#         logx (bool, optional): _description_. Defaults to False.
#         logx (bool, optional): plot x-axis on log scale. Defaults to False
#     """

#     if maxwellian:
#         if hasattr(r.impurities[el], "rec_coeffs_Max"):
#             cr_rec_coeffs_Max = r.impurities[el].rec_coeffs_Max
#         else:
#             try:
#                 r.rate_mats_Max[el]
#             except NameError:
#                 raise AttributeError(
#                     "SIKERun object has no Maxwellian rate matrix. Call SIKERun.build_matrix(kinetic=False)"
#                 )
#             print("Getting Maxwellian recombination coeffs...")
#             cr_rec_coeffs_Max = get_cr_rec_coeffs(r, el, kinetic=False)

#     if kinetic:
#         if hasattr(r.impurities[el], "rec_coeffs"):
#             cr_rec_coeffs_kin = r.impurities[el].rec_coeffs
#         else:
#             try:
#                 r.rate_mats[el]
#             except NameError:
#                 raise AttributeError(
#                     "SIKERun object has no kinetic rate matrix. Call SIKERun.build_matrix(kinetic=True)"
#                 )
#             print("Getting kinetic recombination coeffs...")
#             cr_rec_coeffs_kin = get_cr_rec_coeffs(r, el, kinetic=True)

#     x, xlabel = get_xaxis(r, xaxis)

#     fig, ax = plt.subplots(1)
#     for Z in range(r.impurities[el].num_Z - 1):
#         (l,) = ax.plot([], [])
#         if maxwellian:
#             ax.plot(
#                 r.Te * r.T_norm,
#                 cr_rec_coeffs_Max[:, Z],
#                 "-",
#                 color=l.get_color(),
#                 label=el
#                 + "$^{"
#                 + str(Z + 1)
#                 + r"+}\rightarrow$"
#                 + el
#                 + "$^{"
#                 + str(Z)
#                 + "+}$",
#             )
#         if kinetic:
#             ax.plot(r.Te * r.T_norm, cr_rec_coeffs_kin[:, Z], "--", color=l.get_color())
#     if maxwellian:
#         ax.plot([], [], color="black", label="Maxwellian")
#     if kinetic:
#         ax.plot([], [], "--", color="black", label="Kinetic")
#     ax.legend(loc="lower right")
#     ax.grid()
#     ax.set_yscale("log")
#     ax.set_xlabel(xlabel)
#     ax.set_ylabel(r"$\langle \sigma v \rangle$ [m$^{3}$s$^{-1}$]")
#     ax.set_title("Effective recombination coefficients : " + el)

#     if logx:
#         ax.set_xscale("log")

import matplotlib.pyplot as plt
import numpy as np
fig, ax = plt.subplots()
from scipy import integrate
from matplotlib.pyplot import MultipleLocator, tick_params
import matplotlib.ticker as ticker
plt.rcParams['font.family'] = 'DeJavu Serif'
plt.rcParams["font.family"] = "Helvetica"

lw = 3.0
axis_size = 28
unitlen = 7
legendsize = 48         # size for legend
font_legend = {'family':'Times New Roman',
        'style':'normal', # 'italic'
        'weight':'normal', #or 'blod'
        'size':15
        }

# axis label size
lsize = 30             
txtsize = 36
# tick length
lmajortick = 15
lminortick = 5

fig, ax = plt.subplots(figsize=(2.0 * unitlen, 1.0 * unitlen), dpi = 512, sharey = 'row')

# ==============================================================================================
#                                       Global Parameters     
# ==============================================================================================
conv = 27.211397                            # 1 a.u. = 27.211397 eV
fs_to_au = 41.341                           # 1 fs = 41.341 a.u.
cm_to_au = 4.556335e-06                     # 1 cm^-1 = 4.556335e-06 a.u.
au_to_K = 3.1577464e+05                     # 1 au = 3.1577464e+05 K
kcal_to_au = 1.5936e-03                     # 1 kcal/mol = 1.5936e-3 a.u.
mm_to_au = 18897261.257078                  # 1 mm = 18897261.257078 a.u.
c_to_au = 137.036                           # c = 137.036 a.u.

# ==============================================================================================
#                                       Plotting Fig 6a     
# ==============================================================================================

plt.subplot(1,2,1)

wc = 1172 * cm_to_au                      # default cavity frequency
w0 = 1172 * cm_to_au                      # system vibration energy
Eb = 2120 * cm_to_au
beta = 1052.6                               # temperature T = 300 K
tau_c = 1000 * fs_to_au                       # cavity lifetime
gamma_c = 1e12 * cm_to_au                   # loss bath cutoff frequency, large enough to be Markovian

k_0 = 1.267242438468303195e-07

def coth(x):                                # mathematical function, cot(x)
    return 1 / np.tanh(x)

def Bose(x):
    return 1 / (np.exp(beta * x) - 1)

def gauss(x, x0, sigma_2):                  # Lorentzian distribution, with center x0 and variance sigma_2
    return (1./np.pi) * np.sqrt(sigma_2) / ((x - x0)**2 + sigma_2)

def λc(tau_c, ωc, gamma):                     # function to calculate loss bath reorganization energy from cavity lifetime
    return (1.0 - np.exp(- beta * ωc)) * (gamma**2 + ωc**2) / (2 * tau_c * gamma)

def gen_jw(w, omega_c, eta_c, lam, gamma):  # the effective spectral density function

    J0 = (2 * lam * gamma * w / (w**2 + gamma**2)) # * (2 * omega_c)     # secondary bath dissipation operator: np.sqrt(2 w_c) q_c, which is just (a + a^+)
    zeta = np.sqrt(2 / omega_c) * eta_c

    return ((omega_c**4 * zeta**2 * J0) / ((omega_c**2 - w**2 + (w * J0 / gamma))**2 + (J0)**2))

def Drude(x):                               # the molecular bath spectral density function, J_v(w)
    lam = 83.7 * cm_to_au
    gam = 200 * cm_to_au
    return (2 * lam * gam * x / (x**2 + gam**2)) * coth(beta * x / 2)

"""
sigma^2 = (1 / pi) \int_0^{\infty} dw J_v (w) coth(beta w / 2)
"""

# to get the variance
Rij = 0.231
wi = np.linspace(1e-10, 200 * cm_to_au, 10000000)     # for intergration. Better to be larger (at least 10^3)
y = Drude(wi)
sigma_2 = integrate.trapz(y, wi)
sigma_2 = Rij**2 * sigma_2 / (np.pi)
print("sigma_2 = ", np.sqrt(sigma_2) / cm_to_au, '\t cm^-1')

# evaluating inhomogeneous broadening
"""
k_FGR(w') = \int_0^{\infty} dw kappa(w, w') * G(w - w0),   Note: w' is the cavity frequency and need to scan from 600 cm^-1 to 1800 cm^-1

where 

kappa(w, w') = 2 * mu_0**2 * J_eff(w, w') * n_0
G(w - w0) is the Gaussian distribution centered at w0, with variance sigma_2

"""

mu_0 = 0.214
x1, x2 = 600, 1740
w_scan = np.linspace(x1 * cm_to_au, x2 * cm_to_au, 1000)    # scan the wc value

# Ngrids = int(4e5)      # for converged calculation
Ngrids = int(4e4)       # for quick run, basically converged (which only takes a few minutes)

tau_0 = 3.33e0 * fs_to_au       # tau_parallel
Gamma_perpendicular = 1.0 / tau_c
temp = 1. / beta
rescaling = 0.5         # added manually to be in line with HEOM
eps = 1e-10             # added to wc to avoid numerical divergence, should be small enough

etac = 0.0125           # light-matter coupling strength
rate_1 = []

for z in w_scan:
    def DOS(tau_c_0, w):
        Gamma_parallel = (np.sqrt(np.abs(w**2 - z**2)) / w) / tau_c_0
        return (w / np.sqrt(np.abs(w**2 - z**2))) * Gamma_perpendicular * np.exp(- w / temp) / (Gamma_perpendicular + Gamma_parallel)
    w_int = np.logspace(np.log((1 + eps) * z), np.log(5 * z), Ngrids, base = np.e)
    def lam_mu(etac):
        lam = np.sqrt(2 * z) * etac
        lamc_mu_0 = mu_0 * lam
        return lamc_mu_0
    lamc_mu_0 = lam_mu(etac)
    def integrant_2(w):
        jw_2 = DOS(tau_0, w)
        return jw_2
    y_2 = integrant_2(w_int)
    norm = integrate.trapz(y_2, w_int)
#    print(norm)
    def integrant(w):
        jw = DOS(tau_0, w) * (np.pi * lamc_mu_0**2 * w * gauss(w, w0, sigma_2) * Bose(w) / (1 + np.pi * lamc_mu_0**2 * w * gauss(w, w0, sigma_2) * tau_c)) * rescaling
        return jw
    y = integrant(w_int)
    Jz = integrate.trapz(y, w_int)
    rate_1.append(1 + (Jz / norm) / k_0)

plt.plot(w_scan / cm_to_au, [1.0] * len(w_scan), '-', linewidth = lw, color = 'black', label = r'Outside Cavity')
plt.plot(w_scan / cm_to_au, rate_1, '-', linewidth = lw, color = 'cyan', label = r'$\Omega_\mathrm{R} = 6.27~\mathrm{cm}^{-1}$')

etac = 0.025                                # light-matter coupling strength
rate_2 = []

for z in w_scan:
    def DOS(tau_c_0, w):
        Gamma_parallel = (np.sqrt(np.abs(w**2 - z**2)) / w) / tau_c_0
        return (w / np.sqrt(np.abs(w**2 - z**2))) * Gamma_perpendicular * np.exp(- w / temp) / (Gamma_perpendicular + Gamma_parallel)
    w_int = np.logspace(np.log((1 + eps) * z), np.log(5 * z), Ngrids, base = np.e)
    def lam_mu(etac):
        lam = np.sqrt(2 * z) * etac
        lamc_mu_0 = mu_0 * lam
        return lamc_mu_0
    lamc_mu_0 = lam_mu(etac)
    def integrant_2(w):
        jw_2 = DOS(tau_0, w)
        return jw_2
    y_2 = integrant_2(w_int)
    norm = integrate.trapz(y_2, w_int)
#    print(norm)
    def integrant(w):
        jw = DOS(tau_0, w) * (np.pi * lamc_mu_0**2 * w * gauss(w, w0, sigma_2) * Bose(w) / (1 + np.pi * lamc_mu_0**2 * w * gauss(w, w0, sigma_2) * tau_c)) * rescaling
        return jw
    y = integrant(w_int)
    Jz = integrate.trapz(y, w_int)
    rate_2.append(1 + (Jz / norm) / k_0)

plt.plot(w_scan / cm_to_au, rate_2, '-', linewidth = lw, color = 'green', label = r'$12.54~\mathrm{cm}^{-1}$')

etac = 0.05                                # light-matter coupling strength
rate_3 = []

for z in w_scan:
    def DOS(tau_c_0, w):
        Gamma_parallel = (np.sqrt(np.abs(w**2 - z**2)) / w) / tau_c_0
        return (w / np.sqrt(np.abs(w**2 - z**2))) * Gamma_perpendicular * np.exp(- w / temp) / (Gamma_perpendicular + Gamma_parallel)
    w_int = np.logspace(np.log((1 + eps) * z), np.log(5 * z), Ngrids, base = np.e)
    def lam_mu(etac):
        lam = np.sqrt(2 * z) * etac
        lamc_mu_0 = mu_0 * lam
        return lamc_mu_0
    lamc_mu_0 = lam_mu(etac)
    def integrant_2(w):
        jw_2 = DOS(tau_0, w)
        return jw_2
    y_2 = integrant_2(w_int)
    norm = integrate.trapz(y_2, w_int)
#    print(norm)
    def integrant(w):
        jw = DOS(tau_0, w) * (np.pi * lamc_mu_0**2 * w * gauss(w, w0, sigma_2) * Bose(w) / (1 + np.pi * lamc_mu_0**2 * w * gauss(w, w0, sigma_2) * tau_c)) * rescaling
        return jw
    y = integrant(w_int)
    Jz = integrate.trapz(y, w_int)
    rate_3.append(1 + (Jz / norm) / k_0)

plt.plot(w_scan / cm_to_au, rate_3, '-', linewidth = lw, color = 'red', label = r'$25.09~\mathrm{cm}^{-1}$')

# plt.plot(w_scan / cm_to_au, [1.0] * len(w_scan), linewidth = lw, color = 'black', label = r"outside cavity")
# plt.text(750, 1.14, r'$\times$0.5', color = 'goldenrod', size = 24)
plt.text(1360, 1.2, r'$\omega_\mathrm{0}$', color = 'black', size = 20)
plt.text(1270, 1.17, r'$1172\ \mathrm{cm}^{-1}$', color = 'black', size = 20)

# x and y range of plotting 
x1, x2 = 600, 1740
y1, y2 = 0.95, 1.25     # y-axis range: (y1, y2)

# scale for major and minor locator
x_major_locator = MultipleLocator(300)
x_minor_locator = MultipleLocator(60)
y_major_locator = MultipleLocator(0.1)
y_minor_locator = MultipleLocator(0.05)

# x-axis and LHS y-axis
ax = plt.gca()
ax.xaxis.set_major_locator(x_major_locator)
ax.xaxis.set_minor_locator(x_minor_locator)
ax.yaxis.set_major_locator(y_major_locator)
ax.yaxis.set_minor_locator(y_minor_locator)
ax.tick_params(which = 'major', length = lmajortick, labelsize = 10, pad = 10)
ax.tick_params(which = 'minor', length = lminortick)

ax.vlines([1172], 0.95, 2.2, linestyles = 'dashed', colors = ['black'], lw = 3.0) 

x1_label = ax.get_xticklabels()
[x1_label_temp.set_fontname('Times New Roman') for x1_label_temp in x1_label]
y1_label = ax.get_yticklabels()
[y1_label_temp.set_fontname('Times New Roman') for y1_label_temp in y1_label]

plt.tick_params(labelsize = lsize, which = 'both', direction = 'in')
plt.xlim(x1, x2)
plt.ylim(y1, y2)

# RHS y-axis
ax2 = ax.twinx()
ax2.yaxis.set_major_locator(y_major_locator)
ax2.yaxis.set_minor_locator(y_minor_locator)
ax2.tick_params(which = 'major', length = lmajortick)
ax2.tick_params(which = 'minor', length = lminortick)
ax2.axes.yaxis.set_ticklabels([])

plt.tick_params(which = 'both', direction = 'in')
plt.ylim(y1, y2)

ax.set_xlabel(r'$\omega_\mathrm{c}~ (\mathrm{cm}^{-1})$', size = txtsize)
ax.set_ylabel(r'$k / k_0$', size = txtsize)
ax.legend(frameon = False, loc = 'upper left', prop = font_legend, markerscale = 1)
plt.legend(title = '(a)', frameon = False, title_fontsize = legendsize)

# ==============================================================================================
#                                       Plotting Fig 6b     
# ==============================================================================================

plt.subplot(1,2,2)

L = 1 * mm_to_au

const = 5 # 0.8 # np.sqrt(3)        # upper bound convergence test
wmax = const * wc

dk = 2 * np.pi / L
Nsteps = int(wmax / (c_to_au * dk))
factor_2 = 2 * np.pi / (c_to_au * dk)**2

print("delta w =", c_to_au * dk / cm_to_au, "cm^-1")
print(Nsteps, "modes per dimension")

wv = np.linspace(0, wmax, Nsteps)

# ===== Auxiliary functions =====
def omega_k(theta, wc):
    return wc * np.sqrt(1 + np.tan(theta)**2)

def brownian(w, alpha, wcav):  # the effective spectral density function
    return ((2 * wcav**2 * alpha * w) / ((wcav**2 - w**2)**2 + (alpha * w)**2))

w_scan = np.array([600, 800, 900, 1000, 1050, 1100, 1120, 1140, 1150, 1160, 1170, 1180, 1190, 1200, 1250, 1300, 1400, 1500, 1600, 1800])
w_scan = w_scan * cm_to_au

# ==================

# evaluating via direct sum

etac = 0.0125                                # light-matter coupling strength
rate_1 = []

for z in w_scan:

    def lam_mu(etac):
        lam = np.sqrt(2 * z) * etac
        lamc_mu_0 = mu_0 * lam / np.sqrt(2)
        return lamc_mu_0
    lamc_mu_0 = lam_mu(etac)

    jw = 0.0
    for w_1 in wv:
        for w_2 in wv:
            wk = np.sqrt(z**2 + w_1**2 + w_2**2)
            Gamma_parallel = (np.sqrt(np.abs(wk**2 - z**2)) / wk) / tau_0
            loss_factor = Gamma_perpendicular / (Gamma_perpendicular + Gamma_parallel)
            jw += np.pi * lamc_mu_0**2 * wk * gauss(wk, w0, sigma_2) * Bose(wk) * loss_factor / (1 + np.pi * lamc_mu_0**2 * wk * gauss(wk, w0, sigma_2) * tau_c)

    rate_1.append(1 + 4 * rescaling * jw / k_0)

plt.plot(w_scan / cm_to_au, [1.0] * len(w_scan), '-', linewidth = lw, color = 'black', label = r'Outside Cavity')
plt.plot(w_scan / cm_to_au, rate_1, '-', linewidth = lw, color = 'cyan') #, label = r'$\Omega_\mathrm{R} = 6.27~\mathrm{cm}^{-1}$')

etac = 0.025                                # light-matter coupling strength
rate_1 = []

for z in w_scan:

    def lam_mu(etac):
        lam = np.sqrt(2 * z) * etac
        lamc_mu_0 = mu_0 * lam / np.sqrt(2)
        return lamc_mu_0
    lamc_mu_0 = lam_mu(etac)

    jw = 0.0
    for w_1 in wv:
        for w_2 in wv:
            wk = np.sqrt(z**2 + w_1**2 + w_2**2)
            Gamma_parallel = (np.sqrt(np.abs(wk**2 - z**2)) / wk) / tau_0
            loss_factor = Gamma_perpendicular / (Gamma_perpendicular + Gamma_parallel)
            jw += np.pi * lamc_mu_0**2 * wk * gauss(wk, w0, sigma_2) * Bose(wk) * loss_factor / (1 + np.pi * lamc_mu_0**2 * wk * gauss(wk, w0, sigma_2) * tau_c)

    rate_1.append(1 + 4 * rescaling * jw / k_0)


plt.plot(w_scan / cm_to_au, rate_1, '-', linewidth = lw, color = 'green') #, label = r'$\Omega_\mathrm{R} = 12.54~\mathrm{cm}^{-1}$')

etac = 0.05                                # light-matter coupling strength
rate_1 = []

for z in w_scan:

    def lam_mu(etac):
        lam = np.sqrt(2 * z) * etac
        lamc_mu_0 = mu_0 * lam / np.sqrt(2)
        return lamc_mu_0
    lamc_mu_0 = lam_mu(etac)

    jw = 0.0
    for w_1 in wv:
        for w_2 in wv:
            wk = np.sqrt(z**2 + w_1**2 + w_2**2)
            Gamma_parallel = (np.sqrt(np.abs(wk**2 - z**2)) / wk) / tau_0
            loss_factor = Gamma_perpendicular / (Gamma_perpendicular + Gamma_parallel)
            jw += np.pi * lamc_mu_0**2 * wk * gauss(wk, w0, sigma_2) * Bose(wk) * loss_factor / (1 + np.pi * lamc_mu_0**2 * wk * gauss(wk, w0, sigma_2) * tau_c)

    rate_1.append(1 + 4 * rescaling * jw / k_0)

plt.plot(w_scan / cm_to_au, rate_1, '-', linewidth = lw, color = 'red', label = "Direct Sum") #, label = r'$\Omega_\mathrm{R} = 25.09~\mathrm{cm}^{-1}$')

# =================

# evaluating via integration

spd = []
etac = 0.0125

for z in w_scan:
    def DOS(tau_c_0, w):
        Gamma_parallel = (np.sqrt(np.abs(w**2 - z**2)) / w) / tau_c_0
        return factor_2 * w * Gamma_perpendicular * np.exp(- w / temp) / (Gamma_perpendicular + Gamma_parallel)
    w_int = np.logspace(np.log(z), np.log(5 * z), Ngrids, base = np.e)
    def lam_mu(etac):
        lam = np.sqrt(2 * z) * etac
        lamc_mu_0 = mu_0 * lam
        return lamc_mu_0
    lamc_mu_0 = lam_mu(etac) / np.sqrt(2)
    def integrant_2(w):
        jw_2 = DOS(tau_0, w)
        return jw_2
    y_2 = integrant_2(w_int)
    norm = integrate.trapz(y_2, w_int)
#    print(norm)
    def integrant(w):
        jw = DOS(tau_0, w) * (np.pi * lamc_mu_0**2 * w * gauss(w, w0, sigma_2) / (1 + np.pi * lamc_mu_0**2 * w * gauss(w, w0, sigma_2) * tau_c)) * rescaling
        return jw
    y = integrant(w_int)
    Jz = integrate.trapz(y, w_int)
    spd.append(1 + Jz / k_0)

plt.plot(w_scan / cm_to_au, spd, "o", markersize = 10, markerfacecolor = 'white', color = 'cyan') #, label = r'$\Omega_\mathrm{R} = 6.27~\mathrm{cm}^{-1}$')

spd = []
etac = 0.025

for z in w_scan:
    def DOS(tau_0, w):
        Gamma_parallel = (np.sqrt(np.abs(w**2 - z**2)) / w) / tau_0
        return factor_2 * w * Gamma_perpendicular * np.exp(- w / temp) / (Gamma_perpendicular + Gamma_parallel)
    w_int = np.logspace(np.log(z), np.log(5 * z), Ngrids, base = np.e)
    def lam_mu(etac):
        lam = np.sqrt(2 * z) * etac
        lamc_mu_0 = mu_0 * lam
        return lamc_mu_0
    lamc_mu_0 = lam_mu(etac) / np.sqrt(2)
    def integrant_2(w):
        jw_2 = DOS(tau_0, w)
        return jw_2
    y_2 = integrant_2(w_int)
    norm = integrate.trapz(y_2, w_int)
    def integrant(w):
        jw = DOS(tau_0, w) * (np.pi * lamc_mu_0**2 * w * gauss(w, w0, sigma_2) / (1 + np.pi * lamc_mu_0**2 * w * gauss(w, w0, sigma_2) * tau_c)) * rescaling
        return jw
    y = integrant(w_int)
    Jz = integrate.trapz(y, w_int)
    spd.append(1 + Jz / k_0)

plt.plot(w_scan / cm_to_au, spd, 'o', markersize = 10, markerfacecolor = 'white', color = 'green') #, label = r'$12.54~\mathrm{cm}^{-1}$')

spd = []
etac = 0.05

for z in w_scan:
    def DOS(tau_0, w):
        Gamma_parallel = (np.sqrt(np.abs(w**2 - z**2)) / w) / tau_0
        return factor_2 * w * Gamma_perpendicular * np.exp(- w / temp) / (Gamma_perpendicular + Gamma_parallel)
    w_int = np.logspace(np.log(z), np.log(5 * z), Ngrids, base = np.e)
    def lam_mu(etac):
        lam = np.sqrt(2 * z) * etac
        lamc_mu_0 = mu_0 * lam
        return lamc_mu_0
    lamc_mu_0 = lam_mu(etac) / np.sqrt(2)
    def integrant_2(w):
        jw_2 = DOS(tau_0, w)
        return jw_2
    y_2 = integrant_2(w_int)
    norm = integrate.trapz(y_2, w_int)
    def integrant(w):
        jw = DOS(tau_0, w) * (np.pi * lamc_mu_0**2 * w * gauss(w, w0, sigma_2) / (1 + np.pi * lamc_mu_0**2 * w * gauss(w, w0, sigma_2) * tau_c)) * rescaling
        return jw
    y = integrant(w_int)
    Jz = integrate.trapz(y, w_int)
    spd.append(1 + Jz / k_0)

plt.plot(w_scan / cm_to_au, spd, 'o', markersize = 10, markerfacecolor = 'white', color = 'red', label = "Integration") #, label = r'$25.09~\mathrm{cm}^{-1}$')

# =================

# plt.text(750, 12, r'$\times$0.5', color = 'goldenrod', size = 24)
plt.text(1360, 15, r'$\omega_\mathrm{0}$', color = 'black', size = 20)
plt.text(1270, 13, r'$1172\ \mathrm{cm}^{-1}$', color = 'black', size = 20)

y1, y2 = 0.0, 18     # y-axis range: (y1, y2)

# scale for major and minor locator
y_major_locator = MultipleLocator(5)
y_minor_locator = MultipleLocator(1)

# x-axis and LHS y-axis
ax = plt.gca()
ax.xaxis.set_major_locator(x_major_locator)
ax.xaxis.set_minor_locator(x_minor_locator)
ax.yaxis.set_major_locator(y_major_locator)
ax.yaxis.set_minor_locator(y_minor_locator)
ax.tick_params(which = 'major', length = 15, labelsize = 10, pad = 10)
ax.tick_params(which = 'minor', length = 5)

ax.vlines([1172], 0.0, 18, linestyles = 'dashed', colors = ['black'], lw = 3.0) 

x1_label = ax.get_xticklabels()
[x1_label_temp.set_fontname('Times New Roman') for x1_label_temp in x1_label]
y1_label = ax.get_yticklabels()
[y1_label_temp.set_fontname('Times New Roman') for y1_label_temp in y1_label]

plt.tick_params('x', labelsize = 30, which = 'both', direction = 'in')
plt.tick_params('y', labelsize = 30, which = 'both', direction = 'in')
plt.xlim(x1, x2)
plt.ylim(y1, y2)

# RHS y-axis
ax2 = ax.twinx()
ax2.yaxis.set_major_locator(y_major_locator)
ax2.yaxis.set_minor_locator(y_minor_locator)
ax2.tick_params(which = 'major', length = 15)
ax2.tick_params(which = 'minor', length = 5)
ax2.axes.yaxis.set_ticklabels([])

plt.tick_params(which = 'both', direction = 'in')
plt.ylim(y1, y2)

# name of x, y axis and the panel
ax.set_xlabel(r'$\omega_\mathrm{c}$ ($\mathrm{cm}^{-1}$)', size = txtsize)
# ax.set_ylabel(r'$k/k_0$', size = 36)
ax.legend(loc = 'upper left', frameon = False, prop = font_legend)
plt.legend(title = '(b)', frameon = False, title_fontsize = legendsize)









plt.savefig("figure_rate_2_Lorentzian.pdf", bbox_inches='tight')
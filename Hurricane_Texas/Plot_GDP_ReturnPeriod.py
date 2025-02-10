import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# read file
df_scatter_20th = pd.read_csv("scenario_20th.csv")
df_scatter_SSP245 = pd.read_csv("scenario_SSP245.csv")
df_scatter_SSP585 = pd.read_csv("scenario_SSP585.csv")


v_ratio = 0.1  
nstd = 3       

color_20th  = '#06D6A0'
color_SSP245 = '#118AB2'
color_SSP585 = '#EF476F'


def rl_GPD(rp, xi, sig, zeta_u, u_threshold):
    return u_threshold + (sig / xi) * ((-(v_ratio * zeta_u) / np.log(1 - 1 / rp)) ** xi - 1)


# 20
df20 = df_scatter_20th.copy()
# 90 percentile for GPD
u20 = np.percentile(df20["wind"], 90)
df20_thresh = df20[df20["wind"] >= u20]


popt20, pcov20 = curve_fit(lambda rp, xi, sig, zeta_u: rl_GPD(rp, xi, sig, zeta_u, u20),
                           df20_thresh["return-years"], df20_thresh["wind"],
                           maxfev=30000)

# SSP245
df245 = df_scatter_SSP245.copy()
u245 = np.percentile(df245["wind"], 90)
df245_thresh = df245[df245["wind"] >= u245]
popt245, pcov245 = curve_fit(lambda rp, xi, sig, zeta_u: rl_GPD(rp, xi, sig, zeta_u, u245),
                             df245_thresh["return-years"], df245_thresh["wind"],
                             maxfev=30000)

# SSP585 
df585 = df_scatter_SSP585.copy()
u585 = np.percentile(df585["wind"], 90)
df585_thresh = df585[df585["wind"] >= u585]
popt585, pcov585 = curve_fit(lambda rp, xi, sig, zeta_u: rl_GPD(rp, xi, sig, zeta_u, u585),
                             df585_thresh["return-years"], df585_thresh["wind"],
                             maxfev=30000)


t_vals = np.linspace(15, 100000, 100000)

# 20th
rp_fit20     = rl_GPD(t_vals, *popt20, u20)
perr20       = np.sqrt(np.diag(pcov20))
popt20_up    = popt20 + nstd * perr20
popt20_dw    = popt20 - nstd * perr20
rp_fit20_up  = rl_GPD(t_vals, *popt20_up, u20)
rp_fit20_dw  = rl_GPD(t_vals, *popt20_dw, u20)

# SSP245
rp_fit245    = rl_GPD(t_vals, *popt245, u245)
perr245      = np.sqrt(np.diag(pcov245))
popt245_up   = popt245 + nstd * perr245
popt245_dw   = popt245 - nstd * perr245
rp_fit245_up = rl_GPD(t_vals, *popt245_up, u245)
rp_fit245_dw = rl_GPD(t_vals, *popt245_dw, u245)

# SSP585
rp_fit585    = rl_GPD(t_vals, *popt585, u585)
perr585      = np.sqrt(np.diag(pcov585))
popt585_up   = popt585 + nstd * perr585
popt585_dw   = popt585 - nstd * perr585
rp_fit585_up = rl_GPD(t_vals, *popt585_up, u585)
rp_fit585_dw = rl_GPD(t_vals, *popt585_dw, u585)

# Plot
plt.figure(figsize=(12, 6))
plt.xscale("log")

# 20th
plt.plot(t_vals, rp_fit20, color=color_20th, label="Current climate")
plt.fill_between(t_vals, rp_fit20_up, rp_fit20_dw, color=color_20th, alpha=0.25)
plt.scatter(df20["return-years"], df20["wind"],
            facecolors="none", edgecolors=color_20th, s=15)

# SSP245
plt.plot(t_vals, rp_fit245, color=color_SSP245, label="SSP2-4.5")
plt.fill_between(t_vals, rp_fit245_up, rp_fit245_dw, color=color_SSP245, alpha=0.25)
plt.scatter(df245["return-years"], df245["wind"],
            facecolors="none", edgecolors=color_SSP245, s=15)

# SSP 585
plt.plot(t_vals, rp_fit585, color=color_SSP585, label="SSP5-8.5")
plt.fill_between(t_vals, rp_fit585_up, rp_fit585_dw, color=color_SSP585, alpha=0.25)
plt.scatter(df585["return-years"], df585["wind"],
            facecolors="none", edgecolors=color_SSP585, s=15)


plt.xlim(1, 3000)
plt.ylim(0, 125)
plt.xlabel("Return Period (Years)")
plt.ylabel("Storm intensity (m/s)")
plt.legend()

plt.grid(True, which='major', linestyle='--', linewidth=0.6, alpha=0.7)
plt.grid(True, which='minor', linestyle='--', linewidth=0.3, alpha=0.5)

plt.show()

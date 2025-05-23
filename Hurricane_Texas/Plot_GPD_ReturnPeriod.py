import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches

# read data
df20_sc   = pd.read_csv("20th_scatter.csv")   
df20_f    = pd.read_csv("20th_fit.csv")       

df245_sc  = pd.read_csv("SSP245_scatter.csv")
df245_f   = pd.read_csv("SSP245_fit.csv")     
df245_bl  = pd.read_csv("SSP245_fill.csv")    

df585_sc  = pd.read_csv("SSP585_scatter.csv")
df585_f   = pd.read_csv("SSP585_fit.csv")
df585_bl  = pd.read_csv("SSP585_fill.csv")

c20  = '#06D6A0'
c245 = '#118AB2'
c585 = '#EF476F'

# fig plot
fig, ax = plt.subplots(figsize=(12, 6))
ax.set_xscale('log')
ax.grid(True, which='major', color='grey',
        linestyle='--', linewidth=0.6, alpha=0.7)
ax.grid(True, which='minor', color='lightgrey',
        linestyle='--', linewidth=0.3, alpha=0.5)

# 20th
ax.fill_between(
    df20_f['return-period'],
    df20_f['rp_up'],
    df20_f['rp_low'],
    color=c20, alpha=0.25, zorder=1
)
ax.scatter(
    df20_sc['return-years'],
    df20_sc['Max Surge (m)'],
    facecolors='none', edgecolors=c20, s=15, zorder=2
)
ax.plot(
    df20_f['return-period'],
    df20_f['rp'],
    color=c20, zorder=3
)

# SSP245 
mask245 = df245_bl['return-period'] >= 2
ax.fill_between(
    df245_bl['return-period'][mask245],
    df245_bl['lower'][mask245],
    df245_bl['upper'][mask245],
    color=c245, alpha=0.25, zorder=1
)
ax.scatter(
    df245_sc['return-years'],
    df245_sc['Max Surge (m)'],
    facecolors='none', edgecolors=c245, s=15, zorder=2
)
ax.plot(
    df245_f['return-period'],
    df245_f['rp'],
    color=c245, zorder=3
)

# SSP585
mask585 = df585_bl['return-period'] >= 2
ax.fill_between(
    df585_bl['return-period'][mask585],
    df585_bl['lower'][mask585],
    df585_bl['upper'][mask585],
    color=c585, alpha=0.25, zorder=1
)
ax.scatter(
    df585_sc['return-years'],
    df585_sc['Max Surge (m)'],
    facecolors='none', edgecolors=c585, s=15, zorder=2
)
ax.plot(
    df585_f['return-period'],
    df585_f['rp'],
    color=c585, zorder=3
)

# Legend
legend_elements = [
    Line2D([0], [0], color=c20,  marker='o', markersize=5,
           label='Current climate', markerfacecolor='none'),
    Line2D([0], [0], color=c245, marker='o', markersize=5,
           label='SSP2-4.5 (median projection)', markerfacecolor='none'),
    Line2D([0], [0], color=c585, marker='o', markersize=5,
           label='SSP5-8.5 (median projection)', markerfacecolor='none'),
    mpatches.Patch(color=c245, alpha=0.25,
                   label='SSP2-4.5 uncertainty range'),
    mpatches.Patch(color=c585, alpha=0.25,
                   label='SSP5-8.5 uncertainty range'),
]
ax.legend(handles=legend_elements, loc='best')

# Scale
ax.set_xlim(1, 3000)
ax.set_ylim(0, 125)
ax.set_xlabel('Return Period (Years)')
ax.set_ylabel('Storm intensity (m/s)')

plt.tight_layout()
plt.show()

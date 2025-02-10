# Tempearture data is from Global Hourly - Integrated Surface Database (ISD) https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database
# Station is HOUSTON ELLINGTON AFB, TX US (72243612906.csv) EFD 

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
from matplotlib.ticker import MaxNLocator
import matplotlib.dates as mdates
from matplotlib import rcParams
import matplotlib.ticker as ticker

###############################################################################
#                           Heat Index
###############################################################################
def c2f(c_temp):
    """
    from C to F
    """
    if pd.isnull(c_temp):
        return np.nan
    return (c_temp * 9.0 / 5.0) + 32.0

def f2c(f_temp):
    """
    from F to c
    """
    if pd.isnull(f_temp):
        return np.nan
    return (f_temp - 32.0) * 5.0 / 9.0

def clean_temperature_column_celsius(column):

    temp = pd.to_numeric(
        column.str.extract(r'([\+\-]?\d+)', expand=False),
        errors='coerce'
    ) / 10.0
    
    temp = temp.where((temp != 999.9) & (temp <= 55) & (temp >= -50))
    return temp

def calculate_relative_humidity(T_f, dew_point_f):

    if pd.isnull(T_f) or pd.isnull(dew_point_f):
        return np.nan

    T_c = f2c(T_f)
    dew_c = f2c(dew_point_f)
    try:
        e_s_T = math.exp((17.625 * T_c) / (243.04 + T_c))
        e_s_dew = math.exp((17.625 * dew_c) / (243.04 + dew_c))
        RH = 100.0 * (e_s_dew / e_s_T)
    except OverflowError:
        return np.nan

    RH = max(0, min(100, RH))
    return RH

def calculate_heat_index(T_f, RH):
    """
    NWS Rothfusz regression
    """
    if pd.isnull(T_f) or pd.isnull(RH):
        return np.nan

    HI_simple = 0.5 * (
        T_f + 61.0 
        + ((T_f - 68.0) * 1.2) 
        + (RH * 0.094)
    )
    
    if HI_simple < 80:
        return HI_simple
    
    
    HI_full = (
        -42.379
        + 2.04901523 * T_f
        + 10.14333127 * RH
        - 0.22475541 * T_f * RH
        - 0.00683783 * (T_f ** 2)
        - 0.05481717 * (RH ** 2)
        + 0.00122874 * (T_f ** 2) * RH
        + 0.00085282 * T_f * (RH ** 2)
        - 0.00000199 * (T_f ** 2) * (RH ** 2)
    )
    
    if (RH < 13) and (80 <= T_f <= 112):
        adjustment = ((13 - RH) / 4) * math.sqrt((17 - abs(T_f - 95)) / 17)
        HI_full -= adjustment
    elif (RH > 85) and (80 <= T_f <= 87):
        adjustment = ((RH - 85) / 10) * ((87 - T_f) / 5)
        HI_full += adjustment
    
    return HI_full

###############################################################################
#                        Read ERCOT solar and wind
###############################################################################
# Wind
wind_data = pd.read_excel('Texas_Wind_240708.xlsx')
# Solar
solar_data = pd.read_excel('Texas_Solar_240708.xlsx')


wind_data['datetime'] = pd.to_datetime(wind_data['DELIVERY_DATE']) + \
                        pd.to_timedelta(wind_data['HOUR_ENDING'], unit='h')
solar_data['datetime'] = pd.to_datetime(solar_data['DELIVERY_DATE']) + \
                         pd.to_timedelta(solar_data['HOUR_ENDING'], unit='h')


start_date = '2024-07-07'
end_date   = '2024-07-17'
wind_filtered = wind_data[
    (wind_data['datetime'] >= start_date) &
    (wind_data['datetime'] <= end_date)
].copy()
solar_filtered = solar_data[
    (solar_data['datetime'] >= start_date) &
    (solar_data['datetime'] <= end_date)
].copy()


merged_data = pd.merge(
    wind_filtered[['datetime', 'COP_HSL_SYSTEM_WIDE']],
    solar_filtered[['datetime', 'COP_HSL_SYSTEM_WIDE']],
    on='datetime',
    suffixes=('_wind', '_solar')
)


merged_data['total_output'] = merged_data['COP_HSL_SYSTEM_WIDE_wind'] + merged_data['COP_HSL_SYSTEM_WIDE_solar']

###############################################################################
#                          Read NOAA data
###############################################################################
file_path = '72243612906.csv'  
noaa_data = pd.read_csv(file_path, low_memory=False)

# datetime
noaa_data['DATE'] = pd.to_datetime(noaa_data['DATE'], errors='coerce')


noaa_data['TMP_C'] = clean_temperature_column_celsius(noaa_data['TMP'])
noaa_data['DEW_C'] = clean_temperature_column_celsius(noaa_data['DEW'])


noaa_data['TMP_F'] = noaa_data['TMP_C'].apply(c2f)
noaa_data['DEW_F'] = noaa_data['DEW_C'].apply(c2f)


filtered_data = noaa_data[
    (noaa_data['DATE'] >= start_date) &
    (noaa_data['DATE'] <= end_date)
].copy()

# Relative Humidity
filtered_data['RH'] = filtered_data.apply(
    lambda row: calculate_relative_humidity(row['TMP_F'], row['DEW_F']),
    axis=1
)


filtered_data['Heat_Index_F'] = filtered_data.apply(
    lambda row: calculate_heat_index(row['TMP_F'], row['RH']),
    axis=1
)


filtered_data['Heat_Index_C'] = filtered_data['Heat_Index_F'].apply(f2c)

###############################################################################
#                                figure
###############################################################################

rcParams.update({
    'font.size': 16,          
    'axes.labelsize': 20,     
    'xtick.labelsize': 18,    
    'ytick.labelsize': 18,    
    'legend.fontsize': 18,    
    'axes.titlesize': 20,     
    'font.family': 'sans-serif',  
    'font.sans-serif': ['Arial', 'Helvetica']
})


fig, ax_left = plt.subplots(figsize=(10, 8))

# ======================== Left: solar + wind  =========================
colors = ['#79B4B0', '#FFCC3F']
ax_left.stackplot(
    merged_data['datetime'],
    merged_data['COP_HSL_SYSTEM_WIDE_wind'],
    merged_data['COP_HSL_SYSTEM_WIDE_solar'],
    labels=['Wind', 'Solar'],
    colors=colors,
    alpha=0.8
)


ax_left.plot(
    merged_data['datetime'],
    merged_data['total_output'],
    color='black',
    linewidth=2,
    linestyle='-',
    label='Total Output'
)


ax_left.set_ylabel('Maximum potential of renewable generation (MW)', labelpad=10)


ax_left.xaxis.set_major_locator(mdates.DayLocator(interval=1))
ax_left.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
plt.setp(ax_left.get_xticklabels(), rotation=45, ha="right")


ax_left.yaxis.set_major_locator(MaxNLocator(integer=True))


ax_left.set_ylim([0, 43000])



ax_left.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), frameon=False, ncol=4)

# ======================== Right y axis - Heat Index =======================
ax_right = ax_left.twinx()


ax_right.plot(
    filtered_data['DATE'],
    filtered_data['Heat_Index_F'],  
    color='red',
    linewidth=2,
    linestyle='-',
    label='Heat Index (°F)'
)



ax_right.set_ylim([0, 110])


ax_right.yaxis.set_major_locator(ticker.MultipleLocator(10))



ax_right.set_ylabel('Heat index (°F)', color='red', labelpad=10)
ax_right.tick_params(axis='y', labelcolor='red') 


lines_left, labels_left = ax_left.get_legend_handles_labels()
lines_right, labels_right = ax_right.get_legend_handles_labels()
lines = lines_left + lines_right
labels = labels_left + labels_right
ax_left.legend(
    lines,
    labels,
    loc='upper center',
    bbox_to_anchor=(0.5, 1.1),
    frameon=False,
    ncol=4
)


ax_right.set_xlim(ax_left.get_xlim())




plt.tight_layout()



plt.show()

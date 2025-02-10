import datetime as dt
import logging
import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns



logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

data_dir = Path("./")
dataset_name = "tempo_simple"

def is_partitioned(filepath):
    for p in filepath.iterdir():
        if p.is_dir() and ("=" in p.stem) and (len(p.stem.split("=")) == 2):
            return True
    return False

def get_partitions(filepath):
    assert is_partitioned(filepath), f"{filepath} is not partitioned"
    
    partition_name = None
    for p in filepath.iterdir():
        if p.is_dir() and ("=" in p.stem):
            tmp, value = p.stem.split("=")
            if partition_name:
                assert (tmp == partition_name), f"Found two different partition names in {filepath}: {partition_name}, {tmp}"
            partition_name = tmp
            yield partition_name, value, p

def print_partitions(filepath, print_depth=2, _depth=0):
    if is_partitioned(filepath):
        space = ' ' * 4 * _depth
        for partition_name, value, p in get_partitions(filepath):
            print(f"{space}{partition_name}={value}")
        if (not print_depth) or ((_depth + 1) < print_depth):
            print_partitions(p, print_depth=print_depth, _depth=_depth+1)
            
def get_metadata(dataset_path):
    with open(dataset_path / "metadata.json") as f:
        result = json.load(f)
    return result

# load metadata and get column names by type
metadata = get_metadata(data_dir / dataset_name)
assert metadata["table_format"]["format_type"] == "unpivoted", metadata["table_format"]
value_column = metadata["table_format"]["value_column"]
columns_by_type = {dim_type: metadata["dimensions"][dim_type][0]["column_names"][0] 
                   for dim_type in metadata["dimensions"] if metadata["dimensions"][dim_type]}

# Load data table
filepath = data_dir / dataset_name / "table.csv"
if not filepath.exists():
    filepath = data_dir / dataset_name / "table.parquet"

if filepath.suffix == ".csv":
    kwargs = { 
        "dtype": { columns_by_type['model_year']: str }
    }
    if columns_by_type['time'] == "time_est": 
        kwargs["parse_dates"] = ["time_est"]
        
    df = pd.read_csv(filepath, **kwargs) 
else:  
    df = pd.read_parquet(filepath)
    
logger.info(f"df.dtypes = \n{df.dtypes}")
df.head(5)





df2 = (df.groupby(["scenario", columns_by_type["model_year"]])[value_column].sum() / 1.0E6).reset_index()
df2.rename({columns_by_type["model_year"]: "year", value_column: "annual_twh"}, axis=1, inplace=True)
df2["scenario"] = df2["scenario"].map({
    "efs_high_ldv": "EFS High Electrification",
    "ldv_sales_evs_2035": "All LDV Sales EV by 2035",
    "reference": "AEO Reference"
})





# State  Texas
df_tx = df[df['state'] == 'TX']


df_tx['time_est'] = pd.to_datetime(df_tx['time_est'])


df_tx_july =  df_tx[df_tx['time_est'].dt.month.isin([6, 7, 8, 9, 10, 11])]
#df_tx[(df_tx['time_est'].dt.month == 7) & (df_tx['tempo_project_model_years'] == 2050)]


print(f"Filtered TX data:\n{df_tx.head()}")
print(f"Filtered TX July data:\n{df_tx_july.head()}")



# Select scenario as 'efs_high_ldv'
df_tx_july_efs_high_ldv = df_tx_july[df_tx_july['scenario'] == 'efs_high_ldv' ]

print(f"Filtered TX July data for efs_high_ldv scenario:\n{df_tx_july_efs_high_ldv.head()}")




unique_years = df_tx_july_efs_high_ldv['tempo_project_model_years'].unique()


yearly_dataframes = {}

for year in unique_years:
    df_year = df_tx_july_efs_high_ldv[df_tx_july_efs_high_ldv['tempo_project_model_years'] == year]
    yearly_dataframes[f'df_{year}'] = df_year
    print(f"Created DataFrame for the year {year} with {len(df_year)} rows.")



df_2050 = yearly_dataframes['df_2050']
print(df_2050.head())




summed_yearly_dataframes = {}


for year in unique_years:
    df_year = df_tx_july_efs_high_ldv[df_tx_july_efs_high_ldv['tempo_project_model_years'] == year]
    
    
    df_summed = df_year.groupby('time_est')['value'].sum().reset_index()
    
    summed_yearly_dataframes[f'summed_df_{year}'] = df_summed
    
    print(f"Created summed DataFrame for the year {year} with {len(df_summed)} rows.")

summed_df_2050 = summed_yearly_dataframes['summed_df_2050']
print(summed_df_2050.head())




sns.set(style="ticks")

all_years_df = pd.DataFrame()

for year in unique_years:
    key = f'summed_df_{year}'
    if key in summed_yearly_dataframes:
        df_summed = summed_yearly_dataframes[key]
        df_summed['year'] = year  # Add a column for the year
        all_years_df = pd.concat([all_years_df, df_summed], axis=0)
    else:
        print(f"Key {key} not found in summed_yearly_dataframes.")


from matplotlib import rcParams

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

if not all_years_df.empty:
    plt.figure(figsize=(10, 8))
    
    ax = sns.boxplot(x='year', y='value', data=all_years_df, palette="viridis", showmeans=True, showfliers=False,
                     meanprops={"marker":"o", "markerfacecolor":"white", "markeredgecolor":"black", "markersize":"7"},
                     boxprops=dict(alpha=.7))
    
    ax.set_xlabel('Year', fontsize=20, labelpad=10)
    ax.set_ylabel('EV charging demand (MW)', fontsize=20, labelpad=10)
    
    ax.set_axisbelow(True)
    plt.xticks(rotation=45, fontsize=20)
    plt.yticks(fontsize=20)
    
    plt.tight_layout()
    # Save the figure
    #plt.savefig('EV_Charging_Demand_Hurricane_Season.png', dpi=600)

    plt.show()
else:
    print("No data to plot.")



#################################################################### flexibility


# daily average
average_demand_2050 = df_summed['value'].mean()

# distinguish bev and phev
df_2050['type'] = df_2050['subsector'].apply(lambda x: 'bev' if 'bev' in x else 'phev')

#
df_2050_bev = df_2050[df_2050['type'] == 'bev'].groupby('time_est')['value'].sum().reset_index()
df_2050_phev = df_2050[df_2050['type'] == 'phev'].groupby('time_est')['value'].sum().reset_index()


bev_daily_max = df_2050_bev.groupby(df_2050_bev['time_est'].dt.date)['value'].max().reset_index()
phev_daily_max = df_2050_phev.groupby(df_2050_phev['time_est'].dt.date)['value'].max().reset_index()


merged_daily_max = pd.merge(bev_daily_max, phev_daily_max, on='time_est', suffixes=('_bev', '_phev'))

# bev_daily_max / (bev_daily_max + phev_daily_max)
merged_daily_max['ratio'] = merged_daily_max['value_bev'] / (merged_daily_max['value_bev'] + merged_daily_max['value_phev'])


bev_percent = merged_daily_max['ratio'].mean()

print(f"BEV/(BEV + PHEV) : {bev_percent }")

N_vehicle = 25796600  # Vehicle number in Texas  https://afdc.energy.gov/vehicle-registration
Energy_EFS = 59.118 # TWh
Energy_AllEV = 78.645 #TWh

EV_percent = Energy_EFS/Energy_AllEV

N_EV = int(N_vehicle*EV_percent)

participate = 0.1 # percentage of pariticpation


df_2050_bev['num_charge'] = ((df_2050_bev['value']*1000 / (0.95 * 7.2 + 0.05 * 1.4))) 

df_2050_bev['num_nocharge'] = (bev_percent * N_EV - (df_2050_bev['value']*1000 / (0.95 * 7.2 + 0.05 * 1.4))) 

df_2050_bev['flex'] = (bev_percent * N_EV - (df_2050_bev['value']*1000 / (0.95 * 7.2 + 0.05 * 1.4)))  *  (0.95 * 0.0072) * participate

df_2050_bev['net_flex'] = df_2050_bev['flex'] - df_2050_bev['value']#net_flex = flex- value




sns.set_style("ticks")


plt.figure(figsize=(10, 8))
sns.boxplot(data=df_2050_bev['flex'], color='lightblue', linewidth=2.5, width=0.3)


plt.ylim(8800, 11000)


plt.ylabel('Power (MW)', fontsize=20)
plt.xlabel('BEV Potential Flexibility', fontsize=20)




#plt.grid(True, linestyle='--', alpha=0.7)
plt.xticks([])
plt.yticks(fontsize=18)

plt.tight_layout()
plt.show()




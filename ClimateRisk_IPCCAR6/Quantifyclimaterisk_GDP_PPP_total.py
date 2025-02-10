import pandas as pd

# Load the dataset
file_path_loss_data = './WMO_LossData_mapping.csv'
loss_data_df = pd.read_csv(file_path_loss_data)

# Total loss for each WMO_Region
wmo_region_losses = {
    'AFRICA_WMO': 38.5,
    'ASIA_WMO': 1200,
    'SOUTH AMERICA': 100.9,
    'North America Central America and the Caribbean': 1700,
    'SOUTH-WEST PACIFIC': 163.7,
    'EUROPE': 476.5
}

def calculate_weighted_losses(df, region_losses):
    event_columns = df.columns[1:] 
    
    weighted_losses_df = df[['WMO_Region']].copy()
    
    for event in event_columns:
        weighted_losses_df[event + '_Loss'] = df.apply(
            lambda row: row[event] * region_losses.get(row['WMO_Region'], 0) if pd.notnull(row[event]) else 0, axis=1
        )
    
    return weighted_losses_df

weighted_losses_df = calculate_weighted_losses(loss_data_df, wmo_region_losses)

weighted_losses_df.to_csv('./WMO_LossData_Weighted_Losses_by_Event.csv', index=False)

print(weighted_losses_df.head())




########################### Calculate loss for each event in each WMO region

# Load the datasets
file_path_area_factors = './Risk_Relevance_factors_withGDP.csv'
#file_path_weighted_losses = './Step1_WMO_LossData_Weighted_Losses_by_Event_0928.csv'
area_factors_df = pd.read_csv(file_path_area_factors)
#weighted_losses_df = pd.read_csv(file_path_weighted_losses)

# Merge the weighted loss data with the area factors based on WMO_Region
merged_df = pd.merge(area_factors_df, weighted_losses_df, on='WMO_Region', how='left')

def distribute_losses_by_area(df):
    event_columns = df.columns[df.columns.str.endswith('_Loss')]  # Loss 
    result_df = df[['WMO_Region', 'Name', 'Area']].copy()
    
    for event in event_columns:
        event_proportion_column = event.replace('_Loss', '')
        
        result_df[event + '_Distributed'] = df[event] * df[event_proportion_column]
    
    return result_df

distributed_losses_df = distribute_losses_by_area(merged_df)

# Save the result to a CSV
#distributed_losses_df.to_csv('./Step2_Distributed_Losses_by_Area_0928.csv', index=False)
#distributed_losses_df.to_csv('./New_Distributed_Losses_by_Area.csv', index=False)
distributed_losses_df.to_csv('./Step2New_Distributed_Losses_by_Area_0928.csv', index=False)


print(distributed_losses_df.head())



###


# Load the dataset
file_path = './IPCC_ClimateRiskv3_revisegdp_240927v2.csv'
df = pd.read_csv(file_path)

confidence_mapping = {
    'H': 0.85,
    'M': 0.5,
    'DH': -0.85,
    'DM': -0.5
}

extreme_columns = df.columns[df.columns.get_loc('ExtremeHeat'):]

for col in extreme_columns:
    df[col] = df[col].map(confidence_mapping)

df.to_csv('./Step3_IPCC_ClimateRiskv3_revisegdp_240927v2_quantified.csv', index=False)



##################


# Load the CSV files
step3_file_path = './Step3_IPCC_ClimateRiskv3_revisegdp_240927v2_quantified.csv'
#step2_file_path = './Step2_Distributed_Losses_by_Area_0928.csv'
step2_file_path = './Step2New_Distributed_Losses_by_Area_0928.csv'

step3_df = pd.read_csv(step3_file_path)
step2_df = pd.read_csv(step2_file_path)

non_numeric_columns = step3_df.loc[:, :'ExtremeHeat']

step3_extremeheat_columns = step3_df.loc[:, 'ExtremeHeat':]
step2_extremeheat_columns = step2_df.loc[:, 'ExtremeHeat_Loss_Distributed':]

step2_extremeheat_columns.columns = step3_extremeheat_columns.columns

result_df = step3_extremeheat_columns * step2_extremeheat_columns

final_df = pd.concat([non_numeric_columns.iloc[:, :-1], result_df], axis=1)


output_file_path = './Step4New_Result_Matrix_Pointwise_Multiplication_with_metadata.csv'
final_df.to_csv(output_file_path, index=False)





############################# 
gdp_column = step3_df['GDP_billion']
weighted_result_df = result_df.div(gdp_column, axis=0)

final_weighted_df = pd.concat([non_numeric_columns.iloc[:, :-1], weighted_result_df], axis=1)

final_weighted_df['TotalRiskbyGDP'] = final_weighted_df.loc[:, 'ExtremeHeat':].sum(axis=1)


final_weighted_df_filtered = final_weighted_df.iloc[:, :9].copy()
final_weighted_df_filtered['TotalRiskbyGDP'] = final_weighted_df['TotalRiskbyGDP']

output_file_path = './Step5New_Final_Weighted_Matrix_by_GDP.csv'
final_weighted_df_filtered.to_csv(output_file_path, index=False)

filtered_by_oid_df = final_weighted_df[step3_df['OID_'] <= 43] # only select land region

percentile_30 = filtered_by_oid_df['TotalRiskbyGDP'].quantile(0.30)
percentile_70 = filtered_by_oid_df['TotalRiskbyGDP'].quantile(0.70)











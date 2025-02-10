import pandas as pd

# Load the dataset
file_path = './RiskRelevance_240928_GDP.csv'
df = pd.read_csv(file_path)

def calculate_event_proportion_all(df):
    extreme_event_columns = df.columns[df.columns.get_loc('ExtremeHeat'):]

    proportions = {}

    for event_column in extreme_event_columns:
        
        relevant_df = df[df[event_column] != 'N'].copy()

        if not relevant_df.empty:
            region_area_sums = relevant_df.groupby('WMO_Region')['Area'].sum().reset_index()
            region_area_sums.columns = ['WMO_Region', 'Total_Area_Affected']

            relevant_df = relevant_df.merge(region_area_sums, on='WMO_Region', how='left')

            relevant_df[f'{event_column}_Proportion'] = relevant_df['Area'] / relevant_df['Total_Area_Affected']

            proportions[event_column] = relevant_df[['WMO_Region', 'Name', 'Area', f'{event_column}_Proportion']]

    final_df = df[['WMO_Region', 'Name', 'Area']].copy()
    for event_column, result in proportions.items():
        final_df = final_df.merge(result, on=['WMO_Region', 'Name', 'Area'], how='left')

    return final_df

all_events_proportion_df = calculate_event_proportion_all(df)


all_events_proportion_df.to_csv('./Risk_Relevance_factors_withGDP.csv', index=False)

print(all_events_proportion_df.head())
import pandas as pd


electrification_rate_df = pd.read_csv('./Final_electrification_rate.csv')
#electrification_rate_df = pd.read_csv('./Final_electrification_rate_addmissing.csv')
region_to_country_df = pd.read_excel('./Region_to_Country.xlsx')


country_electrification_df = pd.DataFrame()


for index, row in region_to_country_df.iterrows():
    region = row['GCAM Region']
    countries = row['Countries'].split(', ')
    rate_data = electrification_rate_df[electrification_rate_df['region'] == region]


    for country in countries:
        country_data = rate_data.copy()
        country_data['country'] = country
        country_data.drop('region', axis=1, inplace=True)
        country_data.rename(columns=lambda x: x.strip(), inplace=True)
        country_electrification_df = pd.concat([country_electrification_df, country_data])


country_electrification_df.reset_index(drop=True, inplace=True)

country_electrification_df.to_csv('./country_electrification_rates.csv', index=False)
#country_electrification_df.to_csv('./country_electrification_rates_addmissing.csv', index=False)

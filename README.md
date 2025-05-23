# Cross-Sector Energy System Resilience and Interdependence in a Changing Climate

This repository contains the code and data used to generate the figures in the paper "Cross-Sector Energy System Resilience and Interdependence in a Changing Climate."



## Global electrification and intensifying climate change risks at the sub-national scale

Electrification projection is based on the Global Change Analysis Model (GCAM) v7.1 (https://jgcri.github.io/gcam-doc/toc.html) [R1].  To map regional results to country-level outputs, run:

Run ./GCAM/Python_GCAM_regiontocountry.py

Climate change risks are characterized by composite confidence levels of the projected intensification of climate impact drivers (CIDs) affecting energy infrastructure across all climatologically consistent land regions worldwide, as defined by IPCC AR6.

Run ./ClimateRisk_IPCCAR6/Risk_Relevance_Calculation_GDP.py

Then run ./ClimateRisk_IPCCAR6/Quantifyclimaterisk_GDP_PPP_total.py to quantify risk values for each IPCC-defined land region.



## Hurricane Intensification

Projections for tropical cyclone intensity in Texas under the current climate scenario (green), moderate emission scenario (SSP2-4.5, blue), and high emission scenario (SSP5-8.5, red) by the late 21st century. Wind intensity is calculated at Galveston, Texas. Colored scatter points represent individual samples of the wind intensity (m/s) for each synthetic tropical cyclone that makes landfall in Texas under the corresponding climate scenario. The solid curves, with shaded regions indicating uncertainty, show the statistical fitting using the Generalized Pareto Distribution (GPD) for extreme wind intensities (90th percentile) in each scenario. Each climate scenario presents the return period of synthetic tropical cyclone [R2] projected by downscaling the ensemble of six Coupled Model Intercomparison Project Phase 6 (CMIP6) general circulation models (GCMs), including CanESM5, CNRM-CM6-1, EC-Earth3, IPSL-CM6A-LR, MIROC6, and UKESM1-0-LL.

Run ./Hurricane_Texas/Plot_GDP_ReturnPeriod.py



## Hurricane Beryl

Maximum potential of wind and solar generation and the associated heat index in Texas during Hurricane Beryl from July 7th to July 17th, 2024. The maximum generation potential for renewables is recorded hourly by the Electric Reliability Council of Texas [R3]. The heat index is calculated using air temperature and dew point temperature data recorded by the Houston Ellington AFB station, sourced from NOAA’s Global Hourly Integrated Surface Database (https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database). To obtain the result, run:

./HurricaneBeryl/Plot_WindSolar_HeatIndex.py





## Transportation

Projections of electric vehicle (EV) charging demand in Texas from 2024 to 2050 are presented in this module. The analysis includes boxplots representing hourly charging profiles for light-duty passenger EVs during the hurricane season (June to November) for each year. These profiles are derived from the Transportation Energy & Mobility Pathway Options (TEMPO) model under a high electrification scenario. To generate the boxplot visualization,  run

./Transportation_Texas/tempo_data_simple_tx_boxplot.py



## References

[R1] Pacific Northwest National Laboratory. Gcam: Global change analysis model v7.1 (2024). Available at: https://gcims.pnnl.gov/modeling/gcam-global-change-analysis-model.441

[R2] Xi, D., Lin, N. & Gori, A. Increasing sequential tropical cyclone hazards along the US East and Gulf coasts. Nature Climate Change 13, 258–265 (2023)

[R3] ERCOT. Grid and market conditions. https://www.ercot.com/gridmktinfo/dashboards

[R4] National Renewable Energy Laboratory (NREL). Tempo: Transportation energy & mobility pathway
options model (2022). https://www.nrel.gov/transportation/tempo-model.html.



## License

This project is licensed under the MIT License.

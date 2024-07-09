# Import pandas
import pandas as pd
import geopandas as gpd

# American Community Survey Racial Data 2013-2022
bg2013 = pd.read_csv('Data/ACSDT5Y2013.B03002-Data.csv')
bg2014 = pd.read_csv('Data/ACSDT5Y2014.B03002-Data.csv')
bg2015 = pd.read_csv('Data/ACSDT5Y2015.B03002-Data.csv')
bg2016 = pd.read_csv('Data/ACSDT5Y2016.B03002-Data.csv')
bg2017 = pd.read_csv('Data/ACSDT5Y2017.B03002-Data.csv')
bg2018 = pd.read_csv('Data/ACSDT5Y2018.B03002-Data.csv')
bg2019 = pd.read_csv('Data/ACSDT5Y2019.B03002-Data.csv')
bg2020 = pd.read_csv('Data/ACSDT5Y2020.B03002-Data.csv')
bg2021 = pd.read_csv('Data/ACSDT5Y2021.B03002-Data.csv')
bg2022 = pd.read_csv('Data/ACSDT5Y2022.B03002-Data.csv')
import pandas as pd

# Function to Clean CSV
def clean_csv(df, year):
    df = df.iloc[1:]
    df['GEO_ID'] = df['GEO_ID'].str[9:]
    df = df[['GEO_ID', 'B03002_001E', 'B03002_003E', 'B03002_004E', 'B03002_005E', 'B03002_006E', 'B03002_007E', 'B03002_008E', 'B03002_009E', 'B03002_012E']]
    df.rename(columns={
        'B03002_001E': 'Total Population',
        'B03002_003E': 'White Population',
        'B03002_004E': 'Black Population',
        'B03002_006E': 'Asian Population',
        'B03002_012E': 'Hispanic or Latino Population'
    }, inplace=True)
    df['Some other race'] = df['B03002_008E'].astype(float) + df['B03002_009E'].astype(float) + df['B03002_005E'].astype(float) + df['B03002_007E'].astype(float)
    df.drop(columns=['B03002_008E', 'B03002_009E','B03002_005E', 'B03002_007E' ], inplace=True)
    int_columns = ['Total Population', 'White Population', 'Black Population',
                   'Asian Population', 
                   'Hispanic or Latino Population', 'Some other race']
    df[int_columns] = df[int_columns].astype(int)
    df['Year'] = year
    return df

# List of DataFrames with corresponding years
dfs_with_years = [
    (bg2013, 2013), (bg2014, 2014), (bg2015, 2015), (bg2016, 2016),
    (bg2017, 2017), (bg2018, 2018), (bg2019, 2019), (bg2020, 2020),
    (bg2021, 2021), (bg2022, 2022)
]

df_2010s = pd.DataFrame()
df_2020s = pd.DataFrame()
for df, year in dfs_with_years:
    cleaned_df = clean_csv(df, year)
    if year <= 2019:
        df_2010s = pd.concat([df_2010s, cleaned_df])
    else:
        df_2020s = pd.concat([df_2020s, cleaned_df])

# Read shapefiles
shapefile_2019 = gpd.read_file('Data/NC_blck_grp_2019.shp')
shapefile_2023 = gpd.read_file('Data/NC_blck_grp_2022.shp')

# Merge the 2010s data with the 2019 shapefile
merged_2010s = pd.merge(shapefile_2019, df_2010s, left_on='GEOID', right_on='GEO_ID', how='inner')

# Merge the 2020s data with the 2023 shapefile
merged_2020s = pd.merge(shapefile_2023, df_2020s, left_on='GEOID', right_on='GEO_ID', how='inner')

# Convert merged DataFrames to GeoDataFrames
gdf_2010s = gpd.GeoDataFrame(merged_2010s, geometry=merged_2010s.geometry)
gdf_2020s = gpd.GeoDataFrame(merged_2020s, geometry=merged_2020s.geometry)

# save new shapefiles
gdf_2010s.to_file('merged_2010s.shp')
gdf_2020s.to_file('merged_2020s.shp')

# Import pandas
import pandas as pd

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

# Function to Clean
def clean_csv(df, year):
    
    # Drop the first row
    df = df.iloc[1:]

    # Remove first 9 values from GEO_ID
    df['GEO_ID'] = df['GEO_ID'].str[9:]

    # Keep only Racial Columns + Rename
    df = df[['GEO_ID', 'B03002_001E', 'B03002_003E', 'B03002_004E', 'B03002_005E', 'B03002_006E', 'B03002_007E', 'B03002_008E', 'B03002_009E', 'B03002_012E']]
    df.rename(columns={
        'B03002_001E': 'Total Population',
        'B03002_003E': 'White Population',
        'B03002_004E': 'Black Population',
        'B03002_005E': 'American Indian Population',
        'B03002_006E': 'Asian Population',
        'B03002_007E': 'Native Hawaiian and Other Pacific Islander Population',
        'B03002_012E': 'Hispanic or Latino Population'
    }, inplace=True)

    # Consolidate extra race data
    df['Some other race'] = df['B03002_008E'].astype(float) + df['B03002_009E'].astype(float)

    # Drop columns used to consolidate
    df.drop(columns=['B03002_008E', 'B03002_009E'], inplace=True)

    # Convert columns to integers
    int_columns = ['Total Population', 'White Population', 'Black Population', 'American Indian Population',
                   'Asian Population', 'Native Hawaiian and Other Pacific Islander Population', 
                   'Hispanic or Latino Population', 'Some other race']
    df[int_columns] = df[int_columns].astype(int)
    
    # Add the year column
    df['Year'] = year

    return df

# List of DataFrames with corresponding years
dfs_with_years = [
    (bg2013, 2013), (bg2014, 2014), (bg2015, 2015), (bg2016, 2016),
    (bg2017, 2017), (bg2018, 2018), (bg2019, 2019), (bg2020, 2020),
    (bg2021, 2021), (bg2022, 2022)
]

# There is two different shapefile one for the 2010's and one for the 2020's, so create two DF to house year/race info
df_2010s = pd.DataFrame()
df_2020s = pd.DataFrame()
for df, year in dfs_with_years:
    cleaned_df = clean_csv(df, year)
    if year <= 2019:
        df_2010s = pd.concat([df_2010s, cleaned_df])
    else:
        df_2020s = pd.concat([df_2020s, cleaned_df])

# Test
print("Processed 2013-2019 DataFrame:")
print(df_2010s.head())
print("Processed 2020-2022 DataFrame:")
print(df_2020s.head())

# Export df_2010s to a CSV file
df_2010s.to_csv('processed_2010s_data.csv', index=False)

# Export df_2020s to a CSV file
df_2020s.to_csv('processed_2020s_data.csv', index=False)
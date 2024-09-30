# import pandas library
import pandas as pd

# region STEP 1: IMPORT DATA
# load data from csv files and name the dataframes
# filter the datasets to return only needed columns
outcomes = pd.read_csv('seda_school_pool_cs_4.1-1.csv', usecols=['sedasch', 'cs_mn_avg_ol'])
covariates = pd.read_csv('seda_cov_school_pool_4.1-1.csv', 
                         usecols=['sedasch', 'stateabb', 'type', 'level', 'charter', 'magnet', 
                                  'urbanicity', 'locale', 'totenrl', 'perwht', 'pernam', 'perasn',
                                  'perhsp', 'perblk', 'perfl', 'perrl', 'gifted_flag', 'lep_flag', 
                                  'sped_flag', 'avgrdall'])
characteristics = pd.read_csv('Public_School_Characteristics_2017-18-1.csv', 
                              usecols=['NCESSCH', 'GSLO', 'GSHI', 'VIRTUAL', 'TOTAL', 'STUTERATIO',
                                       'STITLEI', 'TOTMENROL', 'TOTFENROL'])
poverty = pd.read_csv('Poverty_Data_2017-18-1.csv', usecols=['NCESSCH', 'IPR_EST'])
# endregion

# region STEP 2: INSPECT DATA SIZE
# use head() function to get the first five rows of each dataframe -> dataframe
# use shape property to get the size of each dataframe -> tuple(numbers of rows, number of columns)
'''
print(outcomes.head())
print(outcomes.shape)
print(covariates.head())
print(covariates.shape)
print(characteristics.head())
print(characteristics.shape)
print(poverty.head())
print(poverty.shape)
'''
# endregion

# region STEP 3: RENAME COLUMNS
# change all column names in characteristics and poverty to lowercase
characteristics.columns = characteristics.columns.str.lower()
poverty.columns = poverty.columns.str.lower()
# change column names ncessch -> sedasch in characteristics and poverty
characteristics.rename(columns={'ncessch':'sedasch'}, inplace=True)
poverty.rename(columns={'ncessch':'sedasch'}, inplace=True)
# endregion

# region STEP 4: MERGE DATAFRAMES
df = outcomes.merge(characteristics, on='sedasch').merge(covariates, on='sedasch').merge(poverty, on='sedasch')
#df.to_csv('df_temp1.csv', index=False)
#print(df.shape) 
#print(df.dtypes)
# endregion

# region STEP 5: INSPECT VARIABLES
# use for-loop to distinguish between numerical and categorical variables
# if the column is categorical, use unique() and value_counts() to do descriptive statistics
# else, if the column is numerical, use describe() to do descriptive statistics
'''
for col,data in df.items():
    if col!= 'sedasch' and pd.api.types.is_numeric_dtype(data):
        print(col + ' - numeric')
        print(data.describe())
    else:
        print(col + ' - categorical')
        print(data.unique())
        print(data.value_counts())
'''
# endregion

# region STEP 6: COUNT AND REPLACE MISSING VALUES
# use dictionary to record missing values
'''
missing_value_dic = {}

for col, data in df.items():
    i = 0
    if col == 'virtual' or col == 'stitlei':
        # For the 'virtual' column, count the number of 'Missing'
        for value in data:
            if value == 'Missing':
                i += 1
    else:
        # For other columns, count empty strings or missing values (NaN)
        for value in data:
            if value == '' or pd.isna(value):
                i += 1
    missing_value_dic[col] = i

# Output the result
print(missing_value_dic)

'''
# endregion

# region STEP 7: CREATE MISSING_DATA DATAFRAME
'''
df_missing = pd.DataFrame()

# Loop through each row in the DataFrame
for index, row in df.iterrows():
    # Check if the value in the 'cs_mn_avg_ol' column is ''
    if pd.isna(row['cs_mn_avg_ol']):
        # Append the row to the new DataFrame
        df_missing = pd.concat([df_missing, row.to_frame().T], ignore_index=True)

# Output the new DataFrame to csv
#print(df_missing)
df_missing.to_csv('df_missing.csv', index=False)
'''
# endregion

# region STEP 8: DELETE THE MISSING DATA

# reflection: maybe it's not appropriate to delete the missing data just by deleting
# NaN values, because some values are typed as MISSING but they are not NaN ...
df = df.dropna()
print(df.shape)
#df.to_csv('df_temp1.csv', index=False)

# endregion

# region STEP 9: DELETE DATA WHEN GSHI='N'
#df_N = pd.DataFrame()
index_to_delete = []

# Loop through each row in the DataFrame
for index, row in df.iterrows():
    # Check if the value in the 'cs_mn_avg_ol' column is ''
    if row['gslo'] == 'N ' or row['gshi'] == 'N ':
        # Append the row to the new DataFrame
        #df_N = pd.concat([df_N, row.to_frame().T], ignore_index=True)
        index_to_delete.append(index)

# Delete the rows from the original DataFrame
df = df.drop(index_to_delete)

# Output the new DataFrame to csv
#df_N.to_csv('df_n.csv', index=False)
# endregion

# region: STEP 10: CREATE COLUMNS

# Calculate the proportion of male enrollment as 'permale'
# Use the total male enrollment divided by the sum of male and female enrollment
# If the total enrollment is greater than 0, otherwise set to 0
df['permale'] = df.apply(lambda x: x.totmenrol/(x.totmenrol + x.totfenrol) if x.totmenrol + x.totfenrol > 0 else 0, axis=1)

# Calculate the proportion of female enrollment as 'perfemale'
# Use the total female enrollment divided by the sum of male and female enrollment
# If the total enrollment is greater than 0, otherwise set to 0
df['perfemale'] = df.apply(lambda x: x.totfenrol/(x.totmenrol + x.totfenrol) if x.totmenrol + x.totfenrol > 0 else 0, axis=1)

# Calculate the total percentage of urban population as 'perurm'
# Sum the percentages of different urban demographic groups: 'pernam', 'perhsp', and 'perblk'
df['perurm'] = df.apply(lambda x: x.pernam + x.perhsp + x.perblk, axis=1)

# Calculate the total percentage of non-urban population as 'pernonurm'
# Sum the percentages of different non-urban demographic groups: 'perwht' and 'perasn'
df['pernonurm'] = df.apply(lambda x: x.perwht + x.perasn, axis=1)
# endregion

# region: STEP 11: FILTER THE DATAFRAME
# reflection: outliers also could be defined as the data is larger than 1.5IQR+Q3 or smaller than Q1-1.5IQR    
df_filtered = df.drop(df[
    (df['type'] == 'Other/Alt School') |
    (df['type'] == 'Vocational School') |
    (df['level'] == 'Other') |
    (df['charter'] == 1) |
    (df['magnet'] == 1) |
    (df['virtual'] == 'A virtual school') |
    (df['virtual'] == 'Missing')
].index)

for col, data in df_filtered.items():
    if col!= 'sedasch' and pd.api.types.is_numeric_dtype(data):
        lower_fence = data.quantile(0.05)
        upper_fence = data.quantile(0.95)
        for item in data:
            if(item < lower_fence or item > upper_fence):
                df_filtered.drop(df_filtered[df_filtered[col] == item].index, inplace=True)
            
# output the dataframe to csv file
df_filtered.to_csv('seda_plus.csv', index=False)
# endregion
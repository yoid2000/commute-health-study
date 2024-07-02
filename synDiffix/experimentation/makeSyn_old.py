import pandas as pd
import os
from syndiffix import Synthesizer
from syndiffix.clustering.strategy import MlClustering

inFile = 'CommDataOrig.csv'

colConfig = {
    'VO2max': 'float',
    'CommToSch': 'str',
    'CommHome': 'str',
    'gender': 'str',
    'age': 'float',
    'MVPAsqrt': 'float',
    'DistFromHome': 'int',
    'DistFromSchool': 'int',
}

max_weight = 15         # default = 15
cluster_params = {
    'max_weight':22,       #15
    'sample_size':2000,        #1000
    'merge_threshold':0.075        #0.1
}

# Read in file CommData.csv as dataframe, and set the column types according to the colConfig dictionary
df = pd.read_csv(inFile, dtype=colConfig)
print(df.columns)

# Seems that DistFromHome and DistFromSchool columns are not used
# Though note that by removing them, we data quality basicly didn't change!
# (which is good news, actually)
requiredColumns = ["VO2max","CommToSch","CommHome","gender","age","MVPAsqrt",]
allColumns = requiredColumns + ["DistFromHome","DistFromSchool"]
toSchoolColumns = ["VO2max","CommToSch","gender","age","MVPAsqrt"]
toHomeColumns = ["VO2max","CommHome","gender","age","MVPAsqrt"]

# Ok, turns out that the DistFromHome and DistFromSchool columns are not the same. 
diff_count = df['DistFromHome'].ne(df['DistFromSchool']).sum()
print(f"Number of rows where DistFromHome and DistFromSchool are different: {diff_count}")
# diff_rows = df[df['DistFromHome'].ne(df['DistFromSchool'])]
# print(diff_rows.head(5))

print("Original data counts:")
print(df.groupby(['gender', 'CommToSch']).size())
print(df.groupby(['gender', 'CommHome']).size())

# Generate a targeted synthetic dataset with all columns
syn_all = Synthesizer(df, clustering=MlClustering(target_column="VO2max", drop_non_features=False, max_weight=max_weight))
df_syn_all = syn_all.sample()
# Save the synthetic data to a new csv file called CommDataSyn.csv
df_syn_all.to_csv('CommDataSyn_target_VO2max_all.csv', index=False)
print("Synthetic data counts:")
print(df_syn_all.groupby(['gender', 'CommToSch']).size())
print(df_syn_all.groupby(['gender', 'CommHome']).size())

# Generate a targeted synthetic dataset with only the columns required for analysis
syn_req = Synthesizer(df[requiredColumns], clustering=MlClustering(target_column="VO2max", drop_non_features=False, max_weight=max_weight))
df_syn_req = syn_req.sample()
# Save the synthetic data to a new csv file called CommDataSyn.csv
df_syn_req.to_csv('CommDataSyn_target_VO2max_req.csv', index=False)
print("Synthetic data counts:")
print(df_syn_req.groupby(['gender', 'CommToSch']).size())
print(df_syn_req.groupby(['gender', 'CommHome']).size())

# Generate two targetted synthetic tables, each containinng only the columns needed for the
# specific communuting direction used in the analysis
syn_2school = Synthesizer(df[toSchoolColumns], clustering=MlClustering(target_column="VO2max", drop_non_features=True, max_weight=max_weight))
df_syn_2school = syn_2school.sample()
# Save the synthetic data to a new csv file c2schooled CommDataSyn.csv
df_syn_2school.to_csv('CommDataSyn_target_VO2max_2school.csv', index=False)

syn_2home = Synthesizer(df[toHomeColumns], clustering=MlClustering(target_column="VO2max", drop_non_features=False, max_weight=max_weight))
df_syn_2home = syn_2home.sample()
# Save the synthetic data to a new csv file c2homeed CommDataSyn.csv
df_syn_2home.to_csv('CommDataSyn_target_VO2max_2home.csv', index=False)

import pandas as pd
from syndiffix import Synthesizer
from syndiffix.clustering.strategy import MlClustering

colConfig = {
    'VO2max': 'float',
    'CommToSch': 'str',
    'CommHome': 'str',
    'gender': 'str',
    'age': 'float',
    'MVPAsqrt': 'float',
    'DistLog2Home': 'float',
    'DistLog2ToSch': 'float',
    'DistFromHome': 'int',
    'DistFromSchool': 'int',
}

cluster_params = {
    'max_weight':22,       #15
    'sample_size':2000,        #1000
    'merge_threshold':0.075        #0.1
}

# Read in file CommData.csv as dataframe, and set the column types according to the colConfig dictionary
df = pd.read_csv('CommData.csv', dtype=colConfig)
print(df.columns)

# Seems that DistFromHome and DistFromSchool columns are not used
# Though note that by removing them, we data quality basicly didn't change!
# (which is good news, actually)
requiredColumns = ["VO2max","CommToSch","CommHome","gender","age","MVPAsqrt","DistLog2Home","DistLog2ToSch",]
toSchoolColumns = ["VO2max","CommToSch","gender","age","MVPAsqrt","DistLog2ToSch",]
toHomeColumns = ["VO2max","CommHome","gender","age","MVPAsqrt","DistLog2Home",]

# Ok, turns out that the DistFromHome and DistFromSchool columns are not the same. 
diff_count = df['DistFromHome'].ne(df['DistFromSchool']).sum()
print(diff_count)
# diff_rows = df[df['DistFromHome'].ne(df['DistFromSchool'])]
# print(diff_rows.head(5))

# Remove the first column from df
df = df.drop(df.columns[0], axis=1)
print(df.columns)
print("Original data counts:")
print(df.groupby(['gender', 'CommToSch']).size())
print(df.groupby(['gender', 'CommHome']).size())

syn_all = Synthesizer(df[requiredColumns], clustering=MlClustering(target_column="VO2max", drop_non_features=False))
df_syn_all = syn_all.sample()
# Save the synthetic data to a new csv file called CommDataSyn.csv
df_syn_all.to_csv('CommDataSyn_target_VO2max_all.csv', index=True)
print("Synthetic data counts:")
print(df_syn_all.groupby(['gender', 'CommToSch']).size())
print(df_syn_all.groupby(['gender', 'CommHome']).size())

syn_2school = Synthesizer(df[toSchoolColumns], clustering=MlClustering(target_column="VO2max", drop_non_features=True))
df_syn_2school = syn_2school.sample()
# Save the synthetic data to a new csv file c2schooled CommDataSyn.csv
df_syn_2school.to_csv('CommDataSyn_target_VO2max_2school.csv', index=True)

syn_2home = Synthesizer(df[toHomeColumns], clustering=MlClustering(target_column="VO2max", drop_non_features=False))
df_syn_2home = syn_2home.sample()
# Save the synthetic data to a new csv file c2homeed CommDataSyn.csv
df_syn_2home.to_csv('CommDataSyn_target_VO2max_2home.csv', index=True)

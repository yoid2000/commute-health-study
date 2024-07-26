import pandas as pd
import json
import math
import os
from syndiffix import Synthesizer
from syndiffix.clustering.strategy import MlClustering
from syndiffix.clustering.strategy import SingleClustering
from syndiffix_tools.cluster_info import ClusterInfo

inFile = 'CommDataOrig.csv'
# Building synthetic data from the non-log distances is slightly better
# than using the log distances.
useLogDistances = False
if useLogDistances:
    dist2Sch = 'DistLogToSch'
    dist2Home = 'DistLogToHome'
else:
    dist2Sch = 'DistFromHome'
    dist2Home = 'DistFromSchool'

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

def custom_serializer(obj):
    return str(obj)  # Convert any custom type to string

def do_cluster_info(sdx, fileName):
    ci = ClusterInfo(sdx)
    stuff = {}
    stuff['cluster_info'] = ci.get_cluster_info()
    stuff['initial'] = sdx.clusters.initial_cluster
    stuff['derived'] = sdx.clusters.derived_clusters
    with open(fileName, 'w') as f:
        json.dump(stuff, f, default=custom_serializer, indent=4)

# Read in file CommData.csv as dataframe, and set the column types according to the colConfig dictionary
df = pd.read_csv(inFile, dtype=colConfig)
if useLogDistances:
    df[dist2Sch] = df['DistFromHome'].apply(lambda x: 0 if x == 0 else math.log(x))
    df[dist2Home] = df['DistFromSchool'].apply(lambda x: 0 if x == 0 else math.log(x))
    # delete column DistFromHome and DistFromSchool
    df.drop(columns=['DistFromHome', 'DistFromSchool'], inplace=True)

# Seems that DistFromHome and DistFromSchool columns are not used
# Though note that by removing them, we data quality basicly didn't change!
# (which is good news, actually)
requiredColumns = ["VO2max","CommToSch","CommHome","gender","age","MVPAsqrt",]
allColumns = requiredColumns + [dist2Sch,dist2Home]
toSchoolColumns = ["VO2max","CommToSch","gender","age","MVPAsqrt", dist2Sch]
toHomeColumns = ["VO2max","CommHome","gender","age","MVPAsqrt", dist2Home]

# Ok, turns out that the DistFromHome and DistFromSchool columns are not the same. 
diff_count = df[dist2Sch].ne(df[dist2Home]).sum()
print(f"Number of rows where DistFromHome and DistFromSchool are different: {diff_count}")
# diff_rows = df[df[dist2Sch].ne(df[dist2Home])]
# print(diff_rows.head(5))

print("Original data counts:")
print(df.groupby(['gender', 'CommToSch']).size())
print(df.groupby(['gender', 'CommHome']).size())

# Generate two targetted synthetic tables, each containinng only the columns needed for the
# specific communuting direction used in the analysis
syn_2school = Synthesizer(df[toSchoolColumns], clustering=MlClustering(target_column="VO2max", drop_non_features=False, max_weight=max_weight))
do_cluster_info(syn_2school, os.path.join('csvFiles', 'target_VO2max_2school.json'))
df_syn_2school = syn_2school.sample()
# Save the synthetic data to a new csv file c2schooled CommDataSyn.csv
df_syn_2school.to_csv(os.path.join('csvFiles', 'target_VO2max_2school.csv'), index=False)

syn_2home = Synthesizer(df[toHomeColumns], clustering=MlClustering(target_column="VO2max", drop_non_features=False, max_weight=max_weight))
df_syn_2home = syn_2home.sample()
# Save the synthetic data to a new csv file c2homeed CommDataSyn.csv
df_syn_2home.to_csv(os.path.join('csvFiles', 'target_VO2max_2home.csv'), index=False)
do_cluster_info(syn_2home, os.path.join('csvFiles', 'target_VO2max_2home.json'))

# Note that syndiffix determines the ordering of stitch columns itself.
# The order doesn't matter in this configuration
custom_clusters = [
    {  'name': 'cust1',
       'init2s': ["VO2max", "CommToSch", "gender", dist2Sch],
       'drv2s': [ {'owner': 'left', 'stitch': ["gender", "CommToSch", "VO2max"], 'derived':['age'], 'final': False},
       {'owner': 'left', 'stitch': ["gender", "CommToSch", "VO2max"], 'derived':['MVPAsqrt'], 'final': True}, ],
       'init2h': ["VO2max","CommHome","gender",dist2Home],
       'drv2h': [
        {'owner': 'left', 'stitch': ["gender", "CommHome", "VO2max"], 'derived':['age'], 'final': False},
        {'owner': 'left', 'stitch': ["gender", "CommHome", "VO2max"], 'derived':['MVPAsqrt'], 'final': True},]
    },
    {  'name': 'cust2',   #same as cust1, except shared stitches instead of left
                          # left stitch works better than shared in this case
       'init2s': ["VO2max", "CommToSch", "gender", dist2Sch],
       'drv2s': [ {'owner': 'shared', 'stitch': ["gender", "CommToSch", "VO2max"], 'derived':['age'], 'final': False},
       {'owner': 'shared', 'stitch': ["gender", "CommToSch", "VO2max"], 'derived':['MVPAsqrt'], 'final': True}, ],
       'init2h': ["VO2max","CommHome","gender",dist2Home],
       'drv2h': [
        {'owner': 'shared', 'stitch': ["gender", "CommHome", "VO2max"], 'derived':['age'], 'final': False},
        {'owner': 'shared', 'stitch': ["gender", "CommHome", "VO2max"], 'derived':['MVPAsqrt'], 'final': True},]
    },
    {  'name': 'target_VO2max',   # same as target VO2max
       'init2s': ["VO2max", "gender", "age", "MVPAsqrt"],
       'drv2s': [ {'owner': 'shared', 'stitch': ["VO2max"], 'derived':[dist2Sch], 'final': False},
       {'owner': 'left', 'stitch': ["VO2max"], 'derived':['CommToSch'], 'final': True}, ],

       'init2h': ["VO2max", "gender", "age", dist2Home],
       'drv2h': [
        {'owner': 'left', 'stitch': ["VO2max"], 'derived':['CommHome'], 'final': False},
        {'owner': 'left', 'stitch': ["VO2max"], 'derived':['MVPAsqrt'], 'final': True},]
    },
    {  'name': 'cust3',   # like target VO2max, but shared stitch instead of
                          # left stitch. small improvement over left.
       'init2s': ["VO2max", "gender", "age", "MVPAsqrt"],
       'drv2s': [ {'owner': 'shared', 'stitch': ["VO2max"], 'derived':[dist2Sch], 'final': False},
       {'owner': 'shared', 'stitch': ['VO2max'], 'derived':['CommToSch'], 'final': True}, ],
       'init2h': ["VO2max", "gender", "age", dist2Home],
       'drv2h': [
        {'owner': 'shared', 'stitch': ['VO2max'], 'derived':['CommHome'], 'final': False},
        {'owner': 'shared', 'stitch': ['VO2max'], 'derived':['MVPAsqrt'], 'final': True},]
    },
    {  'name': 'cust4',   # from cust3, does 'left' on final stitches
                          # Slightly worse than cust 3
       'init2s': ["VO2max", "gender", "age", "MVPAsqrt"],
       'drv2s': [ {'owner': 'left', 'stitch': ["VO2max"], 'derived':[dist2Sch], 'final': False},
       {'owner': 'left', 'stitch': ['VO2max'], 'derived':['CommToSch'], 'final': True}, ],

       'init2h': ["VO2max", "gender", "age", dist2Home],
       'drv2h': [
        {'owner': 'left', 'stitch': ['VO2max'], 'derived':['CommHome'], 'final': False},
        {'owner': 'left', 'stitch': ['VO2max'], 'derived':['MVPAsqrt'], 'final': True},]
    },
    {  'name': 'cust5',   # from cust3, pushes 'gender' to later stitches
                          # This did a little worse I'm afraid
       'init2s': ["VO2max", dist2Sch, "age", "MVPAsqrt"],
       'drv2s': [ {'owner': 'shared', 'stitch': ["VO2max"], 'derived':["gender"], 'final': False},
       {'owner': 'shared', 'stitch': ['VO2max'], 'derived':['CommToSch'], 'final': True}, ],

       'init2h': ["VO2max", "MVPAsqrt", "age", dist2Home],
       'drv2h': [
        {'owner': 'shared', 'stitch': ['VO2max'], 'derived':['CommHome'], 'final': False},
        {'owner': 'shared', 'stitch': ['VO2max'], 'derived':['gender'], 'final': True},]
    },
    {  'name': 'target_VO2max_left',   # same as target VO2max, but left
                                       # not shared. Shared slightly better.
       'init2s': ["VO2max", "gender", "age", "MVPAsqrt"],
       'drv2s': [ {'owner': 'left', 'stitch': ["VO2max"], 'derived':[dist2Sch], 'final': False},
       {'owner': 'left', 'stitch': [], 'derived':['CommToSch'], 'final': True}, ],
       'init2h': ["VO2max", "gender", "age", dist2Home],
       'drv2h': [
        {'owner': 'left', 'stitch': [], 'derived':['CommHome'], 'final': False},
        {'owner': 'left', 'stitch': [], 'derived':['MVPAsqrt'], 'final': True},]
    },
]

for cluster in custom_clusters:
    # Generate two synthetic tables with custom clustering strategies
    # We use SingleClustering() here as a simple default. We will customize the
    # clustering strategy before sample()
    name = cluster['name']
    if os.path.exists(os.path.join('csvFiles', f'{name}_2school.csv')):
        # We've already done this one, skip
        continue
    syn_cust_2school = Synthesizer(df[toSchoolColumns], clustering=SingleClustering())
    ci = ClusterInfo(syn_cust_2school)
    ci.put_initial_cluster(cluster['init2s'])
    for drv in cluster['drv2s']:
        ci.put_derived_cluster(owner=drv['owner'], stitch_columns=drv['stitch'], derived_columns=drv['derived'], final=drv['final'])
    df_syn_cust_2school = syn_cust_2school.sample()
    # Save the synthetic data to a new csv file c2schooled CommDataSyn.csv
    df_syn_cust_2school.to_csv(os.path.join('csvFiles', f'{name}_2school.csv'), index=False)
    do_cluster_info(syn_cust_2school, os.path.join('csvFiles', f'{name}_2school.json'))

    syn_cust_2home = Synthesizer(df[toHomeColumns], clustering=SingleClustering())
    ci = ClusterInfo(syn_cust_2home)
    ci.put_initial_cluster(cluster['init2h'])
    for drv in cluster['drv2h']:
        ci.put_derived_cluster(owner=drv['owner'], stitch_columns=drv['stitch'], derived_columns=drv['derived'], final=drv['final'])
    df_syn_cust_2home = syn_cust_2home.sample()
    # Save the synthetic data to a new csv file c2homeed CommDataSyn.csv
    df_syn_cust_2home.to_csv(os.path.join('csvFiles', f'{name}_2home.csv'), index=False)
    do_cluster_info(syn_cust_2home, os.path.join('csvFiles', f'{name}_2home.json'))

quit()
# Generate two targetted synthetic tables, each containinng only the columns needed for the
# specific communuting direction used in the analysis
syn_2school = Synthesizer(df[toSchoolColumns], clustering=MlClustering(target_column="VO2max", drop_non_features=False, max_weight=max_weight))
do_cluster_info(syn_2school, os.path.join('csvFiles', 'target_VO2max_2school.json'))
df_syn_2school = syn_2school.sample()
# Save the synthetic data to a new csv file c2schooled CommDataSyn.csv
df_syn_2school.to_csv(os.path.join('csvFiles', 'target_VO2max_2school.csv'), index=False)

syn_2home = Synthesizer(df[toHomeColumns], clustering=MlClustering(target_column="VO2max", drop_non_features=False, max_weight=max_weight))
df_syn_2home = syn_2home.sample()
# Save the synthetic data to a new csv file c2homeed CommDataSyn.csv
df_syn_2home.to_csv(os.path.join('csvFiles', 'target_VO2max_2home.csv'), index=False)
do_cluster_info(syn_2home, os.path.join('csvFiles', 'target_VO2max_2home.json'))

# Generate two targetted synthetic tables, each containinng only the columns needed for the
# specific communuting direction used in the analysis
syn_2school = Synthesizer(df[toSchoolColumns], clustering=MlClustering(target_column="VO2max", drop_non_features=False, max_weight=max_weight))
do_cluster_info(syn_2school, os.path.join('csvFiles', 'target_VO2max_2school.json'))
df_syn_2school = syn_2school.sample()
# Save the synthetic data to a new csv file c2schooled CommDataSyn.csv
df_syn_2school.to_csv(os.path.join('csvFiles', 'target_VO2max_2school.csv'), index=False)

syn_2home = Synthesizer(df[toHomeColumns], clustering=MlClustering(target_column="VO2max", drop_non_features=False, max_weight=max_weight))
df_syn_2home = syn_2home.sample()
# Save the synthetic data to a new csv file c2homeed CommDataSyn.csv
df_syn_2home.to_csv(os.path.join('csvFiles', 'target_VO2max_2home.csv'), index=False)
do_cluster_info(syn_2home, os.path.join('csvFiles', 'target_VO2max_2home.json'))

# Generate two complete synthetic tables, each containinng only the columns needed for the
# specific communuting direction used in the analysis
syn_2school = Synthesizer(df[toSchoolColumns], clustering=SingleClustering())
df_syn_2school = syn_2school.sample()
# Save the synthetic data to a new csv file c2schooled CommDataSyn.csv
df_syn_2school.to_csv(os.path.join('csvFiles', 'complete_2school.csv'), index=False)
do_cluster_info(syn_2school, os.path.join('csvFiles', 'complete_2school.json'))

syn_2home = Synthesizer(df[toHomeColumns], clustering=SingleClustering())
df_syn_2home = syn_2home.sample()
# Save the synthetic data to a new csv file c2homeed CommDataSyn.csv
df_syn_2home.to_csv(os.path.join('csvFiles', 'complete_2home.csv'), index=False)
do_cluster_info(syn_2home, os.path.join('csvFiles', 'complete_2home.json'))

# Generate a targeted synthetic dataset with all columns. Note that we
# duplicate the output for 2home and 2school to match other cases
syn_all = Synthesizer(df, clustering=MlClustering(target_column="VO2max", drop_non_features=False, max_weight=max_weight))
df_syn_all = syn_all.sample()
df_syn_all.to_csv(os.path.join('csvFiles', 'target_VO2max_all_2home.csv'), index=False)
df_syn_all.to_csv(os.path.join('csvFiles', 'target_VO2max_all_2school.csv'), index=False)
print("Synthetic data counts:")
print(df_syn_all.groupby(['gender', 'CommToSch']).size())
print(df_syn_all.groupby(['gender', 'CommHome']).size())
do_cluster_info(syn_all, os.path.join('csvFiles', 'target_VO2max_all_2home.json'))
do_cluster_info(syn_all, os.path.join('csvFiles', 'target_VO2max_all_2school.json'))

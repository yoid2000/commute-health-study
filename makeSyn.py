import pandas as pd
from syndiffix import Synthesizer
from syndiffix.clustering.strategy import DefaultClustering

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

syn = Synthesizer(df, target_column='VO2max', drop_non_features=False,
#                        clustering=DefaultClustering(
#                            max_weight=cluster_params['max_weight'],
#                            sample_size=cluster_params['sample_size'],
#                            merge_threshold=cluster_params['merge_threshold'],
#                        )
                        )
df_syn = syn.sample()
# Save the synthetic data to a new csv file called CommDataSyn.csv
df_syn.to_csv('CommDataSyn.csv', index=False)
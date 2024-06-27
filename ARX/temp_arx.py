import os
import pandas as pd
import pprint

pp = pprint.PrettyPrinter(indent=4)

baseDir = os.environ['COMMUTE_HEALTH_PATH']
print(f"setting baseDir to {baseDir}")

df_syn = pd.read_csv('temp_file.csv', index_col=False)
df_syn = df_syn.loc[:, ~df_syn.columns.str.contains('^Unnamed')]

df_syn.to_csv(os.path.join('datasets', 'syn_dataset.csv'), index=False)

# save df_syn as a parquet file
df_syn.to_parquet(os.path.join('datasets', 'syn_dataset.parquet'), index=False)
import os
import time
import pandas as pd
import pprint
from sdv.metadata import SingleTableMetadata
import sdv
from sdv.single_table import CTGANSynthesizer

print("SDV version:", sdv.version.public)

pp = pprint.PrettyPrinter(indent=4)

baseDir = os.environ['COMMUTE_HEALTH_PATH']
print(f"setting baseDir to {baseDir}")

df_orig = pd.read_csv(os.path.join(baseDir, 'CommDataOrig.csv'), index_col=False)
df_orig = df_orig.loc[:, ~df_orig.columns.str.contains('^Unnamed')]

start_time = time.time()
metadata = SingleTableMetadata()
metadata.detect_from_dataframe(df_orig)
sdv_metadata = metadata.to_dict()
pp.pprint(sdv_metadata)
metadata.validate_data(data=df_orig)

synthesizer = CTGANSynthesizer(metadata)
synthesizer.fit(df_orig)

df_syn = synthesizer.sample(num_rows=len(df_orig))

end_time = time.time()
print(f"Elapsed time: {end_time - start_time}")
print(df_syn.head())

df_syn.to_csv(os.path.join('datasets', 'syn_dataset.csv'), index=False)

# save df_syn as a parquet file
df_syn.to_parquet(os.path.join('datasets', 'syn_dataset.parquet'), index=False)
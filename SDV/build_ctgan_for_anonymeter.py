import os
import time
import pandas as pd
import pprint
from sdv.metadata import SingleTableMetadata
import sdv
from sdv.single_table import CTGANSynthesizer

print("SDV version:", sdv.version.public)

pp = pprint.PrettyPrinter(indent=4)

origPath = os.path.join('..', 'CommDataOrig_original.csv')
df_orig = pd.read_csv(origPath, index_col=False)
df_orig = df_orig.loc[:, ~df_orig.columns.str.contains('^Unnamed')]

start_time = time.time()

# Core instructions (8 lines)
metadata = SingleTableMetadata()
metadata.detect_from_dataframe(df_orig)
sdv_metadata = metadata.to_dict()
pp.pprint(sdv_metadata)
metadata.validate_data(data=df_orig)

synthesizer = CTGANSynthesizer(metadata)
synthesizer.fit(df_orig)

df_syn = synthesizer.sample(num_rows=len(df_orig))
# End of core instructions

end_time = time.time()
print(f"Elapsed time: {end_time - start_time}")
print(df_syn.head())

# make a path to "../risk_evaluation/sdv_original.csv"
syn_path = os.path.join('..', 'risk_evaluation', 'sdv_syn.csv')

df_syn.to_csv(syn_path, index=False)
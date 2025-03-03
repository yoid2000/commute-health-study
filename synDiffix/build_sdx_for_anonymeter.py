import os
import time
import pandas as pd
from syndiffix.blob import SyndiffixBlobBuilder

origPath = os.path.join('..', 'CommDataOrig_original.csv')
df_orig = pd.read_csv(origPath, index_col=False)
df_orig = df_orig.loc[:, ~df_orig.columns.str.contains('^Unnamed')]
path_to_dir = os.path.join('..', 'risk_evaluation')

start_time = time.time()

# Core instructions (2 lines)
sbb = SyndiffixBlobBuilder(blob_name='commute_anonymeter', path_to_dir=path_to_dir, force=True)
sbb.write(df_raw=df_orig)
# End core instructions

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time}")

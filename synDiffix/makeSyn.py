import os
import pandas as pd
import itertools
import json
from syndiffix_tools.tables_builder import TablesBuilder
import pprint

# Set this to true if you want to force synthesis of already synthesized files
force = False

max_combinations = 4

pp = pprint.PrettyPrinter(indent=4)

baseDir = os.environ['COMMUTE_HEALTH_PATH']
print(f"setting baseDir to {baseDir}")

tablesDir = os.path.join(baseDir, 'tmTables')
if not os.path.exists(tablesDir):
    os.makedirs(tablesDir)

tb = TablesBuilder(dir_path=tablesDir)

if tb.df_orig is None:
    # We've never configured the original data, so let's do that now
    df = pd.read_csv(os.path.join(baseDir, 'CommDataOrig.csv'), index_col=False)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    # The following establishes the initial configuration information and original
    # dataset. Edit the file tablesDir/orig_meta_data.json to change the configuration
    tb.put_df_orig(df, 'CommDataOrig')

print("The original data looks like this:")
print(tb.df_orig.head())

print("The column dtypes are this:")
print(tb.df_orig.dtypes)

print("The columns are classified as follows:")
pp.pprint(tb.orig_meta_data['column_classes'])
print(f"If this is not correct, edit the file {os.path.join(tablesDir, 'orig_meta_data.json')}")

# This is a relatively small dataset, so let's create every column combination
# up to four columns. Let's also create a targeted dataset for each column.
# Finally, we'll make a general purpose dataset with all columns.

print("Synthesizing generic all-columns dataset")
tb.synthesize(save_stats="min", force=force)

# Let's do all of the targeted datasets
for target_column in tb.df_orig.columns:
    print(f"Synthesizing dataset with target column {target_column}")
    tb.synthesize(target_column=target_column, save_stats="min", force=force)

# Now let's do the combinations
for i in range(1, max_combinations+1):
    for comb in itertools.combinations(tb.df_orig.columns, i):
        print(f"Synthesizing {list(comb)}")
        tb.synthesize(columns=list(comb), save_stats="min", force=force)

# Let's get some stats about the synthesis process
stats_dir = os.path.join(tablesDir, 'stats')

# read in every json file in stats_dir
elapsed = []
for file in os.listdir(stats_dir):
    if file.endswith('.json'):
        with open(os.path.join(stats_dir, file), 'r') as f:
            stats = json.load(f)
        elapsed.append(stats['elapsed_time'])
print(f"Total files: {len(elapsed)}")
print(f"Max elapsed time: {max(elapsed)}")
print(f"Total elapsed time: {round(sum(elapsed))} seconds, {round(sum(elapsed)/60)} minutes")

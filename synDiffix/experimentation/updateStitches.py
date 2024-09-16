import os
import shutil
import pandas as pd
from syndiffix_tools.tables_reader import TablesReader
from syndiffix.stitcher import stitch
import pprint

pp = pprint.PrettyPrinter(indent=4)
force = False

paper_values = []
baseDir = os.environ['COMMUTE_HEALTH_PATH']
print(f"setting baseDir to {baseDir}")

synDir = os.path.join(baseDir, 'tmTables', 'syn_init')
newDir = os.path.join(baseDir, 'tmTables', 'syn_stitched')

distinct_columns = []

columns_to_update = [   'DistFromHome',
                        'DistFromSchool',
                        'MVPAsqrt',
                        'VO2max',
                    ]

dataframes = {}
dataframes_1col = {}

for filename in os.listdir(synDir):
    if filename.endswith('parquet'):
        parquet_path = os.path.join(synDir, filename)
        df = pd.read_parquet(parquet_path)
        columns = list(df.columns)
        dataframes[filename] = {'df': df, 'columns': columns}
        if len(columns) == 1:
            dataframes_1col[columns[0]] = df
        for column in columns:
            # get the number of distinct values in the column
            distinct_values = df[column].nunique()
            if column not in distinct_columns:
                distinct_columns.append(column)
                print(column, distinct_values)
    else:
        old_path = os.path.join(synDir, filename)
        new_path = os.path.join(newDir, filename)
        shutil.copy(old_path, new_path)

pp.pprint(distinct_columns)

for filename, info in dataframes.items():
    df_right = info['df']
    columns = info['columns']
    old_path = os.path.join(synDir, filename)
    new_path = os.path.join(newDir, filename)
    if not force and os.path.exists(new_path):
        print(f"skipping {filename}")
        continue
    else:
        shutil.copy(old_path, new_path)
    if len(columns) <= 1:
        continue
    for column in columns:
        if column in columns_to_update:
            print(f"updating {column} for {filename}")
            df_left = dataframes_1col[column]
            if len(list(df_left.columns)) > 1:
                print(f"ERROR: column {column} in {filename} has more than one column ")
                quit()
            if set(df_left[column]) == set(df_right[column]):
                print(f"!!!!!!!!!!!!! column {column} in {filename} is the same BEFORE stitching !!!!!!!!!!!!!!")
            df_stitched = stitch(df_left, df_right, shared=False)
            dataframes[filename]['df'] = df_stitched.copy()
            df_right = dataframes[filename]['df']
            if set(df_left[column]) != set(df_stitched[column]):
                print(f"!!!!!!!!!!!!! stitching failed:  column {column} in {filename} !!!!!!!!!!!!!!")
            df_stitched.to_parquet(new_path)

# let's check that we really updated the columns
for filename in os.listdir(synDir):
    if filename.endswith('parquet'):
        old_path = os.path.join(synDir, filename)
        df_old = pd.read_parquet(old_path)
        columns = list(df_old.columns)
        if len(columns) == 1:
            continue
        new_path = os.path.join(newDir, filename)
        df_new = pd.read_parquet(new_path)
        for column in columns:
            if column in columns_to_update:
                if set(df_old[column]) == set(df_new[column]):
                    print(f"ERROR:  column {column} in {filename} is the same")
                    quit()

print("all checks out!")
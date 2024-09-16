import os
import pandas as pd

baseDir = os.environ['COMMUTE_HEALTH_PATH']
synDir = os.path.join(baseDir, 'tmTables', 'syn')
print(baseDir)

def parquet_to_csv(ppath, cpath):
    # Read the Parquet file
    df = pd.read_parquet(ppath)
    
    # Write the DataFrame to a CSV file
    df.to_csv(cpath, index=False)

if True:    # set true for 6-column tables
    for filename in os.listdir(synDir):
        if filename.endswith('parquet') and 'col6.CommHo' in filename:
            ppath = os.path.join(synDir, filename)
            cpath = os.path.join('datasets', 'sdx_toHome_target_VO2max.csv')
            print(f'creating {cpath}')
            parquet_to_csv(ppath, cpath)
        if filename.endswith('parquet') and 'col6.CommTo' in filename:
            ppath = os.path.join(synDir, filename)
            cpath = os.path.join('datasets', 'sdx_toSchool_target_VO2max.csv')
            print(f'creating {cpath}')
            parquet_to_csv(ppath, cpath)
else:
    for filename in os.listdir(synDir):
        if filename.endswith('parquet') and 'col8' in filename and 'TAR.VO2max' in filename:
            ppath = os.path.join(synDir, filename)
            cpath = os.path.join('datasets', 'sdx_toHome_target_VO2max.csv')
            print(f'creating {cpath}')
            parquet_to_csv(ppath, cpath)
            cpath = os.path.join('datasets', 'sdx_toSchool_target_VO2max.csv')
            print(f'creating {cpath}')
            parquet_to_csv(ppath, cpath)

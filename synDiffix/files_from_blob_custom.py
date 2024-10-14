import os
from syndiffix import SyndiffixBlobReader
from syndiffix.stitcher import stitch

import pprint

pp = pprint.PrettyPrinter(indent=4)

def get_df_from_built_dataframes(columns, built_dataframes):
    for df in built_dataframes:
        if set(columns) == set(df.columns):
            return df
    return None

def get_df_from_script(sbr, script):
    built_dataframes = []
    for stitch_command in script:
        df_left = get_df_from_built_dataframes(stitch_command['left'], built_dataframes)
        if df_left is None:
            df_left = sbr.read(columns=stitch_command['left'])
            stitch_record = sbr.stitch_record()
            if len(stitch_record) > 0:
                print(f"stitching needed for {stitch_command['left']}")
                quit()
        df_right = get_df_from_built_dataframes(stitch_command['right'], built_dataframes)
        if df_right is None:
            df_right = sbr.read(columns=stitch_command['right'])
            if len(stitch_record) > 0:
                print(f"stitching needed for {stitch_command['right']}")
                quit()
        built_dataframes.append(stitch(df_left, df_right, shared=stitch_command['shared']))
    return built_dataframes[-1]

baseDir = os.environ['COMMUTE_HEALTH_PATH']
print(f"setting baseDir to {baseDir}")
synDirBlob = os.path.join(baseDir, 'tmTables', 'syn_blob')

sbr = SyndiffixBlobReader(blob_name='commute', path_to_dir=baseDir, cache_df_in_memory=True, force=True)

# Here is my first attempt, but it is worse than automatic
stitch_script_tohome = [
    {'left':['VO2max', 'CommHome'],
     'right':['VO2max', 'CommHome', 'DistFromSchool', 'gender'],
     'shared':False},
    {'left':['VO2max', 'CommHome'],
     'right':['VO2max', 'CommHome', 'age', 'MVPAsqrt'],
     'shared':False},
    {'left':['VO2max', 'CommHome', 'DistFromSchool', 'gender'],
     'right':['VO2max', 'CommHome', 'age', 'MVPAsqrt'],
     'shared':True},
]

stitch_script_toschool = [
    {'left':['VO2max', 'CommToSch'],
     'right':['VO2max', 'CommToSch', 'DistFromHome', 'gender'],
     'shared':False},
    {'left':['VO2max', 'CommToSch'],
     'right':['VO2max', 'CommToSch', 'age', 'MVPAsqrt'],
     'shared':False},
    {'left':['VO2max', 'CommToSch', 'DistFromHome', 'gender'],
     'right':['VO2max', 'CommToSch', 'age', 'MVPAsqrt'],
     'shared':True},
]

# Here is my second attempt, 
stitch_script_tohome = [
    {'left':['VO2max'],
     'right':['VO2max', 'CommHome', 'DistFromSchool', 'gender'],
     'shared':False},
    {'left':['VO2max'],
     'right':['VO2max', 'age', 'MVPAsqrt'],
     'shared':False},
    {'left':['VO2max', 'CommHome', 'DistFromSchool', 'gender'],
     'right':['VO2max', 'age', 'MVPAsqrt'],
     'shared':True},
]

stitch_script_toschool = [
    {'left':['VO2max'],
     'right':['VO2max', 'CommToSch', 'DistFromHome', 'gender'],
     'shared':False},
    {'left':['VO2max'],
     'right':['VO2max', 'age', 'MVPAsqrt'],
     'shared':False},
    {'left':['VO2max', 'CommToSch', 'DistFromHome', 'gender'],
     'right':['VO2max', 'age', 'MVPAsqrt'],
     'shared':True},
]

df_tohome = get_df_from_script(sbr, stitch_script_tohome)
df_toschool = get_df_from_script(sbr, stitch_script_toschool)
cpath_tohome = os.path.join('datasets', 'sdx_toHome_target_VO2max.csv')
df_tohome.to_csv(cpath_tohome, index=False)
cpath_toschool = os.path.join('datasets', 'sdx_toSchool_target_VO2max.csv')
df_toschool.to_csv(cpath_toschool, index=False)

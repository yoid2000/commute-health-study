import os
from syndiffix import SyndiffixBlobReader

import pprint

pp = pprint.PrettyPrinter(indent=4)

sbr = SyndiffixBlobReader(blob_name='commute', path_to_dir='datasets', cache_df_in_memory=True, force=True)

target = "VO2max"

columns = ["VO2max", "MVPAsqrt", "DistFromSchool", "CommHome", "age", "gender"]
df_tohome = sbr.read(columns=columns, target_column=target)
pp.pprint(sbr.stitch_record())
cpath = os.path.join('datasets', 'sdx_toHome_target_VO2max.csv')
df_tohome.to_csv(cpath, index=False)

columns = ["VO2max", "MVPAsqrt", "DistFromHome", "CommToSch", "age", "gender"]
df_toschool = sbr.read(columns=columns, target_column=target)
pp.pprint(sbr.stitch_record())
cpath = os.path.join('datasets', 'sdx_toSchool_target_VO2max.csv')
df_toschool.to_csv(cpath, index=False)
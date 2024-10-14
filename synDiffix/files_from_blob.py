import os
from syndiffix import SyndiffixBlobReader

import pprint

pp = pprint.PrettyPrinter(indent=4)

baseDir = os.environ['COMMUTE_HEALTH_PATH']
print(f"setting baseDir to {baseDir}")
synDirBlob = os.path.join(baseDir, 'tmTables', 'syn_blob')

sbr = SyndiffixBlobReader(blob_name='commute', path_to_dir=baseDir, cache_df_in_memory=True, force=True)

target = "VO2max"

columns = ["VO2max", "MVPAsqrt", "DistFromSchool", "CommHome", "age", "gender"]
df_tohome = sbr.read(columns=columns, target_column=target)
pp.pprint(sbr.stitch_record())
tohome_path = os.path.join(synDirBlob, "commute.col6.CommHo_DistFr_MVPAsq_VVO2max_age_gender.TAR.VO2max.a7uuf6.parquet")
df_tohome.to_parquet(tohome_path)
cpath = os.path.join('datasets', 'sdx_toHome_target_VO2max.csv')
df_tohome.to_csv(cpath, index=False)

columns = ["VO2max", "MVPAsqrt", "DistFromHome", "CommToSch", "age", "gender"]
df_toschool = sbr.read(columns=columns, target_column=target)
pp.pprint(sbr.stitch_record())
toschool_path = os.path.join(synDirBlob, "commute.col6.CommTo_DistFr_MVPAsq_VVO2max_age_gender.TAR.VO2max.83uzrh.parquet")
df_toschool.to_parquet(toschool_path)
cpath = os.path.join('datasets', 'sdx_toSchool_target_VO2max.csv')
df_toschool.to_csv(cpath, index=False)
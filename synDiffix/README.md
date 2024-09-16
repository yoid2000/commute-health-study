Set the environment variable COMMUTE_HEALTH_PATH to the directory where the synDiffix files will be stored.

makeSyn.py reads in a csv file containing the commuting study data. It creates 173 synthetic data files, including all combinations with 1 to 4 columns, two 6-column targeting VO2max, and eight full 8-column tables, also targeting VO2max.

To run CommCode.R, the appropriate files need to be copied from where they are stored, converted from parquet to csv, and placed in 'datasets'. To do this, edit p2c.py to decide if 6-column or 8-column datasets will be used, and run p2c.py. This creates synDiffix/datasets/sdx_toSchool_target_VO2max.csv" and "synDiffix/datasets/sdx_toHome_target_VO2max.csv".

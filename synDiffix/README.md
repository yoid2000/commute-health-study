makeSyn.py reads in a csv file containing the commuting study data. It creates three synthetic data files. In all

1. CommDataSyn_target_VO2max_all.csv. This was generated with all columns, using VO2max as the target column.
2. CommDataSyn_target_VO2max_req.csv. This was generated with all columns except two columns that are not used in the main analysis ("DistFromHome","DistFromSchool"), again using VO2max as the target column.
3. This makes two synthetic tables, using only the columns needed in each direction of commute (labeled ..._2home.csv and ..._2school.csv).
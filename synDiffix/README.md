`build_sdx.py` reads in `../CommDataOrig` and generates the synDiffix blob at `datasets/commute.sdxblob.zip`.

`files_from_blob.py` constructs the two synDiffix csv files required by `CommCode.R`:

```
datasets/sdx_toHome_target_VO2max.csv
datasets/sdx_toSchool_target_VO2max.csv
```

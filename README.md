# bojan-play

Repo for testing synthetic data to see if it is fit for purpose for doing the analysis in the paper "Associations of mode and distance of commuting to school with cardiorespiratory fitness in Slovenian schoolchildren: a nationwide cross-sectional study"

## Datasets

CommData.csv and CommData.Rdata both contain synthetic versions of the full dataset used for the paper. These were produced from the original data by SynDiffix. They can be used to develop synthesis scripts, after which the scripts can be run on the original data by authorized persons.

## Useful scripts

Rdata2csv.R: Creates a csv from from the Rdata. From this we can synthesize. Edit the file name before running.

csv2Rdata.R: Creates an Rdata file from the csv. Edit the file name before running.

Can run, for instance, with `Rscript Rdata2csv.R` in the vscode terminal

## Columns in the commute health data

 * VO2max: The health measure (Oxygen uptake for the shuttle run test and other factors) 56.7335978100438
 * CommToSch: Transport mode to school "car"
 * CommHome: Transport mode from school "car"
 * gender: male or female
 * age: a float 12.3242803444478
 * MVPAsqrt: Self-reported physical activity level (from survey) 25.6904651573303
 * DistLog2Home 15.4460170879173
 * DistLog2ToSch 15.4460170879173
 * DistFromHome 44639
 * DistFromSchool 44639


 VO2max’= constant + commuting group + gender + MVPA + age + commuting group × gender + commuting group × distance

## Paper analysis issues

Can this be done from the synthetic data?

> A post-hoc power analysis showed that, given the number of individuals included in this analysis (N = 713), number of predictors in the models (N = 6) and an alpha value set at 0.05, we had sufficient power (beta=0.81) to detect small effect size (f = 0.14).

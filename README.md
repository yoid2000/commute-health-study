# Commuting Health Paper

This repo contains the code used to produce the data, figures, and tables for the paper "Data Anonymization for Open Science: A Case Study", by Paul Francis, Gregor Jurak, Bojan Leskosek, Thierry Meurers, Karen Otte, and Fabian Praßer.

The paper takes the original data from a base study, anonymized it using three different anonymization tools (ARX 2-anonymity, SDV CTGAN, and SynDiffix), and then determines whether the scientific conclusions of the original paper still hold when the anonymized data is used. 

The base paper for this study is "Associations of mode and distance of commuting to school with cardiorespiratory fitness in Slovenian school children: a nationwide cross-sectional study" by Gregor Jurak, Maroje Soric, Vedrana Sember, Sasa Djuric, Gregor Starc, Marjeta Kovac, and Bojan Leskosek.

A copy of the base study is at papers/commute.pdf. It can be found online at:

https://bmcpublichealth.biomedcentral.com/articles/10.1186/s12889-021-10326-6

## Original data

The original data is not publicly available due to privacy reasons. Please contact Bojan Leskosek at Bojan.Leskosek@fsp.uni-lj.si if you are interested in the original data. (Note this is not a promise to give you the data.)

CommDataSyn.csv is a synthetic version of the original data. It can be used for testing purposes, but is not used in any evaluation.

The true original data should be placed in CommDataOrig.csv. 

# Synthetic data

The directories ARX, SDV, and SynDiffix contain the code to generate the synthetic data for the respective tools. The README files in those directories contain more information.

The synthetic data for ARX and SDV can be found in the following locations respectively:

```
ARX/datasets/syn_dataset.csv and syn_dataset.parquet
SDV/datasets/syn_dataset.csv and syn_dataset.parquet
```

SynDiffix is unique in that it produces multiple datasets when it anonymizes. The datasets are written into a zip file known as a SynDiffix blob. The blob can be found at:

`synDiffix/datasets/commute.sdxblob.zip`

The different datasets contain different columns, and the basic idea is that the dataset with only the columns needed for any given analytic purpose are used. This dataset will have the best accuracy for the analytic task. 

The R script CommCode.R does the linear regression on the data. It uses two of the SynDiffix synthetic data files (one for each direction of commute), located at:

```
synDiffix\datasets\sdx_toHome_target_VO2max.csv
synDiffix\datasets\sdx_toSchool_target_VO2max.csv
```

Because there is no R extension to read a SynDiffix blob, these two files are extracted using the script:

`synDiffix/files_from_blob.py`

## Workflow

Execute the R script `CommCode.R`:

`Rscript CommCode.R` if vscode terminal.

This generates eight files. They are named:

```
results/r_xxx_plot.png
results/r_xxx.json
```

where xxx can be one of `orig`, `arx`, `sdv`, and `sdx`. The plots are displayed in the paper.

Execute:

`python getPaperValues.py`

This reads in the `json` files produced by `CommCode.R` as will as the original and synthetic data files. It generates the following files:

```
results/paper_values.csv
results/paper_values.json
```

(These two files actually contain the same data, but in the two different formats.)

Execute:

`python figs_and_tabs.py`

This reads in `paper_values.json` as well as the synthetic and original data, and produces all of the remaining figures and tables used in the paper (plus some additional plots and tables not used in the paper). The output if placed in `results/tables/`. 

The figures are placed in `results/tables/figs`. The tables are placed in:

```
results/tables/table1.tex
results/tables/table2.tex
results/tables/table3a.tex
results/tables/table3b.tex
```

(Note that these table numbers map to those of the original study paper.)

`figs_and_tabs.py` also produces the file `figs_and_tabs.tex`. This is a main latex file that can be compiled to produce `figs_and_tabs.pdf` as a convenient way of viewing all of the figures and tables.







The script CommCode.R does the analysis and generates the figure from the paper. Note that since CommData.csv is not the original data, the plot produced is slightly different from that of the original paper.

## Build SynDiffix synthetic data

### Tools needed

We are using the github repo `syndiffix_tools` to help manage the building and retrieval of SynDiffix datasets. (Note that, unlike most synthetic data tools, SynDiffix generates multiple dataset.)

Install with:

`python -m pip install git+https://github.com/diffix/syndiffix_tools.git`

(Running this in a venv is highly recommended.)

## Miscellaneous notes

Can this be done from the synthetic data?

> A post-hoc power analysis showed that, given the number of individuals included in this analysis (N = 713), number of predictors in the models (N = 6) and an alpha value set at 0.05, we had sufficient power (beta=0.81) to detect small effect size (f = 0.14).

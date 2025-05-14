import os
import sys
import pandas as pd
import json

from scipy.stats import ttest_ind_from_stats
from syndiffix import SyndiffixBlobReader

ORIGINAL_FILE = os.path.join('..', 'CommDataOrig.csv')
SDV_FILE = os.path.join('..', 'SDV', 'datasets', 'syn_dataset.parquet')
ARX_FILE = os.path.join('..', 'ARX', 'datasets', 'syn_dataset.parquet')
BLOB_PATH = os.path.join('..','synDiffix', 'datasets')

def get_sdx_table(sbr, columns, target):
    df_syn = sbr.read(columns=columns, target_column=target)
    if df_syn is None:
        sys.exit(f"ERROR: Could not find a dataset for {columns}, target")
    if list(df_syn[columns]).sort() != columns.sort():
        sys.exit(f"ERROR: Columns in df_syn {list(df_syn[columns])} do not match expected columns {columns}")
    return df_syn


def get_univariate_sdx_stats(sbr, columns):
    univar_stats = pd.DataFrame()
    for column in columns:
        data = get_sdx_table(sbr, [column], None)
        univar_stats[column] = data.describe()

    return univar_stats


def get_comparison_stats(stats_orig: pd.DataFrame, stats_anon: pd.DataFrame, dataset_name):
    formated_stats = pd.DataFrame()

    mean_ori = stats_orig.loc["mean"].round(2)
    sd_ori = stats_orig.loc["std"].round(2)
    count_ori = stats_orig.loc["count"]

    mean_anon = stats_anon.loc["mean"].round(2)
    sd_anon = stats_anon.loc["std"].round(2)
    count_anon = stats_anon.loc["count"]

    formated_stats[f"original mean (SD) n={count_ori.iloc[0]}"] = mean_ori.astype(str) + " (" + sd_ori.astype(str) + ")"
    formated_stats[f"{dataset_name} mean (SD) n={count_anon.iloc[0]}"] = mean_anon.astype(str) + " (" + sd_anon.astype(str) + ")"

    ttest_results = pd.Series()
    for column in stats_orig:
        ttest = ttest_ind_from_stats(mean_ori[column], sd_ori[column], count_ori[column],
                             mean_anon[column], sd_anon[column], count_anon[column], equal_var=True)
        ttest_results[column] = str(ttest.pvalue.round(3))

    formated_stats[f"{dataset_name} ttest pvalue"] = ttest_results
    return formated_stats


if __name__ == "__main__":

    sbr = SyndiffixBlobReader(blob_name='commute', path_to_dir=BLOB_PATH, cache_df_in_memory=True, force=True)
    df_orig = pd.read_csv(ORIGINAL_FILE, index_col=False)
    df_orig = df_orig.loc[:, ~df_orig.columns.str.contains('^Unnamed')]
    df_sdv = pd.read_parquet(SDV_FILE)
    df_arx = pd.read_parquet(ARX_FILE)

    stats_orig = df_orig.describe()
    stats_sdv = df_sdv.describe()
    stats_arx = df_arx.describe()
    stats_sdx = get_univariate_sdx_stats(sbr=sbr, columns=df_orig.columns)

    results_sdv = get_comparison_stats(stats_orig, stats_sdv, "SDV")
    results_arx = get_comparison_stats(stats_orig, stats_arx, "ARX")
    results_sdx = get_comparison_stats(stats_orig, stats_sdx, "SDX")

    aggregated_results = pd.concat([results_arx, results_sdv.iloc[:,1:], results_sdx.iloc[:,1:]], axis=1)
    aggregated_results.to_csv("commute_dataset_comparison.csv")
    print(aggregated_results.to_latex())
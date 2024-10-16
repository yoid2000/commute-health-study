import os
import sys
import pandas as pd
import json
from syndiffix import SyndiffixBlobReader
import pprint
import seaborn as sns
import matplotlib.pyplot as plt

pp = pprint.PrettyPrinter(indent=4)

paper_values = []
blobPath = os.path.join('synDiffix', 'datasets')
if not os.path.exists(blobPath):
    sys.exit(f"ERROR: Blob file {blobPath} does not exist")

sbr = SyndiffixBlobReader(blob_name='commute', path_to_dir=blobPath, cache_df_in_memory=True, force=True)
df_orig = pd.read_csv('CommDataOrig.csv', index_col=False)
print(list(df_orig.columns))
df_orig = df_orig.loc[:, ~df_orig.columns.str.contains('^Unnamed')]
total_rows = len(df_orig)
commute_modes = list(df_orig['CommToSch'].unique())

for column in df_orig.columns:
    distinct_values = df_orig[column].value_counts()
    print(f"Column: {column}")
    if len(distinct_values) <= 20:
        print(distinct_values)
    else:
        print(f"Number of distinct values: {len(distinct_values)}")

df_sdv = pd.read_parquet(os.path.join('SDV', 'datasets', 'syn_dataset.parquet'))
df_arx = pd.read_parquet(os.path.join('ARX', 'datasets', 'syn_dataset.parquet'))

dataset_info = {
    'orig': {'df': df_orig, 'val': 'orig_val'},
    'arx': {'df': df_arx, 'val': 'arx_val'},
    'sdv': {'df': df_sdv, 'val': 'sdv_val'},
    'sdx': {'df': None, 'sbr': sbr, 'val': 'sdx_val'},
}

def do_checks(df):
    ans = df[(df['context'] == 'Table 1') & (df['tab_column'] == 'Commuting from school') & (df['tab_row'] == 'Commuting to school') & (df['tab_sub_column'] == 'walk') & (df['tab_sub_row'] == 'walk') & (df['val_type'] == 'count')]['orig_val'].iloc[0]
    if ans != 275:
        print(f"ERROR: Expected 275, got {ans}")
    ans = df[(df['context'] == 'Table 1') & (df['tab_column'] == 'Commuting from school') & (df['tab_row'] == 'Commuting to school') & (df['tab_sub_column'] == 'walk') & (df['tab_sub_row'] == 'walk') & (df['val_type'] == 'percent')]['orig_val'].iloc[0]
    if round(ans,1) != 38.6:
        print(f"ERROR: Expected 38.6, got {ans}")
    ans = df[(df['context'] == 'Table 1') & (df['tab_column'] == 'Commuting from school') & (df['tab_row'] == 'Commuting to school') & (df['tab_sub_column'] == 'walk') & (df['tab_sub_row'] == 'car') & (df['val_type'] == 'count')]['orig_val'].iloc[0]
    if ans != 57:
        print(f"ERROR: Expected 57, got {ans}")
    ans = df[(df['context'] == 'Table 1') & (df['tab_column'] == 'Commuting from school') & (df['tab_row'] == 'Commuting to school') & (df['tab_sub_column'] == 'walk') & (df['tab_sub_row'] == 'car') & (df['val_type'] == 'percent')]['orig_val'].iloc[0]
    if round(ans,1) != 8.0:
        print(f"ERROR: Expected 8.0, got {ans}")

    ans = df[(df['context'] == 'Table 2') & (df['tab_column'] == 'From home to school') & (df['tab_row'] == 'Commuting group') & (df['tab_sub_column'] == 'N') & (df['tab_sub_row'] == 'walk') & (df['val_type'] == 'count')]['orig_val'].iloc[0]
    if ans != 279:
        print(f"ERROR: Expected 279, got {ans}")
    ans = df[(df['context'] == 'Table 2') & (df['tab_column'] == 'From home to school') & (df['tab_row'] == 'Commuting group') & (df['tab_sub_column'] == '(%)') & (df['tab_sub_row'] == 'walk') & (df['val_type'] == 'percent')]['orig_val'].iloc[0]
    if round(ans,0) != 39.0:
        print(f"ERROR: Expected 39.0, got {ans}")

    ans = df[(df['context'] == 'Table 2') & (df['tab_column'] == 'From school to home') & (df['tab_row'] == 'Commuting group') & (df['tab_sub_column'] == 'N') & (df['tab_sub_row'] == 'public') & (df['val_type'] == 'count')]['orig_val'].iloc[0]
    if ans != 245:
        print(f"ERROR: Expected 245, got {ans}")
    ans = df[(df['context'] == 'Table 2') & (df['tab_column'] == 'From school to home') & (df['tab_row'] == 'Commuting group') & (df['tab_sub_column'] == '(%)') & (df['tab_sub_row'] == 'public') & (df['val_type'] == 'percent')]['orig_val'].iloc[0]
    if round(ans,0) != 34.0:
        print(f"ERROR: Expected 34.0, got {ans}")

    if False:
        ans = df[(df['context'] == 'Table 2') & (df['tab_column'] == 'From school to home') & (df['tab_row'] == 'Commuting group') & (df['tab_sub_column'] == 'Distance median') & (df['tab_sub_row'] == 'walk') & (df['val_type'] == 'distance_median')]['orig_val'].iloc[0]
        if ans != 973:
            print(f"ERROR: Expected 973, got {ans}")
        ans = df[(df['context'] == 'Table 2') & (df['tab_column'] == 'From school to home') & (df['tab_row'] == 'Commuting group') & (df['tab_sub_column'] == 'Distance IQR') & (df['tab_sub_row'] == 'walk') & (df['val_type'] == 'distance_iqr')]['orig_val'].iloc[0]
        if round(ans,0) != 1046:
            print(f"ERROR: Expected 1046, got {ans}")

    ans = df[(df['context'] == 'Table 3') & (df['tab_column'] == 'From school to home') & (df['tab_row'] == 'Constant') & (df['tab_sub_column'] == 'Coefficient') & (df['val_type'] == 'coefficient')]['orig_val'].iloc[0]
    if round(ans,2) != 36.63:
        print(f"ERROR: Expected 36.63, got {ans}")
    ans = df[(df['context'] == 'Table 3') & (df['tab_column'] == 'From school to home') & (df['tab_row'] == 'Constant') & (df['tab_sub_column'] == '95% CI') & (df['val_type'] == 'ci_low')]['orig_val'].iloc[0]
    if round(ans,2) != 29.11:
        print(f"ERROR: Expected 29.11, got {ans}")

    ans = df[(df['context'] == 'Table 3') & (df['tab_column'] == 'From home to school') & (df['tab_row'] == 'Public x Distance') & (df['tab_sub_column'] == 'Coefficient') & (df['val_type'] == 'coefficient')]['orig_val'].iloc[0]
    if round(ans,2) != 0.06:
        print(f"ERROR: Expected 0.06, got {ans}")
    ans = df[(df['context'] == 'Table 3') & (df['tab_column'] == 'From home to school') & (df['tab_row'] == 'Public x Distance') & (df['tab_sub_column'] == '95% CI') & (df['val_type'] == 'ci_high')]['orig_val'].iloc[0]
    if round(ans,2) != 0.61:
        print(f"ERROR: Expected 0.61, got {ans}")


def get_dataset(dataset, columns, target):
    if dataset_info[dataset]['df'] is not None:
        return dataset_info[dataset]['df'][columns]
    sbr = dataset_info[dataset]['sbr']
    df_syn = sbr.read(columns=columns, target_column=target)
    if df_syn is None:
        sys.exit(f"ERROR: Could not find a dataset for {columns}, target")
    if list(df_syn[columns]).sort() != columns.sort():
        sys.exit(f"ERROR: Columns in df_syn {list(df_syn[columns])} do not match expected columns {columns}")
    return df_syn

def init_row():
    return {
        'context': None,
        'tab_column': None,
        'tab_row': None,
        'tab_sub_column': None,
        'tab_sub_row': None,
        'val_type': None,
        'orig_val': None,
        'sdv_val': None,
        'arx_val': None,
        'sdx_val': None,
        'sdv_norm_err': None,
        'arx_norm_err': None,
        'sdx_norm_err': None,
        'sdv_abs_err': None,
        'arx_abs_err': None,
        'sdx_abs_err': None,
    }

def update_row(row, dset, val):
    row[dataset_info[dset]['val']] = val
    if dset == 'orig':
        return
    if row['val_type'] == 'count':
        # Compute error relative to the total count, normalized
        # to the range 0-1
        row[f'{dset}_norm_err'] = abs(val - row['orig_val']) / total_rows
        row[f'{dset}_abs_err'] = abs(val - row['orig_val'])
    elif row['val_type'] == 'percent':
        # Compute error relative to the total percent, normalized
        # to the range 0-1
        row[f'{dset}_norm_err'] = abs(val - row['orig_val']) / 100
    else:
        row[f'{dset}_abs_err'] = abs(val - row['orig_val'])
        if max(abs(val), abs(row['orig_val'])) != 0:
            row[f'{dset}_norm_err'] = abs(val - row['orig_val']) / max(abs(val), abs(row['orig_val']))

tab3_mappings = {
    "(Intercept)": "Constant",
    "gendermale": "Males",
    "age": "Age",
    "MVPAsqrt": "MVPA",
    "CommToSchcar": "Car",
    "CommToSchpublic": "Public",
    "CommToSchwheels": "Wheels",
    "CommToSchcar:gendermale": "Car x Males",
    "CommToSchpublic:gendermale": "Public x Males",
    "CommToSchwheels:gendermale": "Wheels x Males",
    "CommToSchwalk:DistLogToSch": "Walk x Distance",
    "CommToSchcar:DistLogToSch": "Car x Distance",
    "CommToSchpublic:DistLogToSch": "Public x Distance",
    "CommToSchwheels:DistLogToSch": "Wheels x Distance",
    "CommHomecar": "Car",
    "CommHomepublic": "Public",
    "CommHomewheels": "Wheels",
    "CommHomecar:gendermale": "Car x Males",
    "CommHomepublic:gendermale": "Public x Males",
    "CommHomewheels:gendermale": "Wheels x Males",
    "CommHomewalk:DistLogToHome": "Walk x Distance",
    "CommHomecar:DistLogToHome": "Car x Distance",
    "CommHomepublic:DistLogToHome": "Public x Distance",
    "CommHomewheels:DistLogToHome": "Wheels x Distance",
}

def find_fig1_row(context, tab_column, tab_sub_column, tab_row, tab_sub_row, val_type):
    match = None
    for row in paper_values:
        if row['context'] == context and row['tab_column'] == tab_column and row['tab_row'] == tab_row and row['val_type'] == val_type and row['tab_sub_column'] == tab_sub_column and row['tab_sub_row'] == tab_sub_row:
            if match is not None:
                sys.exit(f"ERROR: Multiple matches for {context}, {tab_column}, {tab_row}, {val_type}, {tab_sub_column}, {tab_sub_row}")
            match = row
    if match is None:
        sys.exit(f"ERROR: No match for {context}, {tab_column}, {tab_row}, {val_type}, {tab_sub_column}, {tab_sub_row}")
    return match

def find_tab3_row(context, tab_column, tab_row, val_type):
    match = None
    for row in paper_values:
        if row['context'] == context and row['tab_column'] == tab_column and row['tab_row'] == tab_row and row['val_type'] == val_type:
            if match is not None:
                sys.exit(f"ERROR: Multiple matches for {context}, {tab_column}, {tab_row}, {val_type}")
            match = row
    if match is None:
        sys.exit(f"ERROR: No match for {context}, {tab_column}, {tab_row}, {val_type}")
    return match

def populate_figure1(data, dset):
    for mode, label, modeKey in [['conf_2s','Commuting mode (from home to school)', 'CommToSch'],
               ['conf_2h','Commuting mode (from school to home)', 'CommHome']]:
        for datapoint in data[mode]:
            if dset == 'orig':
                row_fit = init_row()
                row_fit['context'] = 'Figure 1'
                row_fit['tab_column'] = label
                row_fit['tab_sub_column'] = datapoint[modeKey]
                row_fit['tab_row'] = "VO2max (predicted at mode median distance)"
                row_fit['tab_sub_row'] = datapoint['gender']
                row_fit['val_type'] = 'fit'
                row_lwr = init_row()
                row_lwr['context'] = 'Figure 1'
                row_lwr['tab_column'] = label
                row_lwr['tab_sub_column'] = datapoint[modeKey]
                row_lwr['tab_row'] = "VO2max (predicted at mode median distance)"
                row_lwr['tab_sub_row'] = datapoint['gender']
                row_lwr['val_type'] = 'lwr'
                row_upr = init_row()
                row_upr['context'] = 'Figure 1'
                row_upr['tab_column'] = label
                row_upr['tab_sub_column'] = datapoint[modeKey]
                row_upr['tab_row'] = "VO2max (predicted at mode median distance)"
                row_upr['tab_sub_row'] = datapoint['gender']
                row_upr['val_type'] = 'upr'
                paper_values.append(row_fit)
                paper_values.append(row_lwr)
                paper_values.append(row_upr)
            else:
                row_fit = find_fig1_row('Figure 1', label, datapoint[modeKey], 'VO2max (predicted at mode median distance)', datapoint['gender'], 'fit')
                row_lwr = find_fig1_row('Figure 1', label, datapoint[modeKey], 'VO2max (predicted at mode median distance)', datapoint['gender'], 'lwr')
                row_upr = find_fig1_row('Figure 1', label, datapoint[modeKey], 'VO2max (predicted at mode median distance)', datapoint['gender'], 'upr')
            update_row(row_fit, dset, datapoint['fit'])
            update_row(row_lwr, dset, datapoint['lwr'])
            update_row(row_upr, dset, datapoint['upr'])

'''def find_fig1_row(context, tab_column, tab_sub_column, tab_row, tab_sub_row, val_type):'''

def populate_table3(data, dset, tab_column):
    for datapoint in data:
        if dset == 'orig':
            row_coef = init_row()
            row_coef['context'] = 'Table 3'
            row_coef['tab_column'] = tab_column
            row_coef['tab_row'] = f"{tab3_mappings[datapoint['_row']]}"
            row_coef['val_type'] = 'coefficient'
            row_coef['tab_sub_column'] = 'Coefficient'
            row_prt = init_row()
            row_prt['context'] = 'Table 3'
            row_prt['tab_column'] = tab_column
            row_prt['tab_row'] = f"{tab3_mappings[datapoint['_row']]}"
            row_prt['val_type'] = 'prt'
            row_prt['tab_sub_column'] = 'Coefficient'
            row_ci_low = init_row()
            row_ci_low['context'] = 'Table 3'
            row_ci_low['tab_column'] = tab_column
            row_ci_low['tab_row'] = f"{tab3_mappings[datapoint['_row']]}"
            row_ci_low['val_type'] = 'ci_low'
            row_ci_low['tab_sub_column'] = '95% CI'
            row_ci_high = init_row()
            row_ci_high['context'] = 'Table 3'
            row_ci_high['tab_column'] = tab_column
            row_ci_high['tab_row'] = f"{tab3_mappings[datapoint['_row']]}"
            row_ci_high['val_type'] = 'ci_high'
            row_ci_high['tab_sub_column'] = '95% CI'
            paper_values.append(row_coef)
            paper_values.append(row_prt)
            paper_values.append(row_ci_low)
            paper_values.append(row_ci_high)
        else:
            row_coef = find_tab3_row('Table 3', tab_column, f"{tab3_mappings[datapoint['_row']]}", 'coefficient')
            row_prt = find_tab3_row('Table 3', tab_column, f"{tab3_mappings[datapoint['_row']]}", 'prt')
            row_ci_low = find_tab3_row('Table 3', tab_column, f"{tab3_mappings[datapoint['_row']]}", 'ci_low')
            row_ci_high = find_tab3_row('Table 3', tab_column, f"{tab3_mappings[datapoint['_row']]}", 'ci_high')
        update_row(row_coef, dset, datapoint['Estimate'])
        update_row(row_prt, dset, datapoint['Pr.t.'])
        update_row(row_ci_low, dset, datapoint['2.5 %'])
        update_row(row_ci_high, dset, datapoint['97.5 %'])


# ------------------------------------------------
'''
Page 2:
A post-hoc power analysis showed that, given the number of individuals included in this analysis (N = 713), number of predictors in the models (N = 6) and an alpha value set at 0.05, we had sufficient power (beta=0.81) to detect small effect size (f = 0.14).
'''
# Status: don't know how to replicate this

# ------------------------------------------------
'''
Page 3:
CRF was determined using a 20-m shuttle run test [28].  The test has a moderate-to-high criterion validity for estimating the maximum oxygen uptake (VO2max; r = 0.66–0.84), which is higher when other variables (e.g. sex, age or body mass) are taken into account (r = 0.78–0.95) [29]. Moreover, it has a test-retest reliability coefficient of 0.89 for children [28].
'''
# Status: find out if this is something we need to replicate (looks like it is information from other papers).

# ------------------------------------------------
'''
Page 3:
before the transformation Pearson’s moment coefficient of skewness g3 was 0.71 and 3.61, and after transformation it was − 0.13 and − 0.05, for MVPA and distance, respectively. After the final models were constructed, commuting groups and gender adjusted marginal means with 95% prediction intervals of CRF were calculated at commuting group median street distance from home to
'''
# Status: find out how to deal with this

# ------------------------------------------------

# Table 1 has more detail than the data provided, but we can work
# with the four categories
# We are just getting table stats, so no target
target = None

for comm_to_sch in commute_modes:
    for comm_home in commute_modes:
        row_count = init_row()
        row_count['context'] = 'Table 1'
        row_count['tab_column'] = 'Commuting from school'
        row_count['tab_row'] = 'Commuting to school'
        row_count['val_type'] = 'count'
        row_count['tab_sub_row'] = comm_to_sch
        row_count['tab_sub_column'] = comm_home
        row_percent = init_row()
        row_percent['context'] = 'Table 1'
        row_percent['tab_column'] = 'Commuting from school'
        row_percent['tab_row'] = 'Commuting to school'
        row_percent['val_type'] = 'percent'
        row_percent['tab_sub_row'] = comm_to_sch
        row_percent['tab_sub_column'] = comm_home
        for dataset in dataset_info.keys():
            working_columns = ['CommToSch', 'CommHome']
            df = get_dataset(dataset, working_columns, target)
            count = len(df[(df['CommToSch'] == comm_to_sch) & (df['CommHome'] == comm_home)])
            percent = (count / total_rows) * 100
            update_row(row_count, dataset, count)
            update_row(row_percent, dataset, percent)
        paper_values.append(row_count)
        paper_values.append(row_percent)

# ------------------------------------------------
# Table 2

target = None
tab_row = 'Commuting group'
for tab_column, working_columns in [
    ('From home to school', 'CommToSch'),
    ('From school to home', 'CommHome'), ]:
    for commute_mode in commute_modes:
        row_count = init_row()
        row_count['context'] = 'Table 2'
        row_count['tab_column'] = tab_column
        row_count['tab_row'] = tab_row
        row_count['val_type'] = 'count'
        row_count['tab_sub_row'] = commute_mode
        row_count['tab_sub_column'] = 'N'
        row_percent = init_row()
        row_percent['context'] = 'Table 2'
        row_percent['tab_column'] = tab_column
        row_percent['tab_row'] = tab_row
        row_percent['val_type'] = 'percent'
        row_percent['tab_sub_row'] = commute_mode
        row_percent['tab_sub_column'] = '(%)'
        for dataset in dataset_info.keys():
            df = get_dataset(dataset, [working_columns], target)
            count = len(df[df[working_columns] == commute_mode])
            percent = (count / total_rows) * 100
            update_row(row_count, dataset, count)
            update_row(row_percent, dataset, percent)
        paper_values.append(row_count)
        paper_values.append(row_percent)

target = None
tab_row = 'Commuting group'
for tab_column, working_columns, dist_column in [
    ('From home to school', ['CommToSch', 'DistFromHome'], 'DistFromHome'),
    ('From school to home', ['CommHome', 'DistFromSchool'], 'DistFromSchool'), ]:
    for commute_mode in commute_modes:
        row_dist = init_row()
        row_dist['context'] = 'Table 2'
        row_dist['tab_column'] = tab_column
        row_dist['tab_row'] = tab_row
        row_dist['val_type'] = 'distance_median'
        row_dist['tab_sub_row'] = commute_mode
        row_dist['tab_sub_column'] = 'Distance median'
        row_iqr = init_row()
        row_iqr['context'] = 'Table 2'
        row_iqr['tab_column'] = tab_column
        row_iqr['tab_row'] = tab_row
        row_iqr['val_type'] = 'distance_iqr'
        row_iqr['tab_sub_row'] = commute_mode
        row_iqr['tab_sub_column'] = 'Distance IQR'
        for dataset in dataset_info.keys():
            df = get_dataset(dataset, working_columns, target)
            df_temp = df[df[working_columns[0]] == commute_mode]
            distance_median = int(df_temp[dist_column].quantile(0.5, interpolation='linear'))
            distance_iqr = int(df_temp[dist_column].quantile(0.75, interpolation='linear') - df_temp[dist_column].quantile(0.25, interpolation='linear'))
            update_row(row_dist, dataset, distance_median)
            update_row(row_iqr, dataset, distance_iqr)
        paper_values.append(row_dist)
        paper_values.append(row_iqr)

# Gather table 3 data
with open(os.path.join('results', 'r_orig.json'), 'r') as file:
    tab3_orig = json.load(file)
with open(os.path.join('results', 'r_arx.json'), 'r') as file:
    tab3_arx = json.load(file)
with open(os.path.join('results', 'r_sdv.json'), 'r') as file:
    tab3_sdv = json.load(file)
with open(os.path.join('results', 'r_sdx.json'), 'r') as file:
    tab3_sdx = json.load(file)

populate_table3(tab3_orig['coef_2s'], 'orig', 'From home to school')
populate_table3(tab3_orig['coef_2h'], 'orig', 'From school to home')
populate_table3(tab3_arx['coef_2s'], 'arx', 'From home to school')
populate_table3(tab3_arx['coef_2h'], 'arx', 'From school to home')
populate_table3(tab3_sdv['coef_2s'], 'sdv', 'From home to school')
populate_table3(tab3_sdv['coef_2h'], 'sdv', 'From school to home')
populate_table3(tab3_sdx['coef_2s'], 'sdx', 'From home to school')
populate_table3(tab3_sdx['coef_2h'], 'sdx', 'From school to home')

populate_figure1(tab3_orig, 'orig')
with open(os.path.join('results', 'paper_values.json'), 'w') as file:
    json.dump(paper_values, file, indent=4)
populate_figure1(tab3_arx, 'arx')
populate_figure1(tab3_sdv, 'sdv')
populate_figure1(tab3_sdx, 'sdx')


# ------------------------------------------------
with open(os.path.join('results', 'paper_values.json'), 'w') as file:
    json.dump(paper_values, file, indent=4)

# convert paper_values to a dataframe, and save as a csv file
df_summ = pd.DataFrame(paper_values)
df_summ.to_csv(os.path.join('results', 'paper_values.csv'), index=False)


print('----------------------------------------------------')
for column in df_summ.columns:
    distinct_values = df_summ[column].value_counts()
    print(f"Column: {column}")
    if len(distinct_values) <= 20:
        print(distinct_values)
    else:
        print(f"Number of distinct values: {len(distinct_values)}")

do_checks(df_summ)

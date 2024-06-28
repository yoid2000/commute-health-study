import os
import pandas as pd
import json
from syndiffix_tools.tables_reader import TablesReader
import pprint
import seaborn as sns
import matplotlib.pyplot as plt

pp = pprint.PrettyPrinter(indent=4)

baseDir = os.environ['COMMUTE_HEALTH_PATH']
print(f"setting baseDir to {baseDir}")

synDir = os.path.join(baseDir, 'tmTables', 'syn')

tr = TablesReader(dir_path=synDir)
df_orig = pd.read_csv(os.path.join(baseDir, 'CommDataOrig.csv'), index_col=False)
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
    'sdv': {'df': df_sdv, 'val': 'sdv_val'},
    'arx': {'df': df_arx, 'val': 'arx_val'},
    'sdx': {'df': None, 'tr': tr, 'val': 'sdx_val'},
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

def get_dataset(dataset, columns, target):
    if dataset_info[dataset]['df'] is not None:
        return dataset_info[dataset]['df'][columns]
    tr = dataset_info[dataset]['tr']
    df_syn = tr.get_best_syn_df(columns=columns, target=target)
    if df_syn is None:
        print(f"ERROR: Could not find a dataset for {columns}, target")
        quit()
    if list(df_syn[columns]).sort() != columns.sort():
        print(f"ERROR: Columns in df_syn {list(df_syn[columns])} do not match expected columns {columns}")
        quit()
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

def update_row(row, dataset, val):
    row[dataset_info[dataset]['val']] = val
    if dataset == 'orig':
        return
    if row['val_type'] == 'count':
        # Compute error relative to the total count, normalized
        # to the range 0-1
        row[f'{dataset}_norm_err'] = abs(val - row['orig_val']) / total_rows
        row[f'{dataset}_abs_err'] = abs(val - row['orig_val'])
    if row['val_type'] == 'percent':
        # Compute error relative to the total percent, normalized
        # to the range 0-1
        row[f'{dataset}_norm_err'] = abs(val - row['orig_val']) / 100
    if row['val_type'] in ['distance_median', 'distance_iqr']:
        row[f'{dataset}_abs_err'] = abs(val - row['orig_val'])
        if max(val, row['orig_val']) != 0:
            row[f'{dataset}_norm_err'] = abs(val - row['orig_val']) / max(val, row['orig_val'])

paper_values = []

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
        row_count['tab_column'] ='Commuting from school'
        row_count['tab_row'] ='Commuting to school'
        row_count['val_type'] = 'count'
        row_count['tab_sub_row'] = comm_to_sch
        row_count['tab_sub_column'] = comm_home
        row_percent = init_row()
        row_percent['context'] = 'Table 1'
        row_percent['tab_column'] ='Commuting from school'
        row_percent['tab_row'] ='Commuting to school'
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
            distance_median = int(df_temp[dist_column].quantile(0.5, interpolation='nearest'))
            distance_iqr = int(df_temp[dist_column].quantile(0.75, interpolation='nearest') - df_temp[dist_column].quantile(0.25, interpolation='nearest'))
            update_row(row_dist, dataset, distance_median)
            update_row(row_iqr, dataset, distance_iqr)
        paper_values.append(row_dist)
        paper_values.append(row_iqr)

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

# Make a basic boxplot for all of the normalized error values
columns = ['sdx_norm_err', 'arx_norm_err', 'sdv_norm_err']
sns.boxplot(data=df_summ[columns])
plt.xlabel('')
plt.ylabel('Normalized Error')
plt.savefig(os.path.join('results', 'norm_err.png'))
plt.close()

# Make a basic boxplot for all of the count error values
columns = ['sdx_abs_err', 'arx_abs_err', 'sdv_abs_err']
sns.boxplot(data=df_summ[columns])
plt.xlabel('')
plt.ylabel('Count Error')
plt.savefig(os.path.join('results', 'count_err.png'))
plt.close()
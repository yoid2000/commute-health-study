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
        print()
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
        'sdv_cnt_err': None,
        'arx_cnt_err': None,
        'sdx_cnt_err': None,
    }

def update_row(row, dataset, val):
    row[dataset_info[dataset]['val']] = val
    if dataset == 'orig':
        return
    if row['val_type'] == 'count':
        # Compute error relative to the total count, normalized
        # to the range 0-1
        row[f'{dataset}_norm_err'] = abs(val - row['orig_val']) / total_rows
        row[f'{dataset}_cnt_err'] = abs(val - row['orig_val'])
    if row['val_type'] == 'percent':
        # Compute error relative to the total percent, normalized
        # to the range 0-1
        row[f'{dataset}_norm_err'] = abs(val - row['orig_val']) / 100

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
    ('From home to school', ['CommToSch']),
    ('From school to home', ['CommHome']),
]:
    df = get_dataset(dataset, working_columns, target)
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
            count = len(df[(df[working_columns] == commute_mode)])
            percent = (count / total_rows) * 100
            update_row(row_count, dataset, count)
            update_row(row_percent, dataset, percent)
            paper_values.append(row_count)
            paper_values.append(row_percent)

# ------------------------------------------------
with open(os.path.join('results', 'paper_values.json'), 'w') as file:
    json.dump(paper_values, file, indent=4)

# convert paper_values to a dataframe, and save as a csv file
df_paper_values = pd.DataFrame(paper_values)
df_paper_values.to_csv(os.path.join('results', 'paper_values.csv'), index=False)

# Make a basic boxplot for all of the normalized error values
columns = ['sdx_norm_err', 'arx_norm_err', 'sdv_norm_err']
sns.boxplot(data=df_paper_values[columns])
plt.xlabel('Error Type')
plt.ylabel('Normalized Error')
plt.savefig(os.path.join('results', 'norm_err.png'))
plt.close()

# Make a basic boxplot for all of the count error values
columns = ['sdx_cnt_err', 'arx_cnt_err', 'sdv_cnt_err']
sns.boxplot(data=df_paper_values[columns])
plt.xlabel('Error Type')
plt.ylabel('Count Error')
plt.savefig(os.path.join('results', 'count_err.png'))
plt.close()
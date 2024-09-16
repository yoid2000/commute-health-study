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

oldDir = os.path.join(baseDir, 'tmTables', 'syn_init')
newDir = os.path.join(baseDir, 'tmTables', 'syn_stitched')

tr_old = TablesReader(dir_path=oldDir)
tr_new = TablesReader(dir_path=newDir)

print(tr_old.all_columns)

for columns in [['DistFromHome', 'CommToSch'], ['DistFromSchool', 'CommHome']]:
    df_old2 = tr_old.get_best_syn_df(columns=columns)
    df_new2 = tr_new.get_best_syn_df(columns=columns)

    column = columns[0]

    df_old1 = tr_old.get_best_syn_df(columns=[column])
    df_new1 = tr_new.get_best_syn_df(columns=[column])

    # Sort the dataframes by the specified column
    df_new1_sorted = df_new1.sort_values(by=column).reset_index(drop=True)
    df_old1_sorted = df_old1.sort_values(by=column).reset_index(drop=True)
    df_new2_sorted = df_new2.sort_values(by=column).reset_index(drop=True)
    df_old2_sorted = df_old2.sort_values(by=column).reset_index(drop=True)

    # Create the plot
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df_new1_sorted, x=df_new1_sorted.index, y=column, label='df_new1', linewidth=4.5)
    sns.lineplot(data=df_old1_sorted, x=df_old1_sorted.index, y=column, label='df_old1', linewidth=4.5)
    sns.lineplot(data=df_new2_sorted, x=df_new2_sorted.index, y=column, label='df_new2')
    sns.lineplot(data=df_old2_sorted, x=df_old2_sorted.index, y=column, label='df_old2')

    # Add labels and title
    plt.xlabel('Index (sorted by column)')
    plt.ylabel(column)
    plt.title(f'Comparison of {column} between df_new and df_old')
    plt.legend()

    plt.savefig(os.path.join('plots', f'old_new_{column}.png'))
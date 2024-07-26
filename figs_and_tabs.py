import pandas as pd
import os
import subprocess
import matplotlib.pyplot as plt
from syndiffix_tools.tables_reader import TablesReader

# Get the original and synthetic data
baseDir = os.environ['COMMUTE_HEALTH_PATH']
print(f"setting baseDir to {baseDir}")
synDir = os.path.join(baseDir, 'tmTables', 'syn')
tr = TablesReader(dir_path=synDir)
df_orig = pd.read_csv(os.path.join(baseDir, 'CommDataOrig.csv'), index_col=False)
print(list(df_orig.columns))
df_orig = df_orig.loc[:, ~df_orig.columns.str.contains('^Unnamed')]
total_rows = len(df_orig)
commute_modes = list(df_orig['CommToSch'].unique())
df_sdv = pd.read_parquet(os.path.join('SDV', 'datasets', 'syn_dataset.parquet'))
df_arx = pd.read_parquet(os.path.join('ARX', 'datasets', 'syn_dataset.parquet'))

# Read in results/paper_values.json as a DataFrame
df = pd.read_json(os.path.join('results', 'paper_values.json'))
print(df.head())
methods = ['orig_val', 'sdx_val', 'arx_val', 'sdv_val']

changes = [['car','Car'], ['public','Public'], ['wheels','Wheels'], ['walk','Walk']]
for change in changes:
    for column in df.columns:
        df[column] = df[column].replace(change[0], change[1], regex=True)
modes = ['Car', 'Public', 'Wheels', 'Walk']

def make_figure_median_plots():
    pass

def make_abs_err_tab1_tab2():
    groups = ['count', 'distance_median', 'distance_iqr']
    titles = ['Counts', 'Median distances (meters)', 'IQR distances (meters)']
    columns = ['sdx_abs_err', 'arx_abs_err', 'sdv_abs_err']
    x_labels = ['SynDiffix', 'ARX', 'SDV']

    fig, axs = plt.subplots(1, 3, figsize=(10, 3), sharey=False)
    for i, group in enumerate(groups):
        df_filtered = df[df['val_type'] == group]
        data_to_plot = df_filtered[columns].dropna()
        axs[i].boxplot(data_to_plot)
        axs[i].set_xticklabels(x_labels)
        axs[i].set_title(titles[i])

    plt.tight_layout(rect=[0, 0, 1, 0.95]) 
    plt.savefig(os.path.join('results', 'tables', 'abs_err_tab1_tab2.png'))
    plt.savefig(os.path.join('results', 'tables', 'figs', 'abs_err_tab1_tab2.pdf'))
    plt.close()

def make_figure_abs_err():
    make_abs_err_tab1_tab2()
    figure = '''
        \\begin{figure}
        \\begin{center}
        \\includegraphics[width=0.85\linewidth]{abs_err_tab1_tab2}
        \\caption{Absolute error of the three anonymization methods for the counts and distances in Tables~\\ref{tab:table1} and \\ref{tab:table2}.
        }
        \\label{fig:abs_err_tab1_tab2}
        \\end{center}
        \\end{figure}
    '''
    with open(os.path.join('results', 'tables', 'abs_err_tab1_tab2.tex'), 'w') as f:
        f.write(figure)
    pass

def make_table2():
    dirs = ['From home to school', 'From school to home']
    col_totals = {}
    for method in methods:
        col_totals[method] = {}
        for dir in dirs:
            col_totals[method][dir] = [0,0]

    def make_cell(mode, dir, val_type1, val_type2):
        df1 = df[(df['context'] == 'Table 2') & (df['tab_sub_row'] == mode) & (df['tab_column'] == dir) & (df['val_type'] == val_type1)]
        if len(df1) != 1:
            print(f'Error: df1 has length {len(df1)}, {mode}, {dir}, {val_type1}')
        df2 = df[(df['context'] == 'Table 2') & (df['tab_sub_row'] == mode) & (df['tab_column'] == dir) & (df['val_type'] == val_type2)]
        if len(df2) != 1:
            print(f'Error: df2 has length {len(df2)}, {mode}, {dir}, {val_type2}')
        cell = ' \\makecell[l]{'
        for method in methods:
            p = '\\%' if val_type2 == 'percent' else ''
            val1 = df1.iloc[0][method]
            if p == '\\%': col_totals[method][dir][0] += val1
            val1 = int(val1)
            val2 = df2.iloc[0][method]
            if p == '\\%': col_totals[method][dir][1] += val2
            val2 = round(val2)
            if method == 'orig_val':
                cell += f'\\textbf{{{val1} ({val2}{p})}} \\\\'
            else:
                cell += f'{val1} ({val2}{p}) \\\\'
        return cell + '}'

    table = '''
      \\begin{table}
      \\begin{center}
      \\begin{small}
      \\begin{tabular}{lllll}
      \\toprule
        \\multirow{2}{*}{\\makecell[l]{\\textbf{Commuting}\\\\\\textbf{group}}}
          & \\multicolumn{2}{l}{\\textbf{From home to school}}
          & \\multicolumn{2}{l}{\\textbf{From school to home}} \\\\ \\cline{2-3} \\cline{4-5}
          & \\textbf{N (\\%)} & \\textbf{Distance (IQR)} & \\textbf{N (\\%)} & \\textbf{Distance (IQR)} \\\\
      \\midrule
    '''
    for mode in modes:
        table += f'{mode}'
        table += f'      & {make_cell(mode, dirs[0], "count", "percent")}'
        table += f'      & {make_cell(mode, dirs[0], "distance_median", "distance_iqr")}'
        table += f'      & {make_cell(mode, dirs[1], "count", "percent")}'
        table += f'      & {make_cell(mode, dirs[1], "distance_median", "distance_iqr")}'
        table += ' \\\\ \\cline{2-5}\n'
    cells = ['','']
    for i, dir in enumerate(dirs):
        cells[i] += '      & \\makecell[l]{'
        for method in methods:
            if method == 'orig_val':
                cells[i] += f'\\textbf{{{int(col_totals[method][dir][0])} ({round(col_totals[method][dir][1])}\\%)}} \\\\'
            else:
                cells[i] += f'{int(col_totals[method][dir][0])} ({round(col_totals[method][dir][1])}\\%) \\\\'
        cells[i] += '}'
    table += '      Total ' + cells[0] + ' & ' + cells[1] + ' & \\\\ \n'

    table += '''
      \\bottomrule
      \\end{tabular}
      \\end{small}
      \\caption{Table 2 from the paper showing the counts and distances in meters (median and IQR) for the original data and the three anonymization methods. Each group of four presents the data in order of Original (bold), SynDiffix, ARX, and SDV. Note that the original distances median and IQR don't perfectly match those of the original Table 2 because of differences in the way median and IQR were calculated (Python versus R).}
      \\label{tab:table2}
      \\end{center}
      \\end{table}
    '''
    with open(os.path.join('results', 'tables', 'table2.tex'), 'w') as f:
        f.write(table)

def make_table1():
    CNT = 0
    PCT = 1
    col_totals = {}
    for method in methods:
        col_totals[method] = {}
        for mode in modes:
            col_totals[method][mode] = [0,0]
    def make_cell(row_mode, col_mode):
        df_count = df[(df['context'] == 'Table 1') & (df['tab_sub_column'] == col_mode) & (df['tab_sub_row'] == row_mode) & (df['val_type'] == 'count')]
        if len(df_count) != 1:
            print(f'Error: df_count has length {len(df_count)}, {row_mode}, {col_mode}')
        df_percent = df[(df['context'] == 'Table 1') & (df['tab_sub_column'] == col_mode) & (df['tab_sub_row'] == row_mode) & (df['val_type'] == 'percent')]
        if len(df_percent) != 1:
            print(f'Error: df_percent has length {len(df_percent)}, {row_mode}, {col_mode}')
        cell = ' \\makecell[l]{'
        for method in methods:
            count = df_count.iloc[0][method]
            row_totals[method][CNT] += count
            col_totals[method][col_mode][CNT] += count
            count = int(count)
            percent = df_percent.iloc[0][method]
            row_totals[method][PCT] += percent
            col_totals[method][col_mode][PCT] += percent
            percent = round(percent, 1)
            if method == 'orig_val':
                cell += f'\\textbf{{{count} ({percent}\\%)}} \\\\'
            else:
                cell += f'{count} ({percent}\\%) \\\\'
        return cell[:-3] + '}'

    table = '''
      \\begin{table}
      \\begin{center}
      \\begin{small}
      \\begin{tabular}{lllllll}
      \\toprule
        & \\multirow{2}{*}{\\makecell[l]{\\textbf{Commuting}\\\\\\textbf{Modes}}}
          & \\multicolumn{5}{l}{\\textbf{Commuting from school}} \\\\ \\cline{3-7}
        & & Car & Public & Wheels & Walk & Total \\\\
      \\midrule
        \\multirow{5}{*}{\\makecell[l]{\\textbf{Commuting}\\\\\\textbf{to school}}}
    '''

    for row_mode in modes:
        row_totals = {}
        for method in methods:
            row_totals[method] = [0,0]
        table += f'& {row_mode}'
        for col_mode in modes:
            table += f'      & {make_cell(row_mode, col_mode)}'
        table += '      & \\makecell[l]{'
        for method in methods:
            if method == 'orig_val':
                table += f'\\textbf{{{int(row_totals[method][CNT])} ({round(row_totals[method][PCT], 1)}\\%)}} \\\\'
            else:
                table += f'{int(row_totals[method][CNT])} ({round(row_totals[method][PCT], 1)}\\%) \\\\'
        table += '} \\\\ \\cline{2-7}\n'
    final_totals = {}
    for method in methods:
        final_totals[method] = [0,0]
    table += '& Total'
    for col_mode in modes:
        table += '      & \\makecell[l]{'
        for method in methods:
            final_totals[method][CNT] += col_totals[method][col_mode][CNT]
            final_totals[method][PCT] += col_totals[method][col_mode][PCT]
            if method == 'orig_val':
                table += f'\\textbf{{{int(col_totals[method][col_mode][CNT])} ({round(col_totals[method][col_mode][PCT], 1)}\\%)}} \\\\'
            else:
                table += f'{int(col_totals[method][col_mode][CNT])} ({round(col_totals[method][col_mode][PCT], 1)}\\%) \\\\'
        table += '}'
    table += '      & \\makecell[l]{'
    for method in methods:
        if method == 'orig_val':
            table += f'\\textbf{{{int(final_totals[method][CNT])} ({round(final_totals[method][PCT], 1)}\\%)}} \\\\'
        else:
            table += f'{int(final_totals[method][CNT])} ({round(final_totals[method][PCT], 1)}\\%)  \\\\'
    table += '} \\\\ \n'
    table += '''
      \\bottomrule
      \\end{tabular}
      \\end{small}
      \\caption{Table 1 from the paper showing the counts and percentages for the original data and the three anonymization methods. Each group of four presents the data in order of Original (bold), SynDiffix, ARX, and SDV.}
      \\label{tab:table1}
      \\end{center}
      \\end{table}
    '''
    with open(os.path.join('results', 'tables', 'table1.tex'), 'w') as f:
        f.write(table)

figs_tabs = [
    'table1',
    'table2',
    'abs_err_tab1_tab2',
]

make_table1()
make_table2()
make_figure_abs_err()

# Create a complete LaTeX document
doc = '''\\documentclass{article}
\\usepackage[utf8]{inputenc}
\\usepackage{makecell}
\\usepackage{booktabs}
\\usepackage{multirow}
\\usepackage[left=2cm,right=2cm]{geometry}
\\usepackage{graphicx}

\\graphicspath{{figs/}}
\\DeclareGraphicsExtensions{.png,.pdf}


\\begin{document}
'''
for fig_tab in figs_tabs:
    doc += f'\\input{{{fig_tab}}}\n'

doc += '\\end{document}\n'
doc_path = os.path.join('results', 'tables', 'figs_and_docs.tex')
with open(doc_path, 'w') as f:
    f.write(doc)

quit()
result = subprocess.run(["pdflatex", doc_path], capture_output=True, text=True)

# Check if compilation was successful
if result.returncode == 0:
    print("Compilation successful.")
    print(result.stdout)
else:
    print("Compilation failed.")
    print(result.stderr)
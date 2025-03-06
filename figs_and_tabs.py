import pandas as pd
import os
import shutil
import subprocess
import matplotlib.pyplot as plt
from syndiffix import SyndiffixBlobReader

import pandas as pd
import numpy as np

def write_table(table, name):
    with open(os.path.join('results', 'tables', name), 'w') as f:
        f.write(table)

def my_savefig(plt, name):
    plt.savefig(os.path.join('results', 'tables', f'{name}.png'))
    plt.savefig(os.path.join('results', 'tables', 'figs', f'{name}.pdf'))

def get_count_color(orig, syn):
    if not isinstance(syn, (int, float, complex, np.number)):
        return 'color-very-bad'
    abs_err = abs(orig - syn)
    rel_err = abs_err / max(abs(orig), abs(syn))
    if abs_err < 5 or rel_err < 0.05:
        return 'color-good'
    elif abs_err < 10 or rel_err < 0.15:
        return 'color-good'
        #return 'color-abit'
    elif abs_err < 20 or rel_err < 0.3:
        return 'color-bad'
    else:
        return 'color-very-bad'

star0 = '\phantom{***}'
star1 = '*\phantom{**}'
star2 = '**\phantom{*}'
star3 = '***'
def get_star_color(orig, syn):
    if (syn == star0 and orig != star0) or (syn != star0 and orig == star0):
        # one is significant and the other is not
        return 'color-very-bad'
    if (syn == star1 and orig == star3) or (syn == star3 and orig == star1):
        # both significant, but off by 2 *'s
        # there is only one of these in the commute dataset, so decided to ignore it
        return 'color-good'
        #return 'color-bad'
    return 'color-good'

def get_rel_color(orig, syn):
    if not isinstance(syn, (int, float, complex, np.number)):
        return 'color-very-bad'
    rel_err = abs(orig-syn) / max(abs(orig), abs(syn))
    if rel_err < 0.05:
        return 'color-good'
    elif rel_err < 0.15:
        return 'color-good'
        #return 'color-abit'
    elif rel_err < 0.3:
        return 'color-bad'
    else:
        return 'color-very-bad'

macros = [
    {'method': 'orig_val', 'color': 'color-good', 'macro': 'orig'},
    {'method': 'arx_val', 'color': 'color-good', 'macro': 'arxg'},
    {'method': 'arx_val', 'color': 'color-bad', 'macro': 'arxb'},
    {'method': 'arx_val', 'color': 'color-very-bad', 'macro': 'arxvb'},
    {'method': 'sdv_val', 'color': 'color-good', 'macro': 'sdvg'},
    {'method': 'sdv_val', 'color': 'color-bad', 'macro': 'sdvb'},
    {'method': 'sdv_val', 'color': 'color-very-bad', 'macro': 'sdvvb'},
    {'method': 'sdx_val', 'color': 'color-good', 'macro': 'sdxg'},
    {'method': 'sdx_val', 'color': 'color-bad', 'macro': 'sdxb'},
    {'method': 'sdx_val', 'color': 'color-very-bad', 'macro': 'sdxvb'},
]

def get_macro_color(method, color):
    for macro in macros:
        if macro['method'] == method and macro['color'] == color:
            return macro['macro']
    return 'orig'

def get_macro_font(method, color):
    if color == 'color-good':
        return 'textnormal'
    elif color == 'color-bad':
        return 'textit'
    elif color == 'color-very-bad':
        return 'textbf'
    else:
        print(f'Error: color {color} not recognized')
        quit()

def set_prt_class(df):
    xx = ['orig', 'arx', 'sdv', 'sdx']
    # Initialize the new columns
    for x in xx:
        df[f'{x}_p'] = -1
    
    def classify(val):
        if val <= 0.001:
            return 3
        elif val <= 0.01:
            return 2
        elif val <= 0.05:
            return 1
        else:
            return 0
    
    mask = df['val_type'] == 'prt'
    for x in xx:
        df.loc[mask, f'{x}_p'] = df.loc[mask, f'{x}_val'].apply(classify)
        df[f'{x}_p'] = df[f'{x}_p'].astype(int)
    return df

# Get the original and synthetic data
blobDir = os.path.join('synDiffix', 'datasets')
sbr = SyndiffixBlobReader(blob_name='commute', path_to_dir=blobDir, cache_df_in_memory=True, force=True)
df_orig = pd.read_csv('CommDataOrig.csv', index_col=False)
print(list(df_orig.columns))
df_orig = df_orig.loc[:, ~df_orig.columns.str.contains('^Unnamed')]
total_rows = len(df_orig)
commute_modes = list(df_orig['CommToSch'].unique())
df_sdv = pd.read_parquet(os.path.join('SDV', 'datasets', 'syn_dataset.parquet'))
df_arx = pd.read_parquet(os.path.join('ARX', 'datasets', 'syn_dataset.parquet'))

# Copy the figures made with CommCode.R to the results/tables/figs directory
for filename in ['r_orig_plot.png', 'r_arx_plot.png', 'r_sdv_plot.png', 'r_sdx_plot.png']:
    shutil.copy(os.path.join('results', filename), os.path.join('results', 'tables', 'figs', filename))

def change_modes(df):
    changes = [['car','Car'], ['public','Public'], ['wheels','Wheels'], ['walk','Walk']]
    for change in changes:
        for column in df.columns:
            df[column] = df[column].replace(change[0], change[1], regex=True)
    return df

# Read in results/paper_values.json as a DataFrame
df = pd.read_json(os.path.join('results', 'paper_values.json'))
df = set_prt_class(df)
df_filtered = df[df['val_type'] == 'prt']
pd.set_option('display.max_columns', None)
print(df_filtered.head(5))
methods = ['orig_val', 'arx_val', 'sdv_val', 'sdx_val']

df = change_modes(df)
df_sdv = change_modes(df_sdv)
df_arx = change_modes(df_arx)
df_orig = change_modes(df_orig)
modes = ['Car', 'Public', 'Wheels', 'Walk']

def make_vo2max_grid():

    latex_code = r"""

    \begin{figure}[htbp]
        \centering
        \begin{subfigure}[b]{0.48\textwidth}
            \centering
            \includegraphics[width=\textwidth]{figs/r_orig_plot.png}
            \caption{Original Plot}
            \label{fig:r_orig_plot}
        \end{subfigure}
        \hspace{0.0\textwidth}
        \begin{subfigure}[b]{0.48\textwidth}
            \centering
            \includegraphics[width=\textwidth]{figs/r_arx_plot.png}
            \caption{ARX Plot}
            \label{fig:r_arx_plot}
        \end{subfigure}
        \vfill
        \begin{subfigure}[b]{0.48\textwidth}
            \centering
            \includegraphics[width=\textwidth]{figs/r_sdv_plot.png}
            \caption{SDV Plot}
            \label{fig:r_sdv_plot}
        \end{subfigure}
        \hspace{0.0\textwidth}
        \begin{subfigure}[b]{0.48\textwidth}
            \centering
            \includegraphics[width=\textwidth]{figs/r_sdx_plot.png}
            \caption{SynDiffix Plot}
            \label{fig:r_sdx_plot}
        \end{subfigure}

        \caption{Comparison of the VO2max data. Here we see that ARX matches very closely with the original data. SynDiffix is quite close for female, but for reasons I don't understand yet, does somewhat bad for the car commute for males. Otherwise, though SynDiffix is pretty good. SDV is again quite bad. What will be important is whether the correct conclusions can be drown from the data in spite of the error.
        }
        \label{fig:comparison_plots}
    \end{figure}

    """

    write_table(latex_code, 'r_plots.tex')

def make_figure_median_plots():
    # These are the columns we'll use for the syndiffix plots
    working_columns = ['CommToSch', 'DistFromHome']
    df_sdx = sbr.read(columns=working_columns, target_column=None)
    df_sdx = change_modes(df_sdx)

    # Assuming df_orig, df_sdx, df_arx are already defined and modes is a list of CommToSch values

    dataframes = {
        'Original': df_orig,
        'ARX': df_arx,
        'SynDiffix': df_sdx,
    }

    fig, axs = plt.subplots(1, 5, figsize=(20, 5), sharey=False)

    for i, comm_value in enumerate(modes + ['all']):
        for label, df in dataframes.items():
            if comm_value == 'all':
                df_filtered = df[['CommToSch', 'DistFromHome']]
            else:
                df_filtered = df[df['CommToSch'] == comm_value][['CommToSch', 'DistFromHome']]
            df_filtered = df_filtered.sort_values(by='DistFromHome').reset_index(drop=True)
            
            median_value = df_filtered['DistFromHome'].median()
            
            # Add the median value to the dataframe
            median_row = pd.DataFrame({'CommToSch': [comm_value], 'DistFromHome': [median_value]})
            df_filtered = pd.concat([df_filtered, median_row], ignore_index=True)
            df_filtered = df_filtered.sort_values(by='DistFromHome').reset_index(drop=True)
            
            median_index = df_filtered[df_filtered['DistFromHome'] == median_value].index[0]
            
            axs[i].plot(df_filtered.index, df_filtered['DistFromHome'], label=label, marker='o', markersize=2)
            axs[i].plot(median_index, median_value, 'x', markersize=10, label=f'{label} Median')
        
        axs[i].set_title(f'CommToSch: {comm_value}')
        axs[i].set_xlabel('Index')
        
        # Set y-axis range according to the range of the data for the subplot
        y_min = df_filtered['DistFromHome'].min()
        y_max = df_filtered['DistFromHome'].max()
        axs[i].set_ylim([y_min, y_max])
        
        # Remove y-axis label from all but the leftmost subplot
        if i == 0:
            axs[i].set_ylabel('DistFromHome')
        #else:
            #axs[i].set_yticklabels([])

        axs[i].legend()

    plt.suptitle('DistFromHome by CommToSch')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    my_savefig(plt, 'median_plots')
    plt.close()
    figure = '''
        \\begin{figure}
        \\begin{center}
        \\includegraphics[width=1.0\linewidth]{median_plots}
        \\caption{Distance from home distributions, by commuting type. Median distances marked with an X. I made this plot just to better understand where median distance errors were coming from for SynDiffix. There are two problems for SynDiffix. First, we adjust the "outlier" data points because they strictly speaking might break anonymity. Second, there are very few Wheels datapoints, and SynDiffix struggles with that. 
        }
        \\label{fig:median_plots}
        \\end{center}
        \\end{figure}
    '''
    write_table(figure, 'median_plots.tex')

def make_abs_err_tab1_tab2():
    groups = ['count', 'distance_median', 'distance_iqr']
    titles = ['Counts', 'Median distances (meters)', 'IQR distances (meters)']
    columns = ['arx_abs_err', 'sdv_abs_err', 'sdx_abs_err']
    x_labels = ['ARX', 'SDV', 'SynDiffix']

    fig, axs = plt.subplots(1, 3, figsize=(10, 3), sharey=False)
    for i, group in enumerate(groups):
        df_filtered = df[df['val_type'] == group]
        data_to_plot = df_filtered[columns].dropna()
        axs[i].boxplot(data_to_plot)
        axs[i].set_xticklabels(x_labels)
        axs[i].set_title(titles[i])

    plt.tight_layout(rect=[0, 0, 1, 0.95]) 
    my_savefig(plt, 'abs_err_tab1_tab2')
    plt.close()


def get_low_p(df):
    df1 = df[(df['val_type'] == 'prt') & (df['orig_val'] <= 0.05)]
    df_coeff = df[df['val_type'] == 'coefficient']
    df_filtered = df_coeff.merge(
        df1[['context', 'tab_column', 'tab_row', 'tab_sub_column']],
        on=['context', 'tab_column', 'tab_row', 'tab_sub_column'],
        how='inner'
    )
    return df_filtered

def make_norm_err_tab3_fig1():
    groups = ['coefficient', 'custom', 'fit']
    titles = ['Coefficient (all)', 'Coefficient (p <= 0.05)', 'Fit']
    columns = ['arx_norm_err', 'sdv_norm_err', 'sdx_norm_err']
    x_labels = ['ARX', 'SDV', 'SynDiffix']
    fig, axs = plt.subplots(1, len(groups), figsize=(9, 3), sharey=False)
    for i, group in enumerate(groups):
        if group == 'custom':
            df_filtered = get_low_p(df)
        else:
            df_filtered = df[df['val_type'] == group]
        data_to_plot = df_filtered[columns].dropna()
        axs[i].boxplot(data_to_plot, tick_labels=columns)
        axs[i].set_xticklabels(x_labels)
        axs[i].set_title(titles[i])
    plt.tight_layout()
    my_savefig(plt, 'norm_err_tab3_fig1')
    plt.close()

def make_figure_norm_err_tab3_fig1():
    make_norm_err_tab3_fig1()
    figure = '''
        \\begin{figure}
        \\begin{center}
        \\includegraphics[width=0.65\linewidth]{norm_err_tab3_fig1}
        \\caption{Normalized error for coefficients and fit for Figure~\\ref{fig:comparison_plots}. This reflects the quality we see in Figure~\\ref{fig:comparison_plots}. SynDiffix clearly has more error than ARX.
        }
        \\end{center}
        \\end{figure}
    '''
    write_table(figure, 'norm_err_tab3_fig1.tex')

def make_figure_abs_err():
    make_abs_err_tab1_tab2()
    figure = '''
        \\begin{figure}
        \\begin{center}
        \\includegraphics[width=0.85\linewidth]{abs_err_tab1_tab2}
        \\caption{Absolute error of the three anonymization methods for the counts and distances in Tables~\\ref{tab:table1} and \\ref{tab:table2}. What we see here is that, for counts, SynDiffix is extremely accurate, but ARX is very accurate as well. SynDiffix and ARX are of equal quality for median and IQR distances. SDV is quite bad.
        }
        \\label{fig:abs_err_tab1_tab2}
        \\end{center}
        \\end{figure}
    '''
    write_table(figure, 'abs_err_tab1_tab2.tex')

def make_table3_font():
    dirs = ['From home to school', 'From school to home']

    def make_cell(mode, dir, val_type1, val_type2):
        df1 = df[(df['context'] == 'Table 3') & (df['tab_row'] == mode) & (df['tab_column'] == dir) & (df['val_type'] == val_type1)]
        if len(df1) != 1:
            print(f'Error: df1 has length {len(df1)}, {mode}, {dir}, {val_type1}')
        df2 = df[(df['context'] == 'Table 3') & (df['tab_row'] == mode) & (df['tab_column'] == dir) & (df['val_type'] == val_type2)]
        if len(df2) != 1:
            print(f'Error: df2 has length {len(df2)}, {mode}, {dir}, {val_type2}')
        cell = ' \\makecell[l]{'
        val1_orig = df1.iloc[0]['orig_val']
        val2_orig = df2.iloc[0]['orig_val']
        if val_type2 == 'prt':
            if val2_orig <= 0.001: val2_orig = star3
            elif val2_orig <= 0.01: val2_orig = star2
            elif val2_orig <= 0.05: val2_orig = star1
            else: val2_orig = star0
        for method in methods:
            val1 = df1.iloc[0][method]
            val2 = df2.iloc[0][method]
            op = cma = cp = ''
            if val_type1 == 'ci_low':
                op = '('                  # open paren
                cma = ', '                # comma
                cp = ')'                  # close paren
            val1 = round(val1, 2)
            if val_type2 == 'prt':
                if val2 <= 0.001: val2 = star3
                elif val2 <= 0.01: val2 = star2
                elif val2 <= 0.05: val2 = star1
                else: val2 = star0
                col2 = get_star_color(val2_orig, val2)
            else:
                col2 = 'color-good'
                val2 = round(val2, 2)
            mac1 = get_macro_font(method, col2)
            cell += f'\\{mac1}{{{op}{val1}{cma}{val2}{cp}}} \\\\'
        return cell + '}'
    # ------------------------------------------------------
    table = '''
      \\setlength{\\fboxsep}{0pt}
      \\begin{table}
      \\begin{center}
      \\begin{small}
      \\begin{tabular}{lllll}
      \\toprule
        \\textbf{Variables}
          & \\multicolumn{4}{l}{\\textbf{Adjusted model}} \\\\ \\cline{2-5}
        & \\multicolumn{2}{l}{\\textbf{From home to school}} 
          & \\multicolumn{2}{l}{\\textbf{From school to home}} \\\\ \\cline{2-3} \\cline{4-5}
        & \\textbf{Coefficient} & \\textbf{95\\% CI} & \\textbf{Coefficient} & \\textbf{95\\% CI} \\\\
      \\midrule
    '''
    table += '\\textbf{Constant} '
    table += f'   & {make_cell("Constant", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("Constant", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("Constant", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("Constant", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '\\multicolumn{5}{l}{\\textbf{Commuting group}} \\\\ \n'
    table += '\\quad Car '
    table += f'   & {make_cell("Car", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("Car", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("Car", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("Car", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '& & & & \\\\ \n'
    table += '\\quad Public '
    table += f'   & {make_cell("Public", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("Public", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("Public", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("Public", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '& & & & \\\\ \n'
    table += '\\quad Wheels '
    table += f'   & {make_cell("Wheels", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("Wheels", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("Wheels", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("Wheels", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '\\quad Walk (ref) & & & & \\\\ \n'
    table += '\\multicolumn{5}{l}{\\textbf{Interaction Commuting group x Distance}} \\\\ \n'
    table += '\\quad Car x Distance '
    table += f'   & {make_cell("Car x Distance", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("Car x Distance", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("Car x Distance", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("Car x Distance", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '& & & & \\\\ \n'
    table += '\\quad Public x Distance '
    table += f'   & {make_cell("Public x Distance", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("Public x Distance", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("Public x Distance", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("Public x Distance", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '& & & & \\\\ \n'
    table += '\\quad Wheels x Distance '
    table += f'   & {make_cell("Wheels x Distance", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("Wheels x Distance", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("Wheels x Distance", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("Wheels x Distance", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '& & & & \\\\ \n'
    table += '\\quad Walk x Distance '
    table += f'   & {make_cell("Walk x Distance", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("Walk x Distance", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("Walk x Distance", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("Walk x Distance", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '''
      \\bottomrule
      {\\footnotesize * p $\\leq$ 0.05, \\quad** p $\\leq$ 0.01, \\quad*** p $\\leq$ 0.001}
      \\end{tabular}
      \\end{small}
      \\caption{Part 1 (of 2) of the original paper's Table 3 showing the parameters (regression coefficients) of the linear model for prediction of VO2max by group and distance. \\textbf{Bold font} indcates that the anonymized entry is non-significant where the original data is significant or vice versa. Each group of four presents the data in order of Original, ARX, SDV, and SynDiffix. 
      }
      \\label{tab:table3a}
      \\end{center}
      \\end{table}
      \\setlength{\\fboxsep}{3pt}
    '''
    write_table(table, 'table3a_font.tex')
    # ------------------------------------------------------
    # ------------------------------------------------------
    table = '''
      \\setlength{\\fboxsep}{0pt}
      \\begin{table}
      \\begin{center}
      \\begin{small}
      \\begin{tabular}{lllll}
      \\toprule
        \\textbf{Variables}
          & \\multicolumn{4}{l}{\\textbf{Adjusted model}} \\\\ \\cline{2-5}
        & \\multicolumn{2}{l}{\\textbf{From home to school}} 
          & \\multicolumn{2}{l}{\\textbf{From school to home}} \\\\ \\cline{2-3} \\cline{4-5}
        & \\textbf{Coefficient} & \\textbf{95\\% CI} & \\textbf{Coefficient} & \\textbf{95\\% CI} \\\\
      \\midrule
    '''
    table += '\\textbf{Gender} & & & & \\\\ \n'
    table += '\\quad Males '
    table += f'   & {make_cell("Males", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("Males", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("Males", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("Males", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '\\quad Females (ref) & & & & \\\\ \n'
    table += '\\multicolumn{5}{l}{\\textbf{Interaction Commuting group x Gender}} \\\\ \n'
    table += '\\quad Car x Gender '
    table += f'   & {make_cell("Car x Males", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("Car x Males", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("Car x Males", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("Car x Males", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '& & & & \\\\ \n'
    table += '\\quad Public x Males '
    table += f'   & {make_cell("Public x Males", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("Public x Males", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("Public x Males", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("Public x Males", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '& & & & \\\\ \n'
    table += '\\quad Wheels x Males '
    table += f'   & {make_cell("Wheels x Males", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("Wheels x Males", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("Wheels x Males", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("Wheels x Males", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '\\quad Walk x Males (ref) & & & & \\\\ \n'
    table += '\\textbf{Covariates} & & & & \\\\ \n'
    table += '\\quad MVPA '
    table += f'   & {make_cell("MVPA", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("MVPA", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("MVPA", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("MVPA", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '& & & & \\\\ \n'
    table += '\\quad Age '
    table += f'   & {make_cell("Age", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("Age", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("Age", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("Age", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '''
      \\bottomrule
      {\\footnotesize * p $\\leq$ 0.05, \\quad** p $\\leq$ 0.01, \\quad*** p $\\leq$ 0.001}
      \\end{tabular}
      \\end{small}
      \\caption{Part 2 (of 2) of the original paper's Table 3 showing the parameters (regression coefficients) of the linear model for prediction of VO2max by group and distance. \\textbf{Bold font} indcates that the anonymized entry is non-significant where the original data is significant or vice versa. Each group of four presents the data in order of Original, ARX, SDV, and SynDiffix. 
      }
      \\label{tab:table3b}
      \\end{center}
      \\end{table}
      \\setlength{\\fboxsep}{3pt}
    '''
    write_table(table, 'table3b_font.tex')
    # ------------------------------------------------------

def make_table3_color():
    dirs = ['From home to school', 'From school to home']

    def make_cell(mode, dir, val_type1, val_type2):
        df1 = df[(df['context'] == 'Table 3') & (df['tab_row'] == mode) & (df['tab_column'] == dir) & (df['val_type'] == val_type1)]
        if len(df1) != 1:
            print(f'Error: df1 has length {len(df1)}, {mode}, {dir}, {val_type1}')
        df2 = df[(df['context'] == 'Table 3') & (df['tab_row'] == mode) & (df['tab_column'] == dir) & (df['val_type'] == val_type2)]
        if len(df2) != 1:
            print(f'Error: df2 has length {len(df2)}, {mode}, {dir}, {val_type2}')
        cell = ' \\makecell[l]{'
        val1_orig = df1.iloc[0]['orig_val']
        val2_orig = df2.iloc[0]['orig_val']
        if val_type2 == 'prt':
            if val2_orig <= 0.001: val2_orig = star3
            elif val2_orig <= 0.01: val2_orig = star2
            elif val2_orig <= 0.05: val2_orig = star1
            else: val2_orig = star0
        for method in methods:
            val1 = df1.iloc[0][method]
            val2 = df2.iloc[0][method]
            op = cma = cp = ''
            if val_type1 == 'ci_low':
                op = '('                  # open paren
                cma = ', '                # comma
                cp = ')'                  # close paren
            val1 = round(val1, 2)
            if val_type2 == 'prt':
                if val2 <= 0.001: val2 = star3
                elif val2 <= 0.01: val2 = star2
                elif val2 <= 0.05: val2 = star1
                else: val2 = star0
                col2 = get_star_color(val2_orig, val2)
            else:
                col2 = 'color-good'
                val2 = round(val2, 2)
            mac1 = get_macro_color(method, col2)
            cell += f'\\{mac1}{{{op}{val1}{cma}{val2}{cp}}} \\\\'
        return cell + '}'
    # ------------------------------------------------------
    table = '''
      \\setlength{\\fboxsep}{0pt}
      \\begin{table}
      \\begin{center}
      \\begin{small}
      \\begin{tabular}{lllll}
      \\toprule
        \\textbf{Variables}
          & \\multicolumn{4}{l}{\\textbf{Adjusted model}} \\\\ \\cline{2-5}
        & \\multicolumn{2}{l}{\\textbf{From home to school}} 
          & \\multicolumn{2}{l}{\\textbf{From school to home}} \\\\ \\cline{2-3} \\cline{4-5}
        & \\textbf{Coefficient} & \\textbf{95\\% CI} & \\textbf{Coefficient} & \\textbf{95\\% CI} \\\\
      \\midrule
    '''
    table += '\\textbf{Constant} '
    table += f'   & {make_cell("Constant", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("Constant", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("Constant", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("Constant", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '\\multicolumn{5}{l}{\\textbf{Commuting group}} \\\\ \n'
    table += '\\quad Car '
    table += f'   & {make_cell("Car", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("Car", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("Car", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("Car", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '& & & & \\\\ \n'
    table += '\\quad Public '
    table += f'   & {make_cell("Public", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("Public", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("Public", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("Public", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '& & & & \\\\ \n'
    table += '\\quad Wheels '
    table += f'   & {make_cell("Wheels", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("Wheels", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("Wheels", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("Wheels", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '\\quad Walk (ref) & & & & \\\\ \n'
    table += '\\multicolumn{5}{l}{\\textbf{Interaction Commuting group x Distance}} \\\\ \n'
    table += '\\quad Car x Distance '
    table += f'   & {make_cell("Car x Distance", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("Car x Distance", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("Car x Distance", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("Car x Distance", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '& & & & \\\\ \n'
    table += '\\quad Public x Distance '
    table += f'   & {make_cell("Public x Distance", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("Public x Distance", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("Public x Distance", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("Public x Distance", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '& & & & \\\\ \n'
    table += '\\quad Wheels x Distance '
    table += f'   & {make_cell("Wheels x Distance", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("Wheels x Distance", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("Wheels x Distance", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("Wheels x Distance", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '& & & & \\\\ \n'
    table += '\\quad Walk x Distance '
    table += f'   & {make_cell("Walk x Distance", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("Walk x Distance", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("Walk x Distance", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("Walk x Distance", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '''
      \\bottomrule
      {\\footnotesize * p $\\leq$ 0.05, \\quad** p $\\leq$ 0.01, \\quad*** p $\\leq$ 0.001}
      \\end{tabular}
      \\end{small}
      \\caption{Part 1 (of 2) of the original paper's Table 3 showing the parameters (regression coefficients) of the linear model for prediction of VO2max by group and distance. \\colorbox{color-very-bad}{Red} shading indcates that the anonymized entry is non-significant where the original data is significant or vice versa. Each group of four presents the data in order of Original (bold), ARX, SDV, and SynDiffix. 
      }
      \\label{tab:table3a}
      \\end{center}
      \\end{table}
      \\setlength{\\fboxsep}{3pt}
    '''
    write_table(table, 'table3a_color.tex')
    # ------------------------------------------------------
    # ------------------------------------------------------
    table = '''
      \\setlength{\\fboxsep}{0pt}
      \\begin{table}
      \\begin{center}
      \\begin{small}
      \\begin{tabular}{lllll}
      \\toprule
        \\textbf{Variables}
          & \\multicolumn{4}{l}{\\textbf{Adjusted model}} \\\\ \\cline{2-5}
        & \\multicolumn{2}{l}{\\textbf{From home to school}} 
          & \\multicolumn{2}{l}{\\textbf{From school to home}} \\\\ \\cline{2-3} \\cline{4-5}
        & \\textbf{Coefficient} & \\textbf{95\\% CI} & \\textbf{Coefficient} & \\textbf{95\\% CI} \\\\
      \\midrule
    '''
    table += '\\textbf{Gender} & & & & \\\\ \n'
    table += '\\quad Males '
    table += f'   & {make_cell("Males", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("Males", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("Males", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("Males", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '\\quad Females (ref) & & & & \\\\ \n'
    table += '\\multicolumn{5}{l}{\\textbf{Interaction Commuting group x Gender}} \\\\ \n'
    table += '\\quad Car x Gender '
    table += f'   & {make_cell("Car x Males", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("Car x Males", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("Car x Males", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("Car x Males", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '& & & & \\\\ \n'
    table += '\\quad Public x Males '
    table += f'   & {make_cell("Public x Males", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("Public x Males", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("Public x Males", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("Public x Males", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '& & & & \\\\ \n'
    table += '\\quad Wheels x Males '
    table += f'   & {make_cell("Wheels x Males", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("Wheels x Males", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("Wheels x Males", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("Wheels x Males", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '\\quad Walk x Males (ref) & & & & \\\\ \n'
    table += '\\textbf{Covariates} & & & & \\\\ \n'
    table += '\\quad MVPA '
    table += f'   & {make_cell("MVPA", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("MVPA", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("MVPA", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("MVPA", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '& & & & \\\\ \n'
    table += '\\quad Age '
    table += f'   & {make_cell("Age", dirs[0], "coefficient", "prt")}'
    table += f'   & {make_cell("Age", dirs[0], "ci_low", "ci_high")}'
    table += f'   & {make_cell("Age", dirs[1], "coefficient", "prt")}'
    table += f'   & {make_cell("Age", dirs[1], "ci_low", "ci_high")}'
    table += ' \\\\ \n'
    table += '''
      \\bottomrule
      {\\footnotesize * p $\\leq$ 0.05, \\quad** p $\\leq$ 0.01, \\quad*** p $\\leq$ 0.001}
      \\end{tabular}
      \\end{small}
      \\caption{Part 2 (of 2) of the original paper's Table 3 showing the parameters (regression coefficients) of the linear model for prediction of VO2max by group and distance. \\colorbox{color-very-bad}{Red} shading indcates that the anonymized entry is non-significant where the original data is significant or vice versa. Each group of four presents the data in order of Original (bold), ARX, SDV, and SynDiffix. 
      }
      \\label{tab:table3b}
      \\end{center}
      \\end{table}
      \\setlength{\\fboxsep}{3pt}
    '''
    write_table(table, 'table3b_color.tex')
    # ------------------------------------------------------

def make_table2_font():
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
        val1_orig = df1.iloc[0]['orig_val']
        val2_orig = df2.iloc[0]['orig_val']
        for method in methods:
            p = '\\%' if val_type2 == 'percent' else ''
            val1 = df1.iloc[0][method]
            col1 = get_count_color(val1_orig, val1) if val_type2 == 'percent' else get_rel_color(val1_orig, val1)
            if p == '\\%': col_totals[method][dir][0] += val1
            val1 = int(val1)
            mac1 = get_macro_font(method, col1)
            val2 = df2.iloc[0][method]
            col2 = get_rel_color(val2_orig, val2)
            mac2 = get_macro_font(method, col2)
            if p == '\\%': col_totals[method][dir][1] += val2
            val2 = round(val2)
            cell += f'\\{mac1}{{{val1}}} \\{mac2}{{({val2}{p})}} \\\\'
        return cell + '}'

    table = '''
      \\setlength{\\fboxsep}{0pt}
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
            cells[i] += f'{int(col_totals[method][dir][0])} ({round(col_totals[method][dir][1])}\\%) \\\\'
        cells[i] += '}'
    table += '      Total ' + cells[0] + ' & ' + cells[1] + ' & \\\\ \n'

    table += '''
      \\bottomrule
      \\end{tabular}
      \\end{small}
      \\caption{Base-table 2 from the original paper showing the counts and distances in meters (median and IQR) for the original data and the three anonymization methods. Each group of four presents the data in order of Original, ARX, SDV, and SynDiffix. The shading for counts (N) are as described for Table~\\ref{tab:table1}. Distance and IRQ are \\textbf{bold font} when the relative error is greater than 30\\%, and \\textit{italics} when the relative error is greater than 15\\%.  Note that the original distances median and IQR don't perfectly match those of the original Table 2 because of differences in the way median and IQR were calculated (Python versus R).}
      \\label{tab:table2}
      \\end{center}
      \\end{table}
      \\setlength{\\fboxsep}{3pt}
    '''
    write_table(table, 'table2_font.tex')

def make_table2_color():
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
        val1_orig = df1.iloc[0]['orig_val']
        val2_orig = df2.iloc[0]['orig_val']
        for method in methods:
            p = '\\%' if val_type2 == 'percent' else ''
            val1 = df1.iloc[0][method]
            col1 = get_count_color(val1_orig, val1) if val_type2 == 'percent' else get_rel_color(val1_orig, val1)
            if p == '\\%': col_totals[method][dir][0] += val1
            val1 = int(val1)
            mac1 = get_macro_color(method, col1)
            val2 = df2.iloc[0][method]
            col2 = get_rel_color(val2_orig, val2)
            mac2 = get_macro_color(method, col2)
            if p == '\\%': col_totals[method][dir][1] += val2
            val2 = round(val2)
            cell += f'\\{mac1}{{{val1}}} \\{mac2}{{({val2}{p})}} \\\\'
        return cell + '}'

    table = '''
      \\setlength{\\fboxsep}{0pt}
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
      \\caption{Base-table 2 from the original paper showing the counts and distances in meters (median and IQR) for the original data and the three anonymization methods. Each group of four presents the data in order of Original (bold), ARX, SDV, and SynDiffix. The shading for counts (N) are as described for Table~\\ref{tab:table1}. Distance and IRQ are shaded \\colorbox{color-very-bad}{red} when the relative error is greater than 30\\%, and shaded \\colorbox{color-bad}{orange} when the relative error is greater than 15\\%.  Note that the original distances median and IQR don't perfectly match those of the original Table 2 because of differences in the way median and IQR were calculated (Python versus R).}
      \\label{tab:table2}
      \\end{center}
      \\end{table}
      \\setlength{\\fboxsep}{3pt}
    '''
    write_table(table, 'table2_color.tex')

def make_table1_font():
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
        count_orig = df_count.iloc[0]['orig_val']
        for method in methods:
            count = df_count.iloc[0][method]
            col_count = get_count_color(count_orig, count)
            mac = get_macro_font(method, col_count)
            row_totals[method][CNT] += count
            col_totals[method][col_mode][CNT] += count
            count = int(count)
            percent = df_percent.iloc[0][method]
            row_totals[method][PCT] += percent
            col_totals[method][col_mode][PCT] += percent
            percent = round(percent, 1)
            cell += f'\\{mac}{{{count} ({percent}\\%)}} \\\\'
        return cell[:-3] + '}'

    table = '''
      \\setlength{\\fboxsep}{0pt}
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
            table += f'{int(col_totals[method][col_mode][CNT])} ({round(col_totals[method][col_mode][PCT], 1)}\\%) \\\\'
        table += '}'
    table += '      & \\makecell[l]{'
    for method in methods:
        table += f'{int(final_totals[method][CNT])} ({round(final_totals[method][PCT], 1)}\\%)  \\\\'
    table += '} \\\\ \n'
    table += '''
      \\bottomrule
      \\end{tabular}
      \\end{small}
      \\caption{Base-table 1 from the paper showing the counts and percentages for the original data and the three anonymization methods. Each group of four presents the data in order of Original, ARX, SDV, and SynDiffix. Counts and their corresponding percentages are \\textbf{bold font} when the absolute error is greater than 20 or the relative error is greater than 30\\%. They are \\textit{italic} when the absolute error is greater than 10 or the relative error is greater than 15\\%.}
      \\label{tab:table1}
      \\end{center}
      \\end{table}
      \\setlength{\\fboxsep}{3pt}
    '''
    write_table(table, 'table1_font.tex')

def make_table1_color():
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
        count_orig = df_count.iloc[0]['orig_val']
        for method in methods:
            count = df_count.iloc[0][method]
            col_count = get_count_color(count_orig, count)
            mac = get_macro_color(method, col_count)
            row_totals[method][CNT] += count
            col_totals[method][col_mode][CNT] += count
            count = int(count)
            percent = df_percent.iloc[0][method]
            row_totals[method][PCT] += percent
            col_totals[method][col_mode][PCT] += percent
            percent = round(percent, 1)
            cell += f'\\{mac}{{{count} ({percent}\\%)}} \\\\'
        return cell[:-3] + '}'

    table = '''
      \\setlength{\\fboxsep}{0pt}
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
      \\caption{Base-table 1 from the paper showing the counts and percentages for the original data and the three anonymization methods. Each group of four presents the data in order of Original (bold), ARX, SDV, and SynDiffix. Counts and their corresponding percentages are shaded \\colorbox{color-very-bad}{red} when the absolute error is greater than 20 or the relative error is greater than 30\\%. They are shaded \\colorbox{color-bad}{orange} when the absolute error is greater than 10 or the relative error is greater than 15\\%.}
      \\label{tab:table1}
      \\end{center}
      \\end{table}
      \\setlength{\\fboxsep}{3pt}
    '''
    write_table(table, 'table1_color.tex')

def make_p_table():
    count_prt = (df['val_type'] == 'prt').sum()
    count_small_p = ((df['val_type'] == 'prt') & (df['orig_p'] > 0)).sum()
    count_big_p = count_prt - count_small_p
    xx = ['arx', 'sdv', 'sdx']
    pdata = {}
    for x in xx:
        small_match = ((df['orig_p'] > 0) & (df[f'{x}_p'] > 0)).sum()
        big_match = ((df['orig_p'] == 0) & (df[f'{x}_p'] == 0)).sum()
        exact_small = ((df['orig_p'] > 0) & (df['orig_p'] == df[f'{x}_p'])).sum()
        small_off_1 = ((df['orig_p'] > 0) & (df[f'{x}_p'] > 0) & ((abs(df['orig_p'] - df[f'{x}_p'])) == 1)).sum()
        small_off_2 = ((df['orig_p'] > 0) & (df[f'{x}_p'] > 0) & ((abs(df['orig_p'] - df[f'{x}_p'])) == 2)).sum()
        pdata[x] = {
            'small_match': small_match,
            'big_match': big_match,
            'exact_small': exact_small,
            'small_off_1': small_off_1,
            'small_off_2': small_off_2,
            'small_match_per': round(100 * (small_match / count_small_p)),
            'big_match_per': round(100 * (big_match / count_big_p)),
            'exact_small_per': round(100 * (exact_small / count_small_p)),
            'small_off_1_per': round(100 * (small_off_1 / count_small_p)),
            'small_off_2_per': round(100 * (small_off_2 / count_small_p)),
        }
    table = '''
      \\setlength{\\fboxsep}{0pt}
      \\begin{table}
      \\begin{center}
      \\begin{small}
      \\begin{tabular}{llll}
      \\toprule
        & ARX & SDV & SynDiffix \\\\
      \\midrule
    '''
    table += f'    Of the original {count_small_p} significant p-values, method is also significat '
    for x in xx:
        table += f' & {pdata[x]["small_match"]} ({pdata[x]["small_match_per"]}\\%) '
    table += ' \\\\ \n'
    table += f'    Of the original {count_big_p} insignificant p-values, method is also insignificat '
    for x in xx:
        table += f' & {pdata[x]["big_match"]} ({pdata[x]["big_match_per"]}\\%) '
    table += ' \\\\ \n'
    table += f'    Of the original {count_small_p} significant p-values, method matches '
    for x in xx:
        table += f' & {pdata[x]["exact_small"]} ({pdata[x]["exact_small_per"]}\\%) '
    table += ' \\\\ \n'
    table += f'    Of the original {count_small_p} significant p-values, method off by 1 '
    for x in xx:
        table += f' & {pdata[x]["small_off_1"]} ({pdata[x]["small_off_1_per"]}\\%) '
    table += ' \\\\ \n'
    table += f'    Of the original {count_small_p} significant p-values, method off by 2 '
    for x in xx:
        table += f' & {pdata[x]["small_off_2"]} ({pdata[x]["small_off_2_per"]}\\%) '
    table += ' \\\\ \n'
    table += '''
      \\bottomrule
      \\end{tabular}
      \\end{small}
      \\caption{Error between each method's p-values and the original p-values. P-values are significant when $p \\leq 0.05$. P-values are binned as $p \\leq 0.001$, $0.001 < p \\leq 0.01$, and $0.01 < p \\leq 0.05$. Off by 1 means that the method's bin is one off from the original data's bin (both being significant). Off by 2 means that the method's bin is two off from the original data's bin.
      }
      \\label{tab:p_table}
      \\end{center}
      \\end{table}
      \\setlength{\\fboxsep}{3pt}
    '''
    write_table(table, 'p_table.tex')

figs_tabs = [
    'table1',
    'table2',
    'table3a',
    'table3b',
    'abs_err_tab1_tab2',
    'r_plots',
    'norm_err_tab3_fig1',
    'p_table',
    'median_plots'
]

make_table1_color()
make_table1_font()
make_table2_color()
make_table2_font()
make_table3_color()
make_table3_font()
make_p_table()
make_figure_abs_err()
make_figure_median_plots()
make_vo2max_grid()
make_figure_norm_err_tab3_fig1()

# Create a complete LaTeX document
doc = '''\\documentclass{article}
\\usepackage[utf8]{inputenc}
\\usepackage{makecell}
\\usepackage{booktabs}
\\usepackage{multirow}
\\usepackage[left=2cm,right=2cm]{geometry}
\\usepackage{graphicx}
\\usepackage{caption}
\\usepackage{subcaption}
\\usepackage{longtable}
\\usepackage[dvipsnames]{xcolor}


\\graphicspath{{figs/}}
\\DeclareGraphicsExtensions{.png,.pdf}

\\definecolor{color-bad}{rgb}{1, 0.9, 0.8}
\\definecolor{color-very-bad}{rgb}{1, 0.7, 0.7}
\\definecolor{color-abit}{rgb}{1, 1, 0.8}      % legacy, not used
\\definecolor{color-good}{rgb}{1, 1, 1}     % this is white


\\newcommand{\\completeexample}[1]{%
  \\textbf{\\textit{\\uline{\\textcolor{color-very-bad}{\\colorbox{color-bad}{#1}}}}}%
}
\\newcommand{\\orig}[1]{%
  \\textbf{\\textcolor{black}{\\colorbox{color-good}{#1}}}%
}
\\newcommand{\\arxg}[1]{%
  \\textnormal{\\textcolor{black}{\\colorbox{color-good}{#1}}}%
}
\\newcommand{\\arxb}[1]{%
  \\textnormal{\\textcolor{black}{\\colorbox{color-bad}{#1}}}%
}
\\newcommand{\\arxvb}[1]{%
  \\textnormal{\\textcolor{black}{\\colorbox{color-very-bad}{#1}}}%
}
\\newcommand{\\sdvg}[1]{%
  \\textnormal{\\textcolor{black}{\\colorbox{color-good}{#1}}}%
}
\\newcommand{\\sdvb}[1]{%
  \\textnormal{\\textcolor{black}{\\colorbox{color-bad}{#1}}}%
}
\\newcommand{\\sdvvb}[1]{%
  \\textnormal{\\textcolor{black}{\\colorbox{color-very-bad}{#1}}}%
}
\\newcommand{\\sdxg}[1]{%
  \\textnormal{\\textcolor{black}{\\colorbox{color-good}{#1}}}%
}
\\newcommand{\\sdxb}[1]{%
  \\textnormal{\\textcolor{black}{\\colorbox{color-bad}{#1}}}%
}
\\newcommand{\\sdxvb}[1]{%
  \\textnormal{\\textcolor{black}{\\colorbox{color-very-bad}{#1}}}%
}



\\begin{document}
'''
for fig_tab in figs_tabs:
    doc += f'\\input{{{fig_tab}}}\n'

doc += '\\end{document}\n'
doc_path = os.path.join('results', 'tables', 'figs_and_tabs.tex')
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
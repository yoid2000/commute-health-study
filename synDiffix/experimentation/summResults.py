import os
import json
import pprint
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def get_diffs(method, df_orig, df):
    # Check if df_orig and df have the same columns
    if not df_orig.columns.equals(df.columns):
        raise ValueError("df_orig and df must have the same columns")
    
    # Check if df_orig and df have the same number of rows
    if len(df_orig) != len(df):
        raise ValueError("df_orig and df must have the same number of rows")

    # Initialize the dictionary to return
    result = {
        'method': method,
        'num_in_bounds': 0,
        'abs_err_avg': None,
        'abs_err_sd': None,
        'abs_err_max': None,
        'abs_err_min': None
    }
    
    # Initialize num_in_bounds and abs_err list
    num_in_bounds = 0
    abs_err = []
    
    # Iterate over each row in df
    for _, row in df.iterrows():
        # Find the corresponding row in df_orig
        row_orig = df_orig[(df_orig['comm'] == row['comm']) & 
                           (df_orig['mode'] == row['mode']) & 
                           (df_orig['gender'] == row['gender'])]
        
        if row_orig.empty:
            raise ValueError("Matching row not found in df_orig")
        
        row_orig = row_orig.iloc[0]  # Get the first matching row
        
        # Check if 'fit' is between 'lwr' and 'upr' in row_orig
        if row_orig['lwr'] <= row['fit'] <= row_orig['upr']:
            num_in_bounds += 1
        
        # Compute the absolute error and append to abs_err list
        abs_error = abs(row['fit'] - row_orig['fit'])
        abs_err.append({'method': method, 'abs_err': abs_error})

    # Set the values in the result dictionary
    result['num_in_bounds'] = num_in_bounds
    result['abs_err_avg'] = np.mean([entry['abs_err'] for entry in abs_err])
    result['abs_err_sd'] = np.std([entry['abs_err'] for entry in abs_err])
    result['abs_err_max'] = np.max([entry['abs_err'] for entry in abs_err])
    result['abs_err_min'] = np.min([entry['abs_err'] for entry in abs_err])
    
    return result, abs_err

def pull_conf_data(data_dict):
    # Initialize an empty list to store rows
    rows = []
    
    # Iterate over each key-value pair in the dictionary
    for key, entries in data_dict.items():
        # Iterate over each entry in the list
        for entry in entries:
            # Check if the entry has the key "gender"
            if 'gender' in entry:
                # Determine the value of "comm" and "mode"
                if 'CommToSch' in entry:
                    comm = 'to_school'
                    mode = entry['CommToSch']
                elif 'CommHome' in entry:
                    comm = 'to_home'
                    mode = entry['CommHome']
                else:
                    continue  # Skip the entry if neither CommToSch nor CommHome is present
                
                # Assign values to the row
                row = {
                    'comm': comm,
                    'mode': mode,
                    'gender': entry['gender'],
                    'fit': entry['fit'],
                    'lwr': entry['lwr'],
                    'upr': entry['upr']
                }
                
                # Append the row to the list of rows
                rows.append(row)
    
    # Convert the list of rows to a DataFrame
    df = pd.DataFrame(rows, columns=['comm', 'mode', 'gender', 'fit', 'lwr', 'upr'])
    
    return df

pp = pprint.PrettyPrinter(indent=4)

with open( os.path.join("results", "r_orig.json"), "r") as file:
    orig_data = json.load(file)
    df_orig = pull_conf_data(orig_data)

results = []
abs_errs = []

for file_path in glob.glob(os.path.join("results", "*.json")):
    if file_path.endswith("r_orig.json"):
        continue
    with open(file_path, "r") as file:
        data = json.load(file)
    file_name = os.path.basename(file_path)
    file_name = os.path.splitext(file_name)[0]
    df = pull_conf_data(data)
    result, abs_err = get_diffs(file_name, df_orig, df)
    pp.pprint(result)
    results.append(result)
    abs_errs.extend(abs_err)

df_results = pd.DataFrame(results)
print(len(df_results))
df_abs_err = pd.DataFrame(abs_errs)
print(df_abs_err.head())

# Create a figure with two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

# Left subplot: Bar plot
ax1.barh(df_results['method'], df_results['num_in_bounds'], color='skyblue')
ax1.axvline(x=16, color='red', linestyle='--')
ax1.set_xlabel('num_in_bounds')
ax1.set_ylabel('method')
ax1.set_title('Number in Bounds by Method')

# Right subplot: Boxplot
abs_err_data = [df_abs_err[df_abs_err['method'] == method]['abs_err'].values for method in df_results['method']]

ax2.boxplot(abs_err_data, vert=False, tick_labels=df_results['method'])
ax2.set_xlabel('abs_err')
ax2.set_title('Absolute Error by Method')
ax2.grid()

# Adjust layout
plt.tight_layout()

# Save the plot
output_path = os.path.join('results', 'summary.png')
os.makedirs(os.path.dirname(output_path), exist_ok=True)
plt.savefig(output_path)
plt.close()
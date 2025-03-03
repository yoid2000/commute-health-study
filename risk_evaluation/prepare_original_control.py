import pandas as pd
from sklearn.model_selection import train_test_split

# File paths
input_file = "../CommDataOrig.csv"
original_file = "../CommDataOrig_original.csv"
control_file = "../CommDataOrig_control.csv"

# Read the input CSV file into a DataFrame
df = pd.read_csv(input_file)

# Split the DataFrame into two parts: 100 rows for control and the rest for original
df_original, df_control = train_test_split(df, test_size=100, random_state=42)
print(f"The new original dataframe has {len(df_original)} rows")
print(f"The new control dataframe has {len(df_control)} rows")

# Write the control DataFrame to the control file
df_control.to_csv(control_file, index=False)

# Write the original DataFrame to the original file
df_original.to_csv(original_file, index=False)
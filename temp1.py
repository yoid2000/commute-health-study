import pandas as pd

def remove_columns(csv_path):
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Remove the columns 'DistLog2Home' and 'DistLog2ToSch' if they exist
    df = df.drop(columns=['DistLog2Home', 'DistLog2ToSch'], errors='ignore')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Write the modified DataFrame back to CommDataOrig.csv, overwriting the original file
    df.to_csv(csv_path, index=False)

# Example usage
csv_path = 'CommDataOrig.csv'
remove_columns(csv_path)
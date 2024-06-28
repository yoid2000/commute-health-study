import pandas as pd
import numpy as np

def process_comm_data(csv_path):
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Compute log2 of DistFromSchool and create a new column DistLog2Home
    df['DistLog2Home'] = np.log2(df['DistFromSchool'])
    
    # Compute log2 of DistFromHome and create a new column DistLog2ToSch
    df['DistLog2ToSch'] = np.log2(df['DistFromHome'])
    
    # Write the modified DataFrame back to CommData.csv, overwriting the original file
    df.to_csv(csv_path, index=False)

# Example usage
csv_path = 'CommData.csv'
process_comm_data(csv_path)
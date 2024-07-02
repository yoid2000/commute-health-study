import pandas as pd
import os

def parquet_to_csv(parquet_path, csv_path):
    # Read the Parquet file
    df = pd.read_parquet(parquet_path)
    
    # Write the DataFrame to a CSV file
    df.to_csv(csv_path, index=False)

def csv_to_parquet(csv_path, parquet_path):
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Write the DataFrame to a Parquet file
    df.to_parquet(parquet_path, index=False)

# Example usage
parquet_path = os.path.join('ARX', 'datasets', 'syn_dataset.parquet')
csv_path = os.path.join('ARX', 'datasets', 'syn_dataset.csv')
csv_to_parquet(csv_path, parquet_path)
parquet_path = os.path.join('SDV', 'datasets', 'syn_dataset.parquet')
csv_path = os.path.join('SDV', 'datasets', 'syn_dataset.csv')
csv_to_parquet(csv_path, parquet_path)
import os
import pandas as pd

baseDir = os.environ['COMMUTE_HEALTH_PATH']
print(baseDir)

def parquet_to_csv(ppath, cpath):
    # Read the Parquet file
    df = pd.read_parquet(ppath)
    
    # Write the DataFrame to a CSV file
    df.to_csv(cpath, index=False)

# Example usage
ppath = os.path.join(baseDir, 'tmTables', 'syn','sdx.CommDataOrig.col8.Comm_Comm_Dist_Dist_MVPA_VO2m_age_gend.TAR.VO2max.0vuirf.parquet')
cpath = os.path.join(baseDir, 'tmTables', 'syn','sdx.CommDataOrig.col8.Comm_Comm_Dist_Dist_MVPA_VO2m_age_gend.TAR.VO2max.0vuirf.csv')
parquet_to_csv(ppath, cpath)
ppath = os.path.join(baseDir, 'tmTables', 'syn', 'sdx.CommDataOrig.col8.Comm_Comm_Dist_Dist_MVPA_VO2m_age_gend.gba9yi.parquet')
cpath = os.path.join(baseDir, 'tmTables', 'syn', 'sdx.CommDataOrig.col8.Comm_Comm_Dist_Dist_MVPA_VO2m_age_gend.gba9yi.csv')
parquet_to_csv(ppath, cpath)

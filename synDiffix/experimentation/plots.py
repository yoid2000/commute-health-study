import pandas as pd
import matplotlib.pyplot as plt
import os

def do_plots(df_orig, df_2home, df_2sch, title):
    # Create a figure with two subplots
    fig, axs = plt.subplots(1, 2, figsize=(15, 7))

    # Generate a color map
    unique_comm_home = df_orig['CommHome'].unique()
    unique_comm_to_sch = df_orig['CommToSch'].unique()
    colors_home = plt.get_cmap('tab10', len(unique_comm_home))
    colors_sch = plt.get_cmap('tab10', len(unique_comm_to_sch))

    # Create color dictionaries
    color_dict_home = {comm_home: colors_home(i) for i, comm_home in enumerate(unique_comm_home)}
    color_dict_sch = {comm_to_sch: colors_sch(i) for i, comm_to_sch in enumerate(unique_comm_to_sch)}

    # Left subplot: DistFromSchool
    for comm_home in unique_comm_home:
        df_orig_filtered = df_orig[df_orig['CommHome'] == comm_home]
        sorted_dist_school = df_orig_filtered['DistFromSchool'].sort_values().reset_index(drop=True)
        axs[0].plot(sorted_dist_school, label=f'Orig {comm_home}', color=color_dict_home[comm_home])
        
    for comm_home in df_2home['CommHome'].unique():
        df_2home_filtered = df_2home[df_2home['CommHome'] == comm_home]
        sorted_dist_school = df_2home_filtered['DistFromSchool'].sort_values().reset_index(drop=True)
        axs[0].plot(sorted_dist_school, label=f'2Home {comm_home}', linestyle='--', color=color_dict_home[comm_home])
    
    axs[0].set_title('DistFromSchool')
    axs[0].set_xlabel('Index')
    axs[0].set_ylabel('Distance From School')
    axs[0].legend()
    axs[0].grid(True)

    # Right subplot: DistFromHome
    for comm_to_sch in unique_comm_to_sch:
        df_orig_filtered = df_orig[df_orig['CommToSch'] == comm_to_sch]
        sorted_dist_home = df_orig_filtered['DistFromHome'].sort_values().reset_index(drop=True)
        axs[1].plot(sorted_dist_home, label=f'Orig {comm_to_sch}', color=color_dict_sch[comm_to_sch])
        
    for comm_to_sch in df_2sch['CommToSch'].unique():
        df_2sch_filtered = df_2sch[df_2sch['CommToSch'] == comm_to_sch]
        sorted_dist_home = df_2sch_filtered['DistFromHome'].sort_values().reset_index(drop=True)
        axs[1].plot(sorted_dist_home, label=f'2Sch {comm_to_sch}', linestyle='--', color=color_dict_sch[comm_to_sch])
    
    axs[1].set_title('DistFromHome')
    axs[1].set_xlabel('Index')
    axs[1].set_ylabel('Distance From Home')
    axs[1].legend()
    axs[1].grid(True)

    # Set the overall title
    plt.suptitle(title)

    # Save the plot to a file
    os.makedirs('plots', exist_ok=True)
    plt.savefig(os.path.join('plots', f'{title}.png'))
    plt.close()

df_orig = pd.read_csv('CommDataOrig.csv')

df_2home = pd.read_csv('CommDataSyn_2home.csv')
df_2sch = pd.read_csv('CommDataSyn_2school.csv')
do_plots(df_orig, df_2home, df_2sch, 'mixed_all')

df_2home = pd.read_csv('CommDataSyn_target_VO2max_all.csv')
df_2sch = pd.read_csv('CommDataSyn_target_VO2max_all.csv')
do_plots(df_orig, df_2home, df_2sch, 'all_target')

df_2home = pd.read_csv('CommDataSyn_target_VO2max_2home.csv')
df_2sch = pd.read_csv('CommDataSyn_target_VO2max_2school.csv')
do_plots(df_orig, df_2home, df_2sch, 'mixed_target')

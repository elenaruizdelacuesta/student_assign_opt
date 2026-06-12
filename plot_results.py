import os
import pandas as pd
import matplotlib.pyplot as plt

def create_line_chart(df, x_column, title, xlabel, output_filename):
    """Generates a line chart to show the growth trend."""
    plt.figure(figsize=(10, 6))
    plt.plot(df[x_column], df['Total_Time(s)'], marker='o', linestyle='-', color='#2c3e50', linewidth=2.5, markersize=8)
    plt.title(title, fontsize=14, pad=15)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel('Total Execution Time (seconds)', fontsize=12)
    plt.xticks(df[x_column])
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()

def create_stacked_bar_chart(df, x_column, title, xlabel, output_filename):
    """Generates a stacked bar chart to show the execution time breakdown."""
    plt.figure(figsize=(10, 6))
    
    # Calculate bar width based on the range of x values and number of bars
    bar_width = (df[x_column].max() - df[x_column].min()) / (len(df) * 2)
    if bar_width == 0: bar_width = 1

    plt.bar(df[x_column], df['Time_Step1(s)'], width=bar_width, label='Step 1 (Preferences)', color="#f4b0f6")
    plt.bar(df[x_column], df['Time_Step2(s)'], width=bar_width, bottom=df['Time_Step1(s)'], label='Step 2 (Diversity)', color='#3498db')
    
    bottom_step3 = df['Time_Step1(s)'] + df['Time_Step2(s)']
    plt.bar(df[x_column], df['Time_Step3(s)'], width=bar_width, bottom=bottom_step3, label='Step 3 (Balance)', color="#721195")

    plt.title(title, fontsize=14, pad=15)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel('Execution Time (seconds)', fontsize=12)
    plt.xticks(df[x_column])
    plt.legend(loc='upper left', fontsize=11)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close() 

def generate_plots(mode="equal"):
    """Generates plots for the specified mode (equal or unequal)."""
    
    input_dir = f"results_{mode}"
    output_dir = f"plots_{mode}"
    os.makedirs(output_dir, exist_ok=True)

    mode_title = "Equal-Sized" if mode == "equal" else "Unequal-Sized"

    # =====================================================================
    # EXPERIMENT 1: PROPORTIONAL GROWTH
    # =====================================================================
    df_prop = pd.read_csv(f'{input_dir}/scalability_proportional.csv')
    
    # Line chart
    create_line_chart(df_prop, 'Students', 
                      f'Scalability: Total Time vs. Instance Size (Proportional Growth, {mode_title})', 
                      'Number of Students (|I|) & Proportionally Increasing Seminars', 
                      f'{output_dir}/plot_1_proportional_line.png')

    # Stacked Bar Chart
    create_stacked_bar_chart(df_prop, 'Students', 
                             f'Execution Time Breakdown (Proportional Growth, {mode_title})', 
                             'Number of Students (|I|) & Proportionally Increasing Seminars', 
                             f'{output_dir}/plot_1_proportional_stacked.png')

    # =====================================================================
    # EXPERIMENT 2: FULLER CLASSROOMS
    # =====================================================================
    df_stud = pd.read_csv(f'{input_dir}/scalability_students.csv')
    create_line_chart(df_stud, 'Students',
                      f'Scalability: Total Time vs. Number of Students (Fixed Seminars |J|=5, {mode_title})', 
                      'Number of Students (|I|)', 
                      f'{output_dir}/plot_2_students_line.png')
    create_stacked_bar_chart(df_stud, 'Students', 
                             f'Execution Time Breakdown (Fixed Seminars |J|=5, {mode_title})', 
                             'Number of Students (|I|)', 
                             f'{output_dir}/plot_2_students_stacked.png')

    # =====================================================================
    # EXPERIMENT 3: FRAGMENTATION
    # =====================================================================
    df_sem = pd.read_csv(f'{input_dir}/scalability_seminars.csv')
    create_line_chart(df_sem, 'Seminars',
                      f'Scalability: Total Time vs. Number of Seminars (Fixed Students |I|=60, {mode_title})', 
                      'Number of Seminars (|J|)', 
                      f'{output_dir}/plot_3_seminars_line.png')
    create_stacked_bar_chart(df_sem, 'Seminars', 
                             f'Execution Time Breakdown (Fixed Students |I|=60, {mode_title})', 
                             'Number of Seminars (|J|)', 
                             f'{output_dir}/plot_3_seminars_stacked.png')
    
    print(f"All plots generated in folder '{output_dir}/'")

if __name__ == "__main__":
    generate_plots(mode="equal")
    generate_plots(mode="unequal")
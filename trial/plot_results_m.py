import os
import pandas as pd
import matplotlib.pyplot as plt

def create_comparison_line_chart(df_regular, df_symmetry, x_column, title, xlabel, output_filename):
    """Generates a line chart comparing total time between regular and symmetry versions."""
    plt.figure(figsize=(10, 6))
    
    plt.plot(df_regular[x_column], df_regular['Total_Time(s)'], 
             marker='o', linestyle='-', color='#e74c3c', linewidth=2.5, markersize=8, label='Regular')
    plt.plot(df_symmetry[x_column], df_symmetry['Total_Time(s)'], 
             marker='s', linestyle='--', color='#2c3e50', linewidth=2.5, markersize=8, label='With Symmetry')
    
    plt.title(title, fontsize=14, pad=15)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel('Total Execution Time (seconds)', fontsize=12)
    plt.xticks(df_regular[x_column])
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=11)
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()

def create_comparison_stacked_bar_chart(df_regular, df_symmetry, x_column, title, xlabel, output_filename):
    """Generates two side‑by‑side stacked bar charts: regular vs symmetry."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    
    # Regular (left)
    bar_width = (df_regular[x_column].max() - df_regular[x_column].min()) / (len(df_regular) * 2)
    if bar_width == 0: bar_width = 1
    
    ax1.bar(df_regular[x_column], df_regular['Time_Step1(s)'], width=bar_width, label='Step 1 (Preferences)', color="#f4b0f6")
    ax1.bar(df_regular[x_column], df_regular['Time_Step2(s)'], width=bar_width, bottom=df_regular['Time_Step1(s)'], label='Step 2 (Diversity)', color='#3498db')
    bottom_step3 = df_regular['Time_Step1(s)'] + df_regular['Time_Step2(s)']
    ax1.bar(df_regular[x_column], df_regular['Time_Step3(s)'], width=bar_width, bottom=bottom_step3, label='Step 3 (Balance)', color="#721195")
    ax1.set_title(f'Regular\n{title}', fontsize=12)
    ax1.set_xlabel(xlabel, fontsize=11)
    ax1.set_ylabel('Execution Time (seconds)', fontsize=11)
    ax1.set_xticks(df_regular[x_column])
    ax1.legend(fontsize=9)
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Symmetry (right)
    ax2.bar(df_symmetry[x_column], df_symmetry['Time_Step1(s)'], width=bar_width, label='Step 1 (Preferences)', color="#f4b0f6")
    ax2.bar(df_symmetry[x_column], df_symmetry['Time_Step2(s)'], width=bar_width, bottom=df_symmetry['Time_Step1(s)'], label='Step 2 (Diversity)', color='#3498db')
    bottom_step3_sym = df_symmetry['Time_Step1(s)'] + df_symmetry['Time_Step2(s)']
    ax2.bar(df_symmetry[x_column], df_symmetry['Time_Step3(s)'], width=bar_width, bottom=bottom_step3_sym, label='Step 3 (Balance)', color="#721195")
    ax2.set_title(f'With Symmetry\n{title}', fontsize=12)
    ax2.set_xlabel(xlabel, fontsize=11)
    ax2.set_xticks(df_symmetry[x_column])
    ax2.legend(fontsize=9)
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()

def create_single_line_chart(df, x_column, title, xlabel, output_filename):
    """Original line chart for a single dataset (used for unequal‑sized)."""
    plt.figure(figsize=(10, 6))
    plt.plot(df[x_column], df['Total_Time(s)'], marker='o', linestyle='-', color='#2c3e50', linewidth=2.5, markersize=8)
    plt.title(title, fontsize=14, pad=15)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel('Total Execution Time (seconds)', fontsize=12)
    plt.xticks(df[x_column])
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()

def create_single_stacked_bar_chart(df, x_column, title, xlabel, output_filename):
    """Original stacked bar chart for a single dataset."""
    plt.figure(figsize=(10, 6))
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
    """Generates plots. For equal mode, compares regular vs symmetry."""
    input_dir = f"results_{mode}"
    output_dir = f"plots_{mode}"
    os.makedirs(output_dir, exist_ok=True)

    mode_title = "Equal-Sized" if mode == "equal" else "Unequal-Sized"

    # Define experiment file suffixes and corresponding x‑axis labels
    experiments = [
        ("scalability_proportional", "Students", "Number of Students (|I|) & Proportionally Increasing Seminars"),
        ("scalability_students", "Students", "Number of Students (|I|)"),
        ("scalability_seminars", "Seminars", "Number of Seminars (|J|)")
    ]

    for file_prefix, x_col, xlabel in experiments:
        if mode == "equal":
            # Read both regular and symmetry CSV files
            reg_file = os.path.join(input_dir, f"{file_prefix}_regular.csv")
            sym_file = os.path.join(input_dir, f"{file_prefix}_symmetry.csv")
            if not os.path.exists(reg_file) or not os.path.exists(sym_file):
                print(f"Missing files for {file_prefix}, skipping.")
                continue
            df_reg = pd.read_csv(reg_file)
            df_sym = pd.read_csv(sym_file)
            
            # Line chart comparison
            title_line = f'Scalability: Total Time Comparison ({mode_title})'
            create_comparison_line_chart(df_reg, df_sym, x_col, title_line, xlabel, 
                                         f'{output_dir}/{file_prefix}_line_comparison.png')
            # Stacked bar comparison (side‑by‑side)
            title_stack = f'Execution Time Breakdown Comparison ({mode_title})'
            create_comparison_stacked_bar_chart(df_reg, df_sym, x_col, title_stack, xlabel,
                                                f'{output_dir}/{file_prefix}_stacked_comparison.png')
        else:
            # Unequal mode: only regular file exists
            csv_file = os.path.join(input_dir, f"{file_prefix}.csv")
            if not os.path.exists(csv_file):
                print(f"Missing file {csv_file}, skipping.")
                continue
            df = pd.read_csv(csv_file)
            title_line = f'Scalability: Total Time vs. {x_col} ({mode_title})'
            create_single_line_chart(df, x_col, title_line, xlabel, 
                                     f'{output_dir}/plot_{file_prefix}_line.png')
            title_stack = f'Execution Time Breakdown ({mode_title})'
            create_single_stacked_bar_chart(df, x_col, title_stack, xlabel,
                                            f'{output_dir}/plot_{file_prefix}_stacked.png')
    
    print(f"All plots generated in folder '{output_dir}/'")

if __name__ == "__main__":
    print("Which mode do you want to plot?")
    print("1. Equal-Sized Seminars (comparison regular vs symmetry)")
    print("2. Unequal-Sized Seminars (only regular)")
    choice = input("Choose 1 or 2: ")
    if choice == '1':
        generate_plots(mode="equal")
    elif choice == '2':
        generate_plots(mode="unequal")
    else:
        print("Invalid option. Exiting...")
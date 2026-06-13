import os
import time
import random
import pandas as pd
from data import generate_sapp_data
from models import (
    step1_preference_maximal_assignment, 
    solve_step2_equal_sized, 
    solve_step3_equal_sized,
    solve_step2_unequal_sized,
    solve_step3_unequal_sized
)
from models_with_symmetry import (
    step1_preference_maximal_assignment_symmetry,
    solve_step2_equal_sized_symmetry,
    solve_step3_equal_sized_symmetry,
    # Note: symmetry functions for unequal are not defined (no benefit)
)

def run_experiment_equal(experiment_name, scenarios, csv_filepath, num_iterations=5, use_symmetry=False):
    """
    Runs an experiment for equal‑sized seminars.
    If use_symmetry=True, calls the symmetry versions of the models.
    """
    print("\n" + "="*60)
    version = "with symmetry" if use_symmetry else "without symmetry"
    print(f" STARTING EQUAL EXPERIMENT: {experiment_name} ({version}) ({num_iterations} iterations)")
    print("="*60)

    # Choose model functions based on symmetry flag
    if use_symmetry:
        step1_func = step1_preference_maximal_assignment_symmetry
        step2_func = solve_step2_equal_sized_symmetry
        step3_func = solve_step3_equal_sized_symmetry
    else:
        step1_func = step1_preference_maximal_assignment
        step2_func = solve_step2_equal_sized
        step3_func = solve_step3_equal_sized

    results = []

    for i, (num_students, num_seminars) in enumerate(scenarios, 1):
        print(f"\n[Scenario {i}/{len(scenarios)}] Executing: |I|={num_students}, |J|={num_seminars}...")
        
        sum_t1, sum_t2, sum_t3 = 0.0, 0.0, 0.0
        sum_gap3 = 0.0
        time_limit_count = 0
        optimal_count = 0

        for iteration in range(1, num_iterations + 1):
            seed = 42 + num_students + num_seminars + iteration
            random.seed(seed)

            I, J, p, r_min, r_max, a = generate_sapp_data(num_students, num_seminars, equal_sized=True)
            
            # Step 1
            start_t1 = time.time()
            F_optimal, _, gap1, stat1 = step1_func(I, J, p, r_min, r_max)
            sum_t1 += (time.time() - start_t1)
            
            # Step 2
            start_t2 = time.time()
            Z_optimal = None
            if F_optimal is not None:
                Z_optimal, _, gap2, stat2 = step2_func(I, J, p, F_optimal, a)
                sum_t2 += (time.time() - start_t2)

            # Step 3
            start_t3 = time.time()
            if Z_optimal is not None:
                balance_score, _, gap3, stat3 = step3_func(I, J, p, F_optimal, Z_optimal, a)
                sum_t3 += time.time() - start_t3
                
                if gap3 is not None:
                    sum_gap3 += gap3
                if stat3 == "OPTIMAL":
                    optimal_count += 1
                elif stat3 == "TIME_LIMIT":
                    time_limit_count += 1
            
            if iteration % 5 == 0:
                print(f"    ...Iteration {iteration}/{num_iterations} completed.")
        
        avg_t1 = sum_t1 / num_iterations
        avg_t2 = sum_t2 / num_iterations
        avg_t3 = sum_t3 / num_iterations
        avg_gap3 = sum_gap3 / num_iterations
            
        results.append({
            "Students": num_students,
            "Seminars": num_seminars,
            "Time_Step1(s)": round(avg_t1, 3),
            "Time_Step2(s)": round(avg_t2, 3),
            "Time_Step3(s)": round(avg_t3, 3),
            "Total_Time(s)": round(avg_t1 + avg_t2 + avg_t3, 3),
            "Avg_Gap_Step3(%)": round(avg_gap3 * 100, 4), 
            "Optimal_Runs": optimal_count,
            "TimeLimit_Runs": time_limit_count
        })

    df_results = pd.DataFrame(results)
    df_results.to_csv(csv_filepath, index=False)
    print(f"\n>>> {experiment_name} finished! Saved to {csv_filepath} <<<\n")


def run_experiment_unequal(experiment_name, scenarios, csv_filepath, num_iterations=5):
    """Runs experiments for unequal‑sized seminars (symmetry not applicable)."""
    print("\n" + "="*60)
    print(f" STARTING UNEQUAL EXPERIMENT: {experiment_name} ({num_iterations} iterations)")
    print("="*60)

    results = []

    for i, (num_students, num_seminars) in enumerate(scenarios, 1):
        print(f"\n[Scenario {i}/{len(scenarios)}] Executing: |I|={num_students}, |J|={num_seminars}...")
        
        sum_t1, sum_t2, sum_t3, sum_gap3 = 0.0, 0.0, 0.0, 0.0
        optimal_count, time_limit_count = 0, 0

        for iteration in range(1, num_iterations + 1):
            seed = 42 + num_students + num_seminars + iteration
            random.seed(seed)

            I, J, p, r_min, r_max, a = generate_sapp_data(num_students, num_seminars, equal_sized=False)
            
            start_t1 = time.time()
            F_optimal, _, gap1, stat1 = step1_preference_maximal_assignment(I, J, p, r_min, r_max)
            sum_t1 += (time.time() - start_t1)
            
            start_t2 = time.time()
            Z_optimal = None
            if F_optimal is not None:
                Z_optimal, _, gap2, stat2 = solve_step2_unequal_sized(I, J, p, r_min, r_max, F_optimal, a)
                sum_t2 += (time.time() - start_t2)

            start_t3 = time.time()
            if Z_optimal is not None:
                balance_score, _, gap3, stat3 = solve_step3_unequal_sized(I, J, p, r_min, r_max, F_optimal, Z_optimal, a)
                sum_t3 += time.time() - start_t3
                
                if gap3 is not None: 
                    sum_gap3 += gap3
                if stat3 == "OPTIMAL": 
                    optimal_count += 1
                elif stat3 == "TIME_LIMIT": 
                    time_limit_count += 1
            
            if iteration % 5 == 0:
                print(f"    ...Iteration {iteration}/{num_iterations} completed.")
        
        results.append({
            "Students": num_students, "Seminars": num_seminars,
            "Time_Step1(s)": round(sum_t1 / num_iterations, 3),
            "Time_Step2(s)": round(sum_t2 / num_iterations, 3),
            "Time_Step3(s)": round(sum_t3 / num_iterations, 3),
            "Total_Time(s)": round((sum_t1 + sum_t2 + sum_t3) / num_iterations, 3),
            "Avg_Gap_Step3(%)": round((sum_gap3 / num_iterations) * 100, 4), 
            "Optimal_Runs": optimal_count, "TimeLimit_Runs": time_limit_count
        })

    df_results = pd.DataFrame(results)
    df_results.to_csv(csv_filepath, index=False)
    print(f"\n>>> {experiment_name} finished! Saved to {csv_filepath} <<<\n")


def run_equal_comparison(scenarios, output_dir, experiment_suffix, num_iterations=5):
    """
    Runs both regular and symmetry versions for equal‑sized seminars.
    Saves two CSV files: {experiment_suffix}_regular.csv and {experiment_suffix}_symmetry.csv
    """
    regular_path = os.path.join(output_dir, f"{experiment_suffix}_regular.csv")
    symmetry_path = os.path.join(output_dir, f"{experiment_suffix}_symmetry.csv")
    
    print(f"\n--- Running regular version for {experiment_suffix} ---")
    run_experiment_equal(experiment_suffix, scenarios, regular_path, num_iterations, use_symmetry=False)
    
    print(f"\n--- Running symmetry version for {experiment_suffix} ---")
    run_experiment_equal(experiment_suffix, scenarios, symmetry_path, num_iterations, use_symmetry=True)


def run_all_scalability_tests(mode="equal"):
    print("="*60)
    print(f" SAPP SCALABILITY ANALYSIS - MODE: {mode.upper()}")
    print("="*60)
    output_dir = f"results_{mode}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Experiment scenarios
    scenarios_prop = [(20, 2), (30, 3), (40, 4), (50, 5)]
    scenarios_full = [(25, 5), (50, 5), (75, 5), (100, 5), (125, 5)]
    scenarios_frag = [(60, 2), (60, 3), (60, 4), (60, 5)]
    
    if mode == "equal":
        # For each experiment, run both regular and symmetry, saving separate files
        run_equal_comparison(scenarios_prop, output_dir, "scalability_proportional", num_iterations=5)
        run_equal_comparison(scenarios_full, output_dir, "scalability_students", num_iterations=5)
        run_equal_comparison(scenarios_frag, output_dir, "scalability_seminars", num_iterations=5)
    elif mode == "unequal":
        # Symmetry not applicable; only regular version
        run_experiment_unequal("Proportional Growth", scenarios_prop, f"{output_dir}/scalability_proportional.csv")
        run_experiment_unequal("Fuller Classrooms", scenarios_full, f"{output_dir}/scalability_students.csv")
        run_experiment_unequal("Fragmentation of Offer", scenarios_frag, f"{output_dir}/scalability_seminars.csv")


if __name__ == "__main__":
    print("Which scalability analysis do you want to run?")
    print("1. Equal-Sized Seminars (with regular vs symmetry comparison)")
    print("2. Unequal-Sized Seminars (only regular)")

    choice = input("Choose 1 or 2: ")

    if choice == '1':
        run_all_scalability_tests(mode="equal")
    elif choice == '2':
        run_all_scalability_tests(mode="unequal")
    else:
        print("Invalid option. Exiting...")
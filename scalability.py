import os
import time
import random
import pandas as pd
from data import generate_sapp_data
from models import (
    step1_preference_maximal_assignment, 
    solve_step2_equal_sized, 
    solve_step3_equal_sized
)

def run_experiment(experiment_name, scenarios, csv_filepath):
    """Runs a specific scalability experiment and saves it to a CSV."""
    print("\n" + "="*60)
    print(f" STARTING EXPERIMENT: {experiment_name} ")
    print("="*60)

    results = []
    random.seed(42)

    for i, (num_students, num_seminars) in enumerate(scenarios, 1):
        print(f"\n[Scenario {i}/{len(scenarios)}] Executing: |I|={num_students}, |J|={num_seminars}...")
        
        I, J, p, r_min, r_max, a = generate_sapp_data(num_students, num_seminars, equal_sized=True)
        
        # --- STEP 1 ---
        start_t1 = time.time()
        F_optimal, _ = step1_preference_maximal_assignment(I, J, p, r_min, r_max)
        t1_duration = time.time() - start_t1
        
        # --- STEP 2 ---
        start_t2 = time.time()
        Z_optimal = None
        t2_duration = 0.0
        if F_optimal is not None:
            Z_optimal, _ = solve_step2_equal_sized(I, J, p, F_optimal, a)
            t2_duration = time.time() - start_t2

        # --- STEP 3 ---
        start_t3 = time.time()
        balance_score = None
        t3_duration = 0.0
        if Z_optimal is not None:
            balance_score, _ = solve_step3_equal_sized(I, J, p, F_optimal, Z_optimal, a)
            t3_duration = time.time() - start_t3
            
        results.append({
            "Students": num_students,
            "Seminars": num_seminars,
            "Time_Step1(s)": round(t1_duration, 3),
            "Time_Step2(s)": round(t2_duration, 3),
            "Time_Step3(s)": round(t3_duration, 3),
            "Total_Time(s)": round(t1_duration + t2_duration + t3_duration, 3)
        })

    df_results = pd.DataFrame(results)
    df_results.to_csv(csv_filepath, index=False)
    print(f"\n>>> {experiment_name} finished! Saved to {csv_filepath} <<<\n")


def run_all_scalability_tests():
    print("="*60)
    print(" SAPP SCALABILITY ANALYSIS SUITE (EQUAL-SIZED) ")
    print("="*60)

    # 1. Crear carpeta para los resultados si no existe
    output_dir = "results_equal"
    os.makedirs(output_dir, exist_ok=True)

    # 2. Experimentos
    scenarios_prop = [(20, 2), (50, 5), (100, 10), (150, 15), (200, 20)]
    run_experiment("Proportional Growth", scenarios_prop, f"{output_dir}/scalability_proportional.csv")

    scenarios_full = [(50, 5), (100, 5), (150, 5), (200, 5), (250, 5)]
    run_experiment("Fuller Classrooms", scenarios_full, f"{output_dir}/scalability_students.csv")

    scenarios_frag = [(120, 2), (120, 3), (120, 4), (120, 6), (120, 8), (120, 10)]
    run_experiment("Fragmentation of Offer", scenarios_frag, f"{output_dir}/scalability_seminars.csv")

if __name__ == "__main__":
    run_all_scalability_tests()
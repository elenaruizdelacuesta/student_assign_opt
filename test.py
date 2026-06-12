import random
from data import generate_sapp_data
from models import step1_preference_maximal_assignment, solve_step2_equal_sized, solve_step3_equal_sized, solve_step2_unequal_sized, solve_step3_unequal_sized

def print_assignment(assignment_dict, a_dict):
    if not assignment_dict:
        print("No assignment found.")
        return
        
    # Group students by seminar for better visualization
    seminars = {}
    for student, seminar in assignment_dict.items():
        if seminar not in seminars:
            seminars[seminar] = []
        seminars[seminar].append((student, a_dict[student]))
        
    for sem, students in seminars.items():
        print(f"\n  Seminar {sem} (Total: {len(students)} students):")
        for st, grade in students:
            print(f"    - Student {st} (Grade: {grade})")

def run_equal_sized_test():
    """
    Executes the test for equal-sized seminars
    """
    # TEST 1: EQUAL-SIZED SEMINARS (18 students, 3 seminars)
    print("\nTEST 1: EQUAL-SIZED SEMINARS (18 students, 3 seminars)")
    num_students = 30
    num_seminars = 3
    
    # 1. Generate Data
    I, J, p, r_min, r_max, a = generate_sapp_data(num_students, num_seminars, equal_sized=True)
    
    print(f"\nGenerated Data: {num_students} students for {num_seminars} seminars.")
    print("Student Academic Scores (a_i):")
    print(a, "\n")

    # 2. Execute STEP 1
    print("\nSTEP 1: Maximize Preferences")
    F_optimal, assignment_1, gap1, status1 = step1_preference_maximal_assignment(I, J, p, r_min, r_max)
    #print(f"Maximum Satisfaction (F) = {F_optimal}")
    #print_assignment(assignment_1, a)
    
    # 3. Execute STEP 2
    if F_optimal is not None:
        print(f"\nStep 1 Completed: F = {F_optimal} | Status: {status1} | Gap: {gap1:.2%}")
        
        print("\nSTEP 2: Maximize Academic Diversity")
        Z_optimal, assignment_2, gap2, status2 = solve_step2_equal_sized(I, J, p, F_optimal, a)
        # print(f"Total Diversity (Z) = {Z_optimal}")
        # print_assignment(assignment_2, a)
        
        # 4. Execute STEP 3
        if Z_optimal is not None:
            print(f"\nStep 2 Completed: Z = {Z_optimal} | Status: {status2} | Gap: {gap2:.2%}")

            print("\nSTEP 3: Balancing Seminars")
            balance_score, assignment_3, gap3, status3 = solve_step3_equal_sized(I, J, p, F_optimal, Z_optimal, a)
            #print(f"Total Absolute Deviation (Balance Score) = {balance_score}")
            #print_assignment(assignment_3, a)
            if balance_score is not None:
                print(f"\nStep 3 Completed! Balance Score = {balance_score} | Status: {status3} | Gap: {gap3:.2%}")
                print("\nFINAL ASSIGNMENT SUMMARY:")
                print("="*50)

                for j in J:
                    assigned_students = [i for i, assigned_j in assignment_3.items() if assigned_j == j]
                    
                    print(f" SEMINAR {j} (Total: {len(assigned_students)} students)")
                    
                    for i in assigned_students:
                        print(f" Student {i:2d}  |  Score: {a[i]:.2f}")
                    
                    print("-" * 50)
            else:
                print("\nFailed at Step 3.")
        else:
            print("Step 3 skipped because Step 2 failed.")
    else:
        print("Step 2 and 3 skipped because Step 1 failed.")

def run_unequal_sized_test():
    """
    Executes the test for unequal-sized seminars
    """
    # TEST 2: UNEQUAL-SIZED SEMINARS (10 students, 2 seminars)
    print("\nTEST 2: UNEQUAL-SIZED SEMINARS (10 students, 2 seminars)")
    num_students = 13
    num_seminars = 2
    
    # 1. Generate Data
    I, J, p, r_min, r_max, a = generate_sapp_data(num_students, num_seminars, equal_sized=False)
    
    print(f"\nGenerated Data: {num_students} students for {num_seminars} seminars.")
    print("Student Academic Scores (a_i):")
    print(a, "\n")
    print(f"Capacities -> Min: {r_min}, Max: {r_max}\n")

    # 2. Execute STEP 1
    print("\nSTEP 1: Maximize Preferences")
    F_optimal, assignment_1, gap1, status1 = step1_preference_maximal_assignment(I, J, p, r_min, r_max)
    #print(f"Maximum Satisfaction (F) = {F_optimal}")
    #print_assignment(assignment_1, a)
    
    # 3. Execute STEP 2
    if F_optimal is not None:
        print(f"\nStep 1 Completed: F = {F_optimal} | Status: {status1} | Gap: {gap1:.2%}")
        
        print("\nSTEP 2: Maximize Academic Diversity")
        Z_optimal, assignment_2, gap2, status2 = solve_step2_unequal_sized(I, J, p, r_min, r_max, F_optimal, a)
        #print(f"Total Diversity (Z) = {Z_optimal}")
        #print_assignment(assignment_2, a)
        
        # 4. Execute STEP 3
        if Z_optimal is not None:
            print(f"\nStep 2 Completed: Z = {Z_optimal} | Status: {status2} | Gap: {gap2:.2%}")
            
            print("\nSTEP 3: Balancing Seminars")
            balance_score, assignment_3, gap3, status3  = solve_step3_unequal_sized(I, J, p, r_min, r_max, F_optimal, Z_optimal, a)
            if balance_score is not None:
                print(f"\nStep 3 Completed: Balance Score = {balance_score} | Status: {status3} | Gap: {gap3:.2%}")
                print("\nFINAL ASSIGNMENT SUMMARY")
                print("="*50)

                for j in J:
                    assigned_students = [i for i, assigned_j in assignment_3.items() if assigned_j == j]
                    
                    print(f" SEMINAR {j} (Total: {len(assigned_students)} students)")
                    
                    for i in assigned_students:
                        print(f" Student {i:2d}  |  Score: {a[i]:.2f}")
                    
                    print("-" * 50)
            else: 
                print("\nFailed at Step 3.")
        else:
            print("Step 3 skipped because Step 2 failed.")
    else:
        print("Step 2 and 3 skipped because Step 1 failed.")


if __name__ == "__main__":
    print("="*50)
    print(" SAPP MODEL TESTING (SMALL INSTANCES)")
    print("="*50)
    
    print("Which test do you want to run?")
    print("1. Equal-Sized Seminars")
    print("2. Unequal-Sized Seminars")

    choice = input("Choose 1 or 2: ")

    random.seed(42) 
    if choice == '1':
        # Run the equal-sized scenario
        run_equal_sized_test()
    elif choice == '2':
        # Run the unequal-sized scenario
        run_unequal_sized_test()
    else:
        print("Invalid option. Exiting...")
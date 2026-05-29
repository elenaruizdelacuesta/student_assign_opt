import random
import math

def generate_sapp_data(num_students, num_seminars, equal_sized):
    """
    Generates instances for the Student Assignment Problem with Preferences (SAPP)
    strictly following Section 5.1 of Schulz (2026).
    
    Parameters:
    num_students : int
        Total number of students (|I|)
    num_seminars : int
        Total number of seminars (|J|)
    equal_sized : bool
        If True, all seminars have equal capacities. If False, capacities vary by +/- 10%.
        
    Returns:
    I : list
        List of student indices.
    J : list
        List of seminar indices.
    p : dict
        Preferences dictionary p[i, j] where higher is better (up to |J|).
    r_min : dict
        Minimum capacity per seminar.
    r_max : dict
        Maximum capacity per seminar.
    a : dict
        Academic performance score a[i] for each student (1.0 to 5.0).
    """
    
    # Define Sets
    I = list(range(num_students))
    J = list(range(num_seminars))
    
    # Generate Academic Scores (1.0 to 5.0)
    # we use round to 2 sifnificant figures
    a = {i: round(random.uniform(1.0, 5.0), 2) for i in I}
    
    # Generate Preferences
    p = {}
    for i in I:
        # Create a random sequence of all seminars
        random_sequence = J.copy()
        random.shuffle(random_sequence)
        
        # Assign preference values based on position in the sequence
        # The first seminar gets |J|, the second |J|-1, down to 1
        for position, j in enumerate(random_sequence):
            preference_value = num_seminars - position
            p[i, j] = preference_value
            
    # Generate Capacities (Unequal seminar sizes allowing +/- 10% variation)
    average_size = num_students / num_seminars

    if equal_sized:
        # scenario 1: Equal-sized seminars
        # We assume num_students is divisible by num_seminars for equal sizes
        exact_cap = int(average_size)
        r_min = {j: exact_cap for j in J}
        r_max = {j: exact_cap for j in J}
    else:
        min_cap = math.ceil(0.9 * average_size)
        max_cap = math.ceil(1.1 * average_size)
        
        r_min = {j: min_cap for j in J}
        r_max = {j: max_cap for j in J}
    
    # We ensure the sum of max capacities is at least the number of students
    total_max_capacity = sum(r_max.values())
    if total_max_capacity < num_students:
        print("Warning: The generated maximum capacities cannot fit all students.")
        
    return I, J, p, r_min, r_max, a


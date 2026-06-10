import gurobipy as gp
from gurobipy import GRB
import math
from data import generate_sapp_data

# STEP 1: 4.1 Step 1 — Preference-maximal assignment (for equal and unequal seminar sizes)
def step1_preference_maximal_assignment(I, J, p, r_min, r_max):
    """
    Solves Step 1 of the hierarchical model: Preference-maximal assignment (SAPP).
    
    Parameters:
    I : list
        Set of student identifiers
    J : list
        Set of seminar identifiers 
    p : dict
        Preferences dictionary where keys are tuples (i, j) 
        and the value is p_ij (ranging from 1 to |J|)
    r_min : dict
        Dictionary with the minimum capacity for each seminar j 
    r_max : dict
        Dictionary with the maximum capacity for each seminar j 
        
    Returns:
    float
        The optimal objective function value (F), needed as a parameter for Step 2.
    dict
        Dictionary with the resulting assignment {student: seminar}.
    """
    
    # 1. Initialize the Gurobi model environment
    model = gp.Model("SAPP_Step1_Preferences")
    
    # Enable Gurobi log output to monitor the solver's progress
    model.Params.OutputFlag = 1 
    model.Params.TimeLimit = 300

    # 2. Decision Variables (Equation 7)
    # x[i, j] is binary: 1 if student i is assigned to seminar j; 0 otherwise.
    x = model.addVars(I, J, vtype=GRB.BINARY, name="x")

    # 3. Objective Function (Equation 1)
    # Maximize the penalized preferences using base-2 powers
    objective = gp.quicksum((2 ** p[i, j]) * x[i, j] for i in I for j in J)
    model.setObjective(objective, GRB.MAXIMIZE)

    # 4. System Constraints
    
    # Unique assignment per student (Equation 8)
    # Each student 'i' must be assigned to exactly one seminar 'j'
    model.addConstrs((gp.quicksum(x[i, j] for j in J) == 1 for i in I), name="SingleAssignment")
    if r_min==r_max:
        # Equal seminar sizes scenario
        # Each seminar 'j' must receive exactly r_min[j] students (Equation 4)
        model.addConstrs((gp.quicksum(x[i, j] for i in I) == r_min[j] for j in J), name="EqualSeminarSize")
    else:
        # Minimum capacity limit per seminar (Equation 5)
        # Seminar 'j' must receive at least r_min[j] students
        model.addConstrs((gp.quicksum(x[i, j] for i in I) >= r_min[j] for j in J), name="MinCapacity")

        # Maximum capacity limit per seminar (Equation 6)
        # Seminar 'j' cannot exceed r_max[j] assigned places
        model.addConstrs((gp.quicksum(x[i, j] for i in I) <= r_max[j] for j in J), name="MaxCapacity")

    # 5. Execute the Optimization
    model.optimize()

    # 6. Results Extraction 
    if model.Status == GRB.OPTIMAL:
        F = model.ObjVal
        print(f"\n[Step 1] Success: Optimal Solution Found.")
        print(f"[Step 1] Maximum Preference Objective Value (F) = {F}\n")
        
        # Map the resulting assignment by reading the values of the binary variables
        optimal_assignment = {i: j for i in I for j in J if x[i, j].X > 0.5}
        
        return F, optimal_assignment
    else:
        print("\n[Step 1] Error: The solver could not find a feasible or optimal solution.")
        return None, None

# Preprocessing for Step 2: Diversity weights
def calculate_diversity_weights(num_blocks):
    """
    Calculates the diversity weights (c_l) for each block according to the mathematical formulation in the paper.
    
    Parameters:
    num_blocks : int
                 The number of blocks into which students are divided.
    
    Returns:
    dict
        A dictionary mapping each block identifier to its diversity weight.
    """
    
    L = list(range(1, num_blocks + 1)) 
    c = {}
    
    # we declare the value for each block l based on its position relative to the center of the block distribution
    for l in L:
        if num_blocks % 2 == 0:
            # if the number of blocks is even, the calculation is symmetric
            c_bar = 2 * max((num_blocks / 2) - l, l - (num_blocks / 2) - 1) + 1
        else:
            # if it is odd, they use another logic 
            c_bar = 2 * abs(l - math.ceil(num_blocks / 2))
        
        # assign the value of c[l] based on whether l is in the first half or the second half of the block distribution
        if l <= math.ceil(num_blocks / 2):
            c[l] = c_bar
        else:
            c[l] = -c_bar
            
    return c


# Shared constraint helpers
def add_preference_and_assignment_constraints(model, x, I, J, p, F_step1):
    """
    Adds constraints shared across Steps 2 and 3 for both equal and unequal sized seminars.
    
    (9)  Maintain preference optimality from Step 1
    (12)/(18) Each student assigned to exactly one seminar
    """
    # (9) Maintain preferences F from Step 1
    model.addConstr(gp.quicksum((2 ** p[i, j]) * x[i, j] for i in I for j in J) == F_step1, name="MaintainPreferences")
    # (12)/(18) Single assignment
    model.addConstrs((gp.quicksum(x[i, j] for j in J) == 1 for i in I), name="SingleAssignment")

def add_equal_block_constraints(model, x, y, I, J, L):
    """
    Adds block assignment constraints shared across Steps 2 and 3 for equal-sized seminars.

    (13) Each block l in each seminar j receives exactly one student
    (14) A student can only be assigned to a block in seminar j if they are assigned to seminar j
    """
    # (13) Block completion
    model.addConstrs((gp.quicksum(y[l, i, j] for i in I) == 1 for j in J for l in L), name="BlockCompletion")
    # (14) Student in block
    model.addConstrs((gp.quicksum(y[l, i, j] for l in L) == x[i, j] for i in I for j in J), name="StudentInBlock")

def add_unequal_block_constraints(model, x, w, y_bar, I, J, sizes, r_lb):
    """
    Adds block assignment constraints shared across Steps 2 and 3 for unequal-sized seminars.

    (19) Each block l (up to r_lb[j]) is filled by at most one student across all valid seminar sizes l_bar >= l
    (20) Student i in seminar j iff they occupy exactly one block across all valid (l_bar, l) combinations
    (21) y_bar[i,j,l_bar,l] <= w[j, l_bar]
    (22) The chosen size l_bar must equal the actual number of students in j
    (23) Exactly one size is chosen per seminar
    """
    # (19) Each block l (up to r_lb[j]) is filled by at most one student across all valid seminar sizes l_bar >= l
    model.addConstrs((gp.quicksum(y_bar[i, j, l_bar, l] for i in I for l_bar in sizes[j] if l_bar >= l) <= 1
         for j in J
         for l in range(1, r_lb[j] + 1)),
        name="BlockCapacity")
    # (20) Student i in seminar j iff they occupy exactly one block across all valid (l_bar, l) combinations for that seminar
    model.addConstrs( (gp.quicksum( y_bar[i, j, l_bar, l] for l_bar in sizes[j] for l in range(1, l_bar + 1)) == x[i, j] for i in I for j in J),
        name="StudentBlockLink")
    # (21) y_bar[i,j,l_bar,l] <= w[j, l_bar]  Can only place student in block (l_bar, l) if seminar j has size l_bar
    model.addConstrs( (y_bar[i, j, l_bar, l] <= w[j, l_bar] for i in I for j in J for l_bar in sizes[j] for l in range(1, l_bar + 1)),
        name="BlockSizeLink")
    # (22) The chosen size l_bar must equal the actual number of students in j
    model.addConstrs( (gp.quicksum(l_bar * w[j, l_bar] for l_bar in sizes[j])== gp.quicksum(x[i, j] for i in I) for j in J),
        name="SeminarSizeConsistency")
    # (23) Exactly one size is chosen per seminar
    model.addConstrs( (gp.quicksum(w[j, l_bar] for l_bar in sizes[j]) == 1 for j in J),
        name="OneSizePerSeminar")


# Step 2: Maximally Diverse Grouping Problem (Equal-sized)
def solve_step2_equal_sized(I, J, p, F_step1, a):
    """
    Step 2: Preference-maximal and maximally diverse assignment (Equal-sized).

    Parameters:
    I : list
        Set of student identifiers
    J : list
        Set of seminar identifiers
    p : dict
        Preferences dictionary where keys are tuples (i, j)
    F_step1 : float
        The optimal objective value from Step 1
    a : dict
        Attributes dictionary for students
    num_seminars : int
        The number of seminars
    
    Returns:
    dict
        Dictionary with the resulting assignment {student: seminar} if an optimal solution is found; None otherwise.
    """
    model = gp.Model("SAPP_Step2_Diversity_Equal")
    model.Params.OutputFlag = 1
    model.Params.TimeLimit = 300
    
    num_students = len(I)
    num_blocks = num_students // len(J)
    L = list(range(1, num_blocks + 1)) # set of all blocks
    c = calculate_diversity_weights(num_blocks) # the diveristy weights for each block

    # 1. Variables (Equation 16 and endogenous block assignment)
    # x[i, j] = 1 if student i goes to seminar j
    x = model.addVars(I, J, vtype=GRB.BINARY, name="x")
    # y[l, i, j] = 1 if student i is assigned to block l inside seminar j
    y = model.addVars(L, I, J, vtype=GRB.BINARY, name="y")

    # 2. Objective Function (Equation 11)
    # Maximize diversity: Sum of (Block Weight * Student Grade * Assignment Decision)
    model.setObjective(
        gp.quicksum(c[l] * a[i] * y[l, i, j] for l in L for i in I for j in J),
        GRB.MAXIMIZE
    )

    # 3. Constraints
    add_preference_and_assignment_constraints(model, x, I, J, p, F_step1)
    add_equal_block_constraints(model, x, y, I, J, L)

    model.optimize()
    
    if model.Status == GRB.OPTIMAL:
        # Extract the maximum diversity value (Z^e_1)
        Z_e_1 = model.ObjVal
        # https://github.com/Gurobi/modeling-examples/blob/master/traveling_salesman/tsp.ipynb
        optimal_assignment = {i: j for i in I for j in J if x[i, j].X > 0.5}

        return Z_e_1, optimal_assignment
    
    return None, None

def solve_step2_unequal_sized(I, J, p, r_lb, r_up, F_step1, a):
    """
    Step 2: Preference-maximal and maximally diverse assignment (Unequal-sized).

    Parameters:
    I : list
        Set of student identifiers
    J : list
        Set of seminar identifiers
    p : dict
        Preferences dictionary where keys are tuples (i, j)
    r_lb : dict 
        Minimum seminar size r_lb[j]
    r_up : dict 
        Maximum seminar size r_up[j]
    F_step1 : float
        The optimal objective value from Step 1
    a : dict
        Attributes dictionary for students
    Returns:
    dict
        Dictionary with the resulting assignment {student: seminar} if an optimal solution is found; None otherwise.
    """
    model = gp.Model("SAPP_Step2_Diversity_Unequal")
    model.Params.OutputFlag = 1

    """All valid seminar sizes per seminar j
    sizes[j] = [r_lb[j], r_lb[j]+1, ..., r_up[j]] """
    sizes = {j: list(range(r_lb[j], r_up[j]+1)) for j in J}

    """ Block positions within a given size l_bar: l in {1, ..., l_bar}
    Diversity weights depend on block position within the seminar of size l_bar
    c_weights[l_bar][l] = weight for block l in a seminar of size l_bar """
    c_weights ={l_bar: calculate_diversity_weights(l_bar) for j in J for l_bar in sizes[j]} 

    # 1. Variables 

    # x[i, j] = 1 if student i is assigned to seminar j  (Eq. 25)
    x = model.addVars(I, J, vtype=GRB.BINARY, name="x")
    # w[j, l_bar] = 1 if seminar j has exactly l_bar students  (Eq. 24)
    w = model.addVars( [(j, l_bar) for j in J for l_bar in sizes[j]],
        vtype=GRB.BINARY, name="w"    )

    # y_bar[i, j, l_bar, l] = 1 if student i is in block l of seminar j
    #when seminar j has l_bar students  (Eq. 17)    
    y_bar = model.addVars([(i, j, l_bar, l) for i in I for j in J for l_bar in sizes[j] for l in range(1, l_bar + 1)],
        vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name="y_bar")   

    #2. Objective (Eq. 17)
    model.setObjective(
        gp.quicksum(c_weights[l_bar][l] * a[i] * y_bar[i, j, l_bar, l] for i in I for j in J for l_bar in sizes[j] for l in range(1, l_bar + 1)),
        GRB.MAXIMIZE)

    #3. Constraints
    add_preference_and_assignment_constraints(model, x, I, J, p, F_step1)
    add_unequal_block_constraints(model, x, w, y_bar, I, J, sizes, r_lb)

    model.optimize()

    if model.Status == GRB.OPTIMAL:
        Z_u_1 = model.ObjVal
        optimal_assignment = {i: j for i in I for j in J if x[i, j].X > 0.5}
        return Z_u_1, optimal_assignment

    return None, None

# Step 3: Balanced Assignment (Equal-sized)
def solve_step3_equal_sized(I, J, p, F_step1, Z_step2, a):
    """
    Step 3: Preference-maximal, maximally diverse, and balanced assignment (Equal-sized).

    Parameters:
    I : list
        Set of student identifiers
    J : list
        Set of seminar identifiers
    p : dict
        Preferences dictionary where keys are tuples (i, j)
    F_step1 : float
        The optimal preference value from Step 1
    Z_step2 : float
        The optimal diversity score from Step 2
    a : dict
        Attributes dictionary for students (academic grades)
        
    Returns:
    float
        The optimal balancing score (minimizing deviation between seminars).
    dict
        Dictionary with the final balanced assignment {student: seminar}.
    """
    model = gp.Model("SAPP_Step3_Balancing_Equal")
    model.Params.OutputFlag = 1
    model.Params.TimeLimit = 300
    
    num_students = len(I)
    num_blocks = num_students // len(J)
    L = list(range(1, num_blocks + 1))
    c = calculate_diversity_weights(num_blocks)

    # 1. Variables
    x = model.addVars(I, J, vtype=GRB.BINARY, name="x")
    y = model.addVars(L, I, J, vtype=GRB.BINARY, name="y")
    
    # We add a continuous variable for the absolute deviation between pairs of seminars.
    # We only create variables for j' > j to avoid duplicates (Equation 27)
    J_pairs = [(J[idx_j], J[idx_jprime]) for idx_j in range(len(J)) for idx_jprime in range(idx_j + 1, len(J))]
    abdev = model.addVars(J_pairs, vtype=GRB.CONTINUOUS, lb=0, name="abdev")

    # 2. Objective Function (Equation 27)
    # Minimize the sum of absolute deviations between all seminar pairs
    model.setObjective(gp.quicksum(abdev[j, jprime] for j, jprime in J_pairs), GRB.MINIMIZE)

    # 3. Old Constraints from Step 1 & 2
    add_preference_and_assignment_constraints(model, x, I, J, p, F_step1)
    add_equal_block_constraints(model, x, y, I, J, L)

    # 4. Constraints for Step 3
    # (26) Maintain maximum diversity (Z) found in Step 2
    model.addConstr(
        gp.quicksum(c[l] * a[i] * y[l, i, j] for l in L for i in I for j in J) == Z_step2, 
        name="MaintainDiversity"
    )

    # (28) and (29) Linearization of the absolute difference
    for j, jprime in J_pairs:
        # Calculate the diversity score for seminar j
        div_j = gp.quicksum(c[l] * a[i] * y[l, i, j] for l in L for i in I)
        # Calculate the diversity score for seminar j'
        div_jprime = gp.quicksum(c[l] * a[i] * y[l, i, jprime] for l in L for i in I)
        
        # Constraint 28
        model.addConstr(div_j - div_jprime <= abdev[j, jprime], name=f"DevPos_{j}_{jprime}")
        # Constraint 29
        model.addConstr(div_jprime - div_j <= abdev[j, jprime], name=f"DevNeg_{j}_{jprime}")

    model.optimize()
 
    if model.Status == GRB.OPTIMAL:
        balance_score = model.ObjVal
        optimal_assignment = {i: j for i in I for j in J if x[i, j].X > 0.5}
        return balance_score, optimal_assignment
    
    return None, None

def solve_step3_unequal_sized(I, J, p, r_lb, r_ub, F_step1, Z_step2, a):
    """
    Step 3: Preference-maximal, maximally diverse, and balanced assignment (Unequal-sized).
    Parameters:
    I : list
        Set of student identifiers
    J : list
        Set of seminar identifiers
    p : dict
        Preferences dictionary where keys are tuples (i, j)
    r_lb : dict 
        Minimum seminar size r_lb[j]
    r_up : dict 
        Maximum seminar size r_up[j]
    F_step1 : float
        The optimal objective value from Step 1
    Z_step2 : float
        The optimal diversity score from Step 2
    a : dict
        Attributes dictionary for students

    Returns:
    float
        The optimal balancing score (minimizing deviation between seminars).
    dict
        Dictionary with the final balanced assignment {student: seminar}.
    """
    model = gp.Model("SAPP_Step3_Balancing_Unequal")
    model.Params.OutputFlag = 1

    sizes = {j: list(range(r_lb[j], r_ub[j] + 1)) for j in J}
    c_weights = {
        l_bar: calculate_diversity_weights(l_bar)
        for j in J for l_bar in sizes[j]
    }

    # 1. Variables (same as Step 2 unequal)
    x = model.addVars(I, J, vtype=GRB.BINARY, name="x")
    w = model.addVars([(j, l_bar) for j in J for l_bar in sizes[j]],
        vtype=GRB.BINARY, name="w")
    y_bar = model.addVars(
        [(i, j, l_bar, l) for i in I for j in J for l_bar in sizes[j] for l in range(1, l_bar + 1)],
        vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name="y_bar")

    J_pairs = [(J[idx_j], J[idx_jprime]) for idx_j in range(len(J)) for idx_jprime in range(idx_j + 1, len(J))]
    abdev = model.addVars(J_pairs, vtype=GRB.CONTINUOUS, lb=0, name="abdev")

    # 2. Objective (Eq. 31)
    model.setObjective(gp.quicksum(abdev[j, jprime] for j, jprime in J_pairs),
        GRB.MINIMIZE)

    # 3. Constraints carried over from Step 2 (Eqs. 9, 18-25)
    add_preference_and_assignment_constraints(model, x, I, J, p, F_step1)
    add_unequal_block_constraints(model, x, w, y_bar, I, J, sizes, r_lb)

    # 4. Step 3 constraints

    # (30) Maintain maximum diversity Z from Step 2
    model.addConstr(gp.quicksum(c_weights[l_bar][l] * a[i] * y_bar[i, j, l_bar, l] for i in I for j in J for l_bar in sizes[j] for l in range(1, l_bar + 1)) == Z_step2,
        name="MaintainDiversity")

    # (32) and (33) Linearization of absolute deviation between seminar pairs
    for j, jprime in J_pairs:
        div_j = gp.quicksum(
            c_weights[l_bar][l] * a[i] * y_bar[i, j, l_bar, l]
            for i in I
            for l_bar in sizes[j]
            for l in range(1, l_bar + 1)
        )
        div_jprime = gp.quicksum(
            c_weights[l_bar][l] * a[i] * y_bar[i, jprime, l_bar, l]
            for i in I
            for l_bar in sizes[jprime]
            for l in range(1, l_bar + 1)
        )

        # (32)
        model.addConstr(div_j - div_jprime <= abdev[j, jprime], name=f"DevPos_{j}_{jprime}")
        # (33)
        model.addConstr(div_jprime - div_j <= abdev[j, jprime], name=f"DevNeg_{j}_{jprime}")

    model.optimize()

    if model.Status == GRB.OPTIMAL:
        balance_score = model.ObjVal
        optimal_assignment = {i: j for i in I for j in J if x[i, j].X > 0.5}
        return balance_score, optimal_assignment

    return None, None

if __name__ == "__main__":
    # Generate test data for SAPP
    num_students = 100
    num_seminars = 5
    equal_sized = False

    I, J, p, r_min, r_max, a = generate_sapp_data(num_students, num_seminars, equal_sized)

    # Step 1: Preference-maximal assignment
    F_step1, assignment_step1 = step1_preference_maximal_assignment(I, J, p, r_min, r_max)

    if F_step1 is not None:
        print(f"Step 1 Optimal Objective Value (F): {F_step1}")
        print(f"Step 1 Assignment: {assignment_step1}")

        # Step 2: Preference-maximal and maximally diverse assignment (Equal-sized)
        Z_e_1, assignment_step2 = solve_step2_unequal_sized(I, J, p,r_min, r_max, F_step1, a)

        if Z_e_1 is not None:
            print(f"Step 2 Optimal Diversity Value (Z^e_1): {Z_e_1}")
            print(f"Step 2 Assignment: {assignment_step2}")
            final, assignment_step3 = solve_step3_unequal_sized(I, J, p, r_min, r_max, F_step1, Z_e_1, a)
            if final is not None:
                print(f"Step 3 Optimal Balance Score: {final}")
                print(f"Step 3 Assignment: {assignment_step3}")
            else:
                print("No optimal solution found for Step 3.")
        else:
            print("No optimal solution found for Step 2.")
    else:
        print("No optimal solution found for Step 1.")
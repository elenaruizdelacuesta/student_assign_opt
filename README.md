# Student Assignment Problem with Preferences (SAPP) - Scalability Analysis

## Project Description
This repository contains the implementation and computational analysis of the "Student Assignment Problem with Preferences" (SAPP), based on the methodology proposed by Schulz (2026). 

The algorithm solves the assignment problem in three hierarchical steps:
1. **Step 1:** Maximizing student preferences.
2. **Step 2:** Maximizing diversity within groups (Maximally Diverse Grouping Problem).
3. **Step 3:** Balancing diversity across different groups.

Two variants of the model are analyzed and compared:
* **Equal-Sized Seminars:** Strictly rigid and equal capacity for all classrooms.
* **Unequal-Sized Seminars:** Flexible capacity with a tolerance margin of +/- 10% from the average.

## Requirements and Dependencies
To run this project, you need the following components installed:
* **Python 3.8+**
* **Gurobi Optimizer** (Requires a valid academic or commercial license).
* Python libraries: `gurobipy`, `pandas`, `numpy`, `matplotlib`.

## Code Structure
* `data.py`: Contains the instance generator (`generate_sapp_data`). Creates random academic records and strict preferences to ensure the reproducibility of experiments using seeds.
* `models.py`: Contains the mathematical logic and Gurobi solver constraints for the three steps of the algorithm, covering both the equal and unequal-sized versions.
* `test.py`: It executes samll instances of the SAPP problem for both equal and unequal-sized models. 
* `scalability.py`: Executes the scalability tests (Proportional Growth, Fuller Classrooms, and Fragmentation) and exports the execution times to CSV files.
* `plot_results.py`: Visualization module. Reads the generated CSV files and builds line and stacked bar charts.

## Execution Instructions
1. Run the preliminary tests:
To verify that the solver and models are working correctly on small instances:
```bash
python test.py
```
2. Run the scalability file from the terminal:
   ```bash
   python scalability.py
   ```
You will need to choose the execution mode (1 for Equal-Sized or 2 for Unequal-Sized). The results will be saved in the results_equal/ or results_unequal/ folders.
3. Once the data is generated, run the visualization script to obtain the plots:
```bash
   python plot_results.py
   ```
The images will be saved in the plots_equal/ or plots_unequal/ folders.

## Results and Conclusions
The experiments demonstrate the computational limit of the SAPP problem when real-world conditions (classroom flexibility) are applied. Both models were compared using the exact same seeds to guarantee a fair comparison. 

### The Cost of Flexibility
The main conclusion on the analysis is that the computational complexity of the problem does not lie only in balancing students' academic scores, but in combining this balancing objective with the flexibility of classroom sizes.
* In the **Equal-Sized** model, since the classroom size is fixed, the search space is reduced. The solver is able to assign and balance 125 students across 5 seminars in less than 4 seconds. 
* In the **Unequal-Sized** model, introducing a 10% tolerance margin changes the mathematical formulation. The exact number of participants per seminar becomes an active variable rather than a constant. For the same 125 students and 5 seminars, the execution time exceeds 330 seconds, forcing the solver to reach the time limit. As a result, it returns a solution with an optimality gap of over 16%, meaning the execution terminated before the solver could mathematically prove that the found assignment was the absolute best possible.

### Complexity of the Balancing Phase (Step 3)
The breakdown of execution times confirms that Steps 1 and 2 are solved efficiently in both scenarios. The performance drop occurs in **Step 3 (Balancing)** of the Unequal model. By allowing variable classroom sizes, the mathematical model is forced to expand its dimensions through the use of complex four-index variables. The solver must evaluate not only *which* students to swap to balance the academic scores, but also *how many* students should optimally be in each seminar, increasing the computational time. 

### Stabilization in the Fragmentation Experiments
In the fragmentation experiments (keeping 60 students fixed and increasing the seminar offering from 2 to 5), the execution time curve was observed to flatten rather than grow exponentially.

This stabilization occurs due to the ratio between students and seminars. As the number of seminars icreases for a fixed student population, the size of each class is reduced. While the solver has to perform more cross-seminar comparisons, the difficulty of arranging students within those much smaller groups is lower. This reduction in the internal combinations of each classroom offsets the penalty of having more seminars, stabilizing the overall execution time.
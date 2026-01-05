"""
Data Generator for Job Optimizer Demo
"""

import random
from datetime import time
from typing import List, Dict, Any
from models.job import Job
from models.machine import Machine, Constraint

def generate_random_jobs(num_jobs: int = 5, rush_probability: float = 0.3) -> List[Job]:
    """
    Generate random jobs with TIGHT deadlines to force optimization needs.
    """
    products = ['P_A', 'P_B', 'P_C']
    jobs = []
    
    for i in range(num_jobs):
        prod = random.choice(products)
        is_rush = random.random() < rush_probability  # Use the parameter

        
        # Deadlines are TIGHT (09:00 - 11:00) to ensure Baseline fails
        due_hour = random.randint(9, 11) 
        due_min = random.choice([0, 15, 30, 45])
        
        # Duration based on product type
        if prod == 'P_A':
            duration = 45
            machine_opts = ["M1", "M2"]
        elif prod == 'P_B':
            duration = 60
            machine_opts = ["M1", "M3"]
        else: # P_C
            duration = 30
            machine_opts = ["M2", "M3"]
            
        jobs.append(Job(
            job_id=f"J{i+1:03d}",
            product_type=prod,
            processing_time=duration,
            due_time=time(due_hour, due_min),
            priority="rush" if is_rush else "normal",
            machine_options=machine_opts
        ))
        
    return jobs

def get_demo_machines() -> List[Machine]:
    return [
        Machine(machine_id="M1", capabilities=["P_A", "P_B"]),
        Machine(machine_id="M2", capabilities=["P_A", "P_C"]),
        Machine(machine_id="M3", capabilities=["P_B", "P_C"]),
    ]

def get_demo_constraint() -> Constraint:
    return Constraint(
        shift_start=time(8, 0),
        shift_end=time(16, 0),
        max_overtime_minutes=30,
        setup_times={
            "P_A->P_B": 10, "P_B->P_A": 10,
            "P_A->P_C": 15, "P_C->P_A": 15,
            "P_B->P_C": 12, "P_C->P_B": 12
        }
    )

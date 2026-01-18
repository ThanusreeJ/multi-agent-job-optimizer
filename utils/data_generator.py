"""
Data Generator for Job Optimizer Demo
"""

import random
import io
import pandas as pd
from datetime import time, datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from models.job import Job
from models.machine import Machine, Constraint, DowntimeWindow

def generate_random_jobs(num_jobs: int = 5, rush_probability: float = 0.3, machines: Optional[List[Machine]] = None, constraint: Optional[Constraint] = None) -> List[Job]:
    """
    Generate random jobs with deadlines based on shift constraints.
    """
    if machines is None:
        machines = get_demo_machines()
    if constraint is None:
        constraint = get_demo_constraint()
        
    # Get all unique products from machine capabilities
    all_products = set()
    for m in machines:
        all_products.update(m.capabilities)
    products = sorted(list(all_products))
        
    jobs = []
    
    # Shift timing for deadline generation
    start_hour = constraint.shift_start.hour
    end_hour = constraint.shift_end.hour
    
    for i in range(num_jobs):
        prod = random.choice(products)
        is_rush = random.random() < rush_probability
        
        # Deadlines are within the first half of the shift to force optimization
        due_hour = random.randint(start_hour + 1, start_hour + (end_hour - start_hour) // 2 + 1) 
        due_min = random.choice([0, 15, 30, 45])
        
        # Find machines that can handle this product
        machine_opts = [m.machine_id for m in machines if m.can_produce(prod)]
            
        # Standardize duration or randomize it
        duration = random.choice([30, 45, 60, 90])
            
        jobs.append(Job(
            job_id=f"J{i+1:03d}",
            product_type=prod,
            processing_time=duration,
            due_time=time(due_hour, due_min),
            priority="rush" if is_rush else "normal",
            machine_options=machine_opts
        ))
        
    return jobs

def generate_random_downtime(machines: List[Machine], constraint: Constraint) -> None:
    """
    Scenario A: Randomly generate downtime for testing re-optimization.
    """
    if not machines:
        return
        
    # Randomly select a machine
    machine = random.choice(machines)
    
    # Generate random window within shift hours
    shift_start_min = constraint.shift_start.hour * 60 + constraint.shift_start.minute
    shift_end_min = constraint.shift_end.hour * 60 + constraint.shift_end.minute
    
    # Start between 10% and 70% into the shift
    start_min_abs = random.randint(
        shift_start_min + (shift_end_min - shift_start_min) // 10,
        shift_start_min + (shift_end_min - shift_start_min) * 7 // 10
    )
    
    # Duration 30-120 minutes (clamped to shift end)
    duration_min = random.choice([30, 45, 60, 90, 120])
    end_min_abs = min(start_min_abs + duration_min, shift_end_min)
    
    # Current date context
    now = datetime.now()
    start_dt = datetime.combine(now.date(), time(start_min_abs // 60, start_min_abs % 60))
    end_dt = datetime.combine(now.date(), time(end_min_abs // 60, end_min_abs % 60))
    
    machine.add_downtime(start_dt, end_dt, "Random POC downtime")

def parse_downtime_csv(csv_content: str, machines: List[Machine]) -> List[str]:
    """
    Scenario B: Parse CSV content and apply downtime as constraints.
    CSV Columns: machine_id, downtime_start, downtime_end, reason
    """
    try:
        df = pd.read_csv(io.StringIO(csv_content))
        errors = []
        
        for _, row in df.iterrows():
            m_id = str(row['machine_id']).strip()
            try:
                start_dt = pd.to_datetime(row['downtime_start'])
                end_dt = pd.to_datetime(row['downtime_end'])
            except:
                errors.append(f"Invalid date format for {m_id}")
                continue
                
            reason = row.get('reason', 'Planned maintenance')
            
            target_machine = next((m for m in machines if m.machine_id == m_id), None)
            if target_machine:
                target_machine.add_downtime(start_dt, end_dt, reason)
            else:
                errors.append(f"Machine {m_id} not found")
                
        return errors
    except Exception as e:
        return [f"CSV parsing error: {str(e)}"]

def parse_jobs_csv(csv_content: str) -> Tuple[List[Job], List[str]]:
    """
    Scenario B: Parse CSV content and create Job objects.
    CSV Columns: job_id, product_type, processing_time, due_time, priority, machine_options
    machine_options should be semicolon separated (e.g., "M1;M2")
    """
    try:
        df = pd.read_csv(io.StringIO(csv_content))
        jobs = []
        errors = []
        
        for _, row in df.iterrows():
            job_id = str(row['job_id']).strip()
            prod = str(row['product_type']).strip()
            proc_time = int(row['processing_time'])
            
            # Parse due time
            try:
                dt_obj = pd.to_datetime(row['due_time'])
                due_time = dt_obj.time()
            except:
                errors.append(f"Invalid due_time for {job_id}")
                continue
                
            prio = str(row['priority']).strip().lower()
            
            # Parse machine options
            m_opts_str = str(row['machine_options']).strip()
            m_opts = [opt.strip() for opt in m_opts_str.split(';')] if ';' in m_opts_str else [m_opts_str]
            
            jobs.append(Job(
                job_id=job_id,
                product_type=prod,
                processing_time=proc_time,
                due_time=due_time,
                priority=prio,
                machine_options=m_opts
            ))
            
        return jobs, errors
    except Exception as e:
        return [], [f"Job CSV parsing error: {str(e)}"]

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

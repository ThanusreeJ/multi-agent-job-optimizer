
import sys
import os
from datetime import time, datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.job import Job
from models.machine import Machine, Constraint, DowntimeWindow
from models.schedule import Schedule, JobAssignment
from agents.constraint_agent import ConstraintAgent

def test_downtime_overlap():
    print("Testing Downtime Overlap Logic...")
    now = datetime.now()
    # Downtime 10:00 - 12:00
    dt_window = DowntimeWindow(
        datetime.combine(now.date(), time(10, 0)),
        datetime.combine(now.date(), time(12, 0)),
        "Maintenance"
    )
    
    # Job 09:00 - 11:00 (Overlaps at start of DT)
    assert dt_window.overlaps_with(time(9, 0), time(11, 0), now) == True
    
    # Job 11:00 - 11:30 (Fully inside)
    assert dt_window.overlaps_with(time(11, 0), time(11, 30), now) == True
    
    # Job 11:30 - 13:00 (Overlaps at end of DT)
    assert dt_window.overlaps_with(time(11, 30), time(13, 0), now) == True
    
    # Job 08:00 - 10:00 (No overlap, ends exactly at DT start)
    assert dt_window.overlaps_with(time(8, 0), time(10, 0), now) == False
    
    # Job 12:00 - 14:00 (No overlap, starts exactly at DT end)
    assert dt_window.overlaps_with(time(12, 0), time(14, 0), now) == False
    
    print("✓ Downtime Overlap Logic Passed")

def test_constraint_agent_downtime():
    print("\nTesting Constraint Agent with Downtime...")
    now = datetime.now()
    
    m1 = Machine("M1", ["P_A"])
    m1.add_downtime(
        datetime.combine(now.date(), time(10, 0)),
        datetime.combine(now.date(), time(12, 0)),
        "Maintenance"
    )
    
    jobs = [Job("J001", "P_A", 60, time(16, 0), "normal", ["M1"])]
    
    # Invalid Schedule: Job at 10:30 - 11:30
    sched_invalid = Schedule()
    sched_invalid.add_assignment(JobAssignment(jobs[0], "M1", time(10, 30), time(11, 30), 0))
    
    agent = ConstraintAgent()
    valid, violations, report = agent.validate_schedule(sched_invalid, jobs, [m1], Constraint())
    
    assert valid == False
    assert any("overlaps with downtime" in v for v in violations)
    print("✓ Constraint Agent properly detected downtime violation")
    
    # Valid Schedule: Job at 08:00 - 09:00
    sched_valid = Schedule()
    sched_valid.add_assignment(JobAssignment(jobs[0], "M1", time(8, 0), time(9, 0), 0))
    valid, violations, report = agent.validate_schedule(sched_valid, jobs, [m1], Constraint())
    
    assert valid == True
    assert len(violations) == 0
    print("✓ Constraint Agent approved valid schedule around downtime")

if __name__ == "__main__":
    try:
        test_downtime_overlap()
        test_constraint_agent_downtime()
        print("\nALL DOWNTIME LOGIC TESTS PASSED!")
    except Exception as e:
        print(f"\nTEST FAILED: {str(e)}")
        sys.exit(1)

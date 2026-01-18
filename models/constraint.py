"""
Constraint model for scheduling constraints.
Day 1: Core data model created
"""

from dataclasses import dataclass, field
from datetime import time
from typing import Dict, Optional, Any


@dataclass
class Constraint:
    """
    Represents scheduling constraints for the production system.
    
    This includes shift times, setup time matrices, priority weights, etc.
    """
    
    # Shift boundaries
    shift_start: time = time(8, 0)       # Shift starts at 08:00
    shift_end: time = time(16, 0)        # Shift ends at 16:00
    max_overtime_minutes: int = 0        # No overtime allowed by default
    
    # Setup times between product types (in minutes)
    # Example: {"P_A->P_A": 5, "P_A->P_B": 30, "P_B->P_B": 5, "P_B->P_A": 30}
    setup_times: Dict[str, int] = field(default_factory=dict)
    
    # Priority weights for rush vs normal jobs
    rush_job_weight: float = 10.0        # Rush jobs are 10x more important
    normal_job_weight: float = 1.0
    
    # Objective function weights
    tardiness_weight: float = 1.0        # How much we care about meeting deadlines
    setup_weight: float = 0.5            # How much we care about minimizing setups
    utilization_weight: float = 0.3      # How much we care about balancing load
    
    # WIP (Work in Progress) limits
    max_wip_per_machine: Optional[int] = None
    
    def get_setup_time(self, from_product: str, to_product: str) -> int:
        """
        Get setup time required when switching from one product to another.
        
        Args:
            from_product: Current product type
            to_product: Next product type
            
        Returns:
            Setup time in minutes
        """
        # If same product, use same-product setup time (usually shorter)
        if from_product == to_product:
            key = f"{from_product}->{to_product}"
            return self.setup_times.get(key, 5)  # Default 5 minutes
        
        # Different products require longer setup
        key = f"{from_product}->{to_product}"
        return self.setup_times.get(key, 30)  # Default 30 minutes
    
    def get_shift_duration_minutes(self) -> int:
        """
        Calculate total shift duration in minutes.
        
        Returns:
            Shift duration in minutes
        """
        start_minutes = self.shift_start.hour * 60 + self.shift_start.minute
        end_minutes = self.shift_end.hour * 60 + self.shift_end.minute
        return end_minutes - start_minutes
    
    def is_within_shift(self, time_point: time) -> bool:
        """
        Check if a time point falls within the shift.
        
        Args:
            time_point: Time to check
            
        Returns:
            True if within shift, False otherwise
        """
        point_minutes = time_point.hour * 60 + time_point.minute
        start_minutes = self.shift_start.hour * 60 + self.shift_start.minute
        end_minutes = self.shift_end.hour * 60 + self.shift_end.minute + self.max_overtime_minutes
        
        return start_minutes <= point_minutes <= end_minutes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert constraints to dictionary."""
        return {
            "shift_start": self.shift_start.strftime("%H:%M"),
            "shift_end": self.shift_end.strftime("%H:%M"),
            "max_overtime_minutes": self.max_overtime_minutes,
            "setup_times": self.setup_times,
            "rush_job_weight": self.rush_job_weight,
            "normal_job_weight": self.normal_job_weight,
            "tardiness_weight": self.tardiness_weight,
            "setup_weight": self.setup_weight,
            "utilization_weight": self.utilization_weight,
            "max_wip_per_machine": self.max_wip_per_machine
        }
    
    def __str__(self) -> str:
        return (f"Constraint(Shift: {self.shift_start}-{self.shift_end}, "
                f"{len(self.setup_times)} setup rules)")

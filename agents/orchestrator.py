"""
LangGraph Orchestration - Multi-Agent Workflow

This module implements the LangGraph workflow that orchestrates all agents
in a deterministic, traceable pipeline.

Workflow Steps:
    1. Supervisor analyzes the request
    2. Batching Agent creates setup-optimized schedule
    3. Bottleneck Agent creates load-balanced schedule
    4. Constraint Agent validates both candidates
    5. Supervisor selects best valid schedule
    6. If violations found, retry with adjustments

Uses LangGraph for state management and LangSmith for full traceability.
"""

import os
import time as time_module
from typing import Dict, List, Any, TypedDict, Annotated
from datetime import time

from langgraph.graph import StateGraph, END
from langsmith import traceable

from models.job import Job
from models.machine import Machine, Constraint
from models.schedule import Schedule

from agents.supervisor import SupervisorAgent
from agents.batching_agent import BatchingAgent
from agents.bottleneck_agent import BottleneckAgent
from agents.constraint_agent import ConstraintAgent
from utils.baseline_scheduler import BaselineScheduler


class OptimizationState(TypedDict):
    """
    State object passed between agents in the workflow.
    
    LangGraph uses this to track progress through the optimization pipeline.
    """
    # Inputs
    jobs: List[Job]
    machines: List[Machine]
    constraint: Constraint
    
    # Intermediate results
    supervisor_analysis: str
    baseline_schedule: Schedule
    baseline_explanation: str
    batching_schedule: Schedule
    batching_explanation: str
    bottleneck_schedule: Schedule
    bottleneck_explanation: str
    
    # Validation results
    baseline_valid: bool
    baseline_violations: List[str]
    batching_valid: bool
    batching_violations: List[str]
    bottleneck_valid: bool
    bottleneck_violations: List[str]
    
    # Final output
    final_schedule: Schedule
    final_explanation: str
    
    # Metadata
    retry_count: int
    optimization_time_seconds: float
    status: str  # "running", "completed", "failed"


class OptimizationOrchestrator:
    """
    LangGraph-based orchestrator for the multi-agent optimization workflow.
    
    This class coordinates all agents in a deterministic pipeline with
    automatic retry logic and full LangSmith tracing.
    """
    
    def __init__(self, groq_api_key: str = None):
        """
        Initialize the orchestrator with all agents.
        
        Args:
            groq_api_key: Groq API key for LLM agents
        """
        # Initialize all agents
        self.supervisor = SupervisorAgent(groq_api_key)
        self.baseline_scheduler = BaselineScheduler()
        self.batching_agent = BatchingAgent(groq_api_key)
        self.bottleneck_agent = BottleneckAgent(groq_api_key)
        self.constraint_agent = ConstraintAgent()
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph state graph defining the agent workflow.
        
        Returns:
            Compiled StateGraph
        """
        # Create graph
        graph = StateGraph(OptimizationState)
        
        # Add nodes for each step
        graph.add_node("analyze_request", self._analyze_request)
        graph.add_node("create_baseline_schedule", self._create_baseline_schedule)
        graph.add_node("create_batching_schedule", self._create_batching_schedule)
        graph.add_node("create_bottleneck_schedule", self._create_bottleneck_schedule)
        graph.add_node("validate_schedules", self._validate_schedules)
        graph.add_node("select_best", self._select_best)
        
        # Define edges (workflow flow)
        graph.set_entry_point("analyze_request")
        graph.add_edge("analyze_request", "create_baseline_schedule")
        graph.add_edge("create_baseline_schedule", "create_batching_schedule")
        graph.add_edge("create_batching_schedule", "create_bottleneck_schedule")
        graph.add_edge("create_bottleneck_schedule", "validate_schedules")
        graph.add_edge("validate_schedules", "select_best")
        graph.add_edge("select_best", END)
        
        return graph.compile()
    
    @traceable(name="Supervisor Analysis")
    def _analyze_request(self, state: OptimizationState) -> OptimizationState:
        """
        Step 1: Supervisor analyzes the optimization request.
        """
        print("📊 Supervisor analyzing request...")
        
        analysis = self.supervisor.analyze_optimization_request(
            state["jobs"],
            state["machines"],
            state["constraint"]
        )
        
        state["supervisor_analysis"] = analysis
        state["status"] = "analyzing"
        
        return state

    @traceable(name="Baseline Schedule")
    def _create_baseline_schedule(self, state: OptimizationState) -> OptimizationState:
        """
        Step 1b: Create a baseline FIFO schedule.
        """
        print("📊 Creating baseline schedule...")
        sched, exp = self.baseline_scheduler.schedule(
            state["jobs"],
            state["machines"],
            state["constraint"]
        )
        state["baseline_schedule"] = sched
        state["baseline_explanation"] = exp
        return state
    
    @traceable(name="Batching Agent Schedule")
    def _create_batching_schedule(self, state: OptimizationState) -> OptimizationState:
        """
        Step 2: Batching agent creates setup-optimized schedule.
        """
        print("🔄 Batching agent creating schedule...")
        
        schedule, explanation = self.batching_agent.create_batched_schedule(
            state["jobs"],
            state["machines"],
            state["constraint"]
        )
        
        # Calculate KPIs
        schedule.calculate_kpis(state["machines"], state["constraint"])
        
        state["batching_schedule"] = schedule
        state["batching_explanation"] = explanation
        
        return state
    
    @traceable(name="Bottleneck Agent Schedule")
    def _create_bottleneck_schedule(self, state: OptimizationState) -> OptimizationState:
        """
        Step 3: Bottleneck agent creates load-balanced schedule.
        """
        print("⚖️  Bottleneck agent creating schedule...")
        
        schedule, explanation = self.bottleneck_agent.rebalance_schedule(
            state["batching_schedule"],  # Start from batching schedule
            state["machines"],
            state["constraint"],
            state["jobs"]
        )
        
        # Calculate KPIs
        schedule.calculate_kpis(state["machines"], state["constraint"])
        
        state["bottleneck_schedule"] = schedule
        state["bottleneck_explanation"] = explanation
        
        return state
    
    @traceable(name="Constraint Validation")
    def _validate_schedules(self, state: OptimizationState) -> OptimizationState:
        """
        Step 4: Validate all candidate schedules.
        """
        print("✅ Constraint agent validating schedules...")
        
        # Validate baseline
        base_valid, base_violations, _ = self.constraint_agent.validate_schedule(
            state["baseline_schedule"],
            state["jobs"],
            state["machines"],
            state["constraint"]
        )
        state["baseline_valid"] = base_valid
        state["baseline_violations"] = base_violations

        # Validate batching schedule
        batching_valid, batching_violations, _ = self.constraint_agent.validate_schedule(
            state["batching_schedule"],
            state["jobs"],
            state["machines"],
            state["constraint"]
        )
        
        state["batching_valid"] = batching_valid
        state["batching_violations"] = batching_violations
        
        # Validate bottleneck schedule
        bottleneck_valid, bottleneck_violations, _ = self.constraint_agent.validate_schedule(
            state["bottleneck_schedule"],
            state["jobs"],
            state["machines"],
            state["constraint"]
        )
        
        state["bottleneck_valid"] = bottleneck_valid
        state["bottleneck_violations"] = bottleneck_violations
        
        return state
    
    @traceable(name="Supervisor Selection")
    def _select_best(self, state: OptimizationState) -> OptimizationState:
        """
        Step 5: Supervisor selects the best valid schedule.
        """
        print("🎯 Supervisor selecting best schedule...")
        
        # Collect valid candidates first
        valid_candidates = []
        
        if state["batching_valid"]:
            valid_candidates.append((state["batching_schedule"], "Batching-Optimized (Setup Minimization)", 0))
        
        if state["bottleneck_valid"]:
            valid_candidates.append((state["bottleneck_schedule"], "Load-Balanced (Bottleneck Relief)", 0))

        if state["baseline_valid"]:
            valid_candidates.append((state["baseline_schedule"], "Baseline FIFO (Fallback)", 0))
        
        if valid_candidates:
            # We have valid schedules - select best
            candidates = [(sched, name) for sched, name, _ in valid_candidates]
        else:
            # No fully valid schedules - use best-effort approach
            # Select the schedule with fewest violations
            print("⚠️  No fully valid schedules found - using best-effort approach")
            
            best_effort = [
                (state["batching_schedule"], "Batching-Optimized (Best Effort)", len(state["batching_violations"])),
                (state["bottleneck_schedule"], "Load-Balanced (Best Effort)", len(state["bottleneck_violations"])),
                (state["baseline_schedule"], "Baseline FIFO (Best Effort)", len(state["baseline_violations"]))
            ]
            
            # Sort by fewest violations
            best_effort.sort(key=lambda x: x[2])
            
            # Take the one with fewest violations
            best_schedule, best_name, violation_count = best_effort[0]
            
            # Format violations for display
            if best_name.startswith("Batching"):
                violations = state["batching_violations"]
            elif best_name.startswith("Load"):
                violations = state["bottleneck_violations"]
            else:
                violations = state["baseline_violations"]
            
            state["final_schedule"] = best_schedule
            state["final_explanation"] = f"""
⚠️ BEST-EFFORT SCHEDULE ({best_name})

No schedule could meet all constraints. Selected schedule with fewest violations ({violation_count}).

VIOLATIONS:
{chr(10).join('- ' + v for v in violations)}

RECOMMENDATION:
- Some constraints may be impossible to meet simultaneously
- Consider extending shift duration, reducing job count, or relaxing rush deadlines
- Review machine downtime schedules for conflicts
"""
            state["status"] = "best-effort"
            return state
        
        # Select best
        best_schedule, explanation = self.supervisor.select_best_schedule(
            candidates,
            state["constraint"]
        )
        
        state["final_schedule"] = best_schedule
        state["final_explanation"] = explanation
        state["status"] = "completed"
        
        return state
    
    @traceable(name="Full Optimization")
    def optimize(
        self,
        jobs: List[Job],
        machines: List[Machine],
        constraint: Constraint
    ) -> Dict[str, Any]:
        """
        Run the full multi-agent optimization workflow.
        
        This is the main entry point for optimization.
        
        Args:
            jobs: List of jobs to schedule
            machines: List of available machines
            constraint: Scheduling constraints and policies
            
        Returns:
            Dictionary with final schedule and metadata
        """
        start_time = time_module.time()
        
        # Initialize state
        initial_state = OptimizationState(
            jobs=jobs,
            machines=machines,
            constraint=constraint,
            supervisor_analysis="",
            baseline_schedule=None,
            baseline_explanation="",
            batching_schedule=None,
            batching_explanation="",
            bottleneck_schedule=None,
            bottleneck_explanation="",
            baseline_valid=False,
            baseline_violations=[],
            batching_valid=False,
            batching_violations=[],
            bottleneck_valid=False,
            bottleneck_violations=[],
            final_schedule=None,
            final_explanation="",
            retry_count=0,
            optimization_time_seconds=0.0,
            status="running"
        )
        
        print("\n" + "="*70)
        print("🚀 STARTING MULTI-AGENT OPTIMIZATION")
        print("="*70)
        
        # Run workflow
        final_state = self.workflow.invoke(initial_state)
        
        # Calculate timing
        end_time = time_module.time()
        final_state["optimization_time_seconds"] = end_time - start_time
        
        print("\n" + "="*70)
        print(f"✅ OPTIMIZATION COMPLETE ({final_state['optimization_time_seconds']:.2f}s)")
        print("="*70 + "\n")
        
        # Return results
        # Success if completed (fully valid) or best-effort (has a schedule with violations)
        return {
            "success": final_state["status"] in ["completed", "best-effort"],
            "schedule": final_state["final_schedule"],
            "explanation": final_state["final_explanation"],
            "optimization_time": final_state["optimization_time_seconds"],
            "supervisor_analysis": final_state["supervisor_analysis"],
            "batching_schedule": final_state["batching_schedule"],
            "bottleneck_schedule": final_state["bottleneck_schedule"],
            "status": final_state["status"]
        }


# Example usage and testing
if __name__ == "__main__":
    from dotenv import load_dotenv
    from utils.data_generator import generate_random_jobs
    from utils.config_loader import load_config
    
    load_dotenv()
    
    # Load configuration
    config = load_config()
    
    # Generate test jobs
    test_jobs = generate_random_jobs(15, rush_probability=0.2)
    
    print(f"Generated {len(test_jobs)} jobs for testing")
    print(f"Machines: {[m.machine_id for m in config['machines']]}")
    
    # Create orchestrator
    orchestrator = OptimizationOrchestrator()
    
    # Run optimization
    result = orchestrator.optimize(
        jobs=test_jobs,
        machines=config['machines'],
        constraint=config['constraint']
    )
    
    # Print results
    if result["success"]:
        print(result["explanation"])
        
        schedule = result["schedule"]
        print("\nMACHINE SCHEDULE:")
        for machine_id in schedule.assignments.keys():
            jobs = schedule.get_machine_jobs(machine_id)
            print(f"\n{machine_id}: {len(jobs)} jobs")
            for job in jobs:
                print(f"  {job.start_time} - {job.end_time}: {job.job.job_id} ({job.job.product_type})")
    else:
        print("Optimization failed!")
        print(result["explanation"])

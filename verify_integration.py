from models.job import Job
from models.machine import Machine, Constraint
from agents.supervisor import SupervisorAgent
from agents.constraint_agent import ConstraintAgent
from agents.orchestrator import OptimizationOrchestrator
from utils.data_generator import generate_random_jobs, get_demo_machines, get_demo_constraint
import os
from dotenv import load_dotenv

load_dotenv()

def test_imports():
    print("Testing imports...")
    try:
        jobs = generate_random_jobs(3)
        machines = get_demo_machines()
        constraint = get_demo_constraint()
        print("✓ Models and Utils loaded")
        
        c_agent = ConstraintAgent()
        print("✓ ConstraintAgent loaded")
        
        # We won't run Supervisor or Orchestrator unless API key is present
        if os.getenv("GROQ_API_KEY"):
            print("✓ GROQ_API_KEY found")
            orchestrator = OptimizationOrchestrator()
            print("✓ Orchestrator loaded")
        else:
            print("! GROQ_API_KEY not found - skipping LLM tests")
            
        print("\nVerification Successful!")
    except Exception as e:
        print(f"\nVerification Failed: {e}")

if __name__ == "__main__":
    test_imports()

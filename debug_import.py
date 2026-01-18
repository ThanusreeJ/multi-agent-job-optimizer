
import sys
import os

# Add job-optimizer to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print(f"Python path: {sys.path[0]}")

try:
    from utils.data_generator import parse_jobs_csv
    print("SUCCESS: Successfully imported parse_jobs_csv from utils.data_generator")
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
    import utils.data_generator
    print(f"Module file: {utils.data_generator.__file__}")
    print(f"Available attributes: {[attr for attr in dir(utils.data_generator) if not attr.startswith('__')]}")
except Exception as e:
    print(f"OTHER ERROR: {type(e).__name__}: {e}")

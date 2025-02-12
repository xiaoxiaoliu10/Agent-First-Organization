import os
import sys
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(root_dir)
from dotenv import load_dotenv

from benchmark.tau_bench.auto_error_identification import get_args, run_error_identification
load_dotenv()

if __name__ == "__main__":
    '''
    Provide --results-path and --output-dir
    '''
    sys.argv += ['--env', 'retail']
    sys.argv += ['--platform', 'openai']
    sys.argv += ['--max-concurrency', '16']
    args = get_args()
    run_error_identification(args)
    
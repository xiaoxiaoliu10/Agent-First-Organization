import os
import argparse
import sys
import subprocess
import atexit
from dotenv import load_dotenv

from tau_bench.auto_error_identification import get_args, run_error_identification
load_dotenv()

if __name__ == "__main__":
    sys.argv += ['--env', 'retail']
    sys.argv += ['--platform', 'openai']
    sys.argv += ['--max-concurrency', '16']
    args = get_args()
    run_error_identification(args)
    
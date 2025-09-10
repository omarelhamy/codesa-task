#!/usr/bin/env python3

import subprocess
import sys

def run_tests():
    """Run all tests in the project"""
    # Test backend
    backend_result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "backend/test_api.py", "-v"
    ], capture_output=True, text=True)
    
    if backend_result.returncode != 0:
        print(backend_result.stdout)
        print(backend_result.stderr)
    
    # Test worker
    worker_result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "worker/test_worker.py", "-v"
    ], capture_output=True, text=True)
    
    if worker_result.returncode != 0:
        print(worker_result.stdout)
        print(worker_result.stderr)
    
    if backend_result.returncode == 0 and worker_result.returncode == 0:
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())

#!/usr/bin/env python3

import subprocess
import sys
import os

def run_tests():
    """Run all tests in the project"""
    print("Running tests...")
    
    # Test backend
    print("Testing backend...")
    backend_result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "backend/test_api.py", "-v"
    ], capture_output=True, text=True)
    
    if backend_result.returncode == 0:
        print("Backend tests passed")
    else:
        print("Backend tests failed")
        print(backend_result.stdout)
        print(backend_result.stderr)
    
    # Test worker
    print("Testing worker...")
    worker_result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "worker/test_worker.py", "-v"
    ], capture_output=True, text=True)
    
    if worker_result.returncode == 0:
        print("Worker tests passed")
    else:
        print("Worker tests failed")
        print(worker_result.stdout)
        print(worker_result.stderr)
    
    if backend_result.returncode == 0 and worker_result.returncode == 0:
        print("All tests passed")
        return 0
    else:
        print("Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())

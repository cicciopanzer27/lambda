#!/usr/bin/env python3
"""
Simple Test Client for Lambda Visualizer Backend
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"Health check passed: {data['status']}")
            print(f"   Version: {data['version']}")
            return True
        else:
            print(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Health check error: {e}")
        return False

def test_analyze(expression):
    """Test analyze endpoint"""
    print(f"\nAnalyzing expression: {expression}")
    try:
        response = requests.post(f"{BASE_URL}/api/analyze", 
                               json={"expression": expression})
        if response.status_code == 200:
            data = response.json()
            print(f"Analysis successful:")
            print(f"   Complexity: {data['complexity']}")
            print(f"   Abstractions: {data['abstractions']}")
            print(f"   Applications: {data['applications']}")
            print(f"   Variables: {data['variables']}")
            if 'reduction_steps' in data:
                print(f"   Reduction Steps: {data['reduction_steps']}")
            return data
        else:
            print(f"Analysis failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"Analysis error: {e}")
        return None

def test_visualize(expression, duration=3.0):
    """Test visualize endpoint"""
    print(f"\nCreating visualization for: {expression}")
    try:
        response = requests.post(f"{BASE_URL}/api/visualize", 
                               json={"expression": expression, "duration": duration})
        if response.status_code == 200:
            data = response.json()
            print(f"Visualization created:")
            print(f"   Job ID: {data['job_id']}")
            print(f"   Animation File: {data['animation_file']}")
            print(f"   Total Frames: {data['total_frames']}")
            return data
        else:
            print(f"Visualization failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"Visualization error: {e}")
        return None

def run_complex_calculations():
    """Run complex calculations"""
    print("\n" + "="*60)
    print("RUNNING COMPLEX LAMBDA CALCULATIONS")
    print("="*60)
    
    # Test expressions
    expressions = [
        "\\f.(\\x.f(x x))(\\x.f(x x))",  # Y-combinator
        "(\\m.\\n.\\f.\\x.m f (n f x)) (\\f.\\x.f(f x)) (\\f.\\x.f(f(f x)))",  # 2+3
        "(\\m.\\n.\\f.m(n f)) (\\f.\\x.f(f x)) (\\f.\\x.f(f(f x)))",  # 2*3
        "(\\m.\\n.n m) (\\f.\\x.f(f x)) (\\f.\\x.f(f(f x)))",  # 2^3
    ]
    
    results = []
    
    for i, expr in enumerate(expressions, 1):
        print(f"\n--- Calculation {i} ---")
        
        # Analyze
        analysis = test_analyze(expr)
        if analysis:
            results.append(analysis)
        
        # Create visualization
        viz_result = test_visualize(expr, duration=3.0)
        if viz_result:
            results.append(viz_result)
        
        time.sleep(1)  # Small delay between requests
    
    return results

def main():
    """Main test function"""
    print("Lambda Visualizer Backend Test Client")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("\nBackend is not running. Please start it first:")
        print("   python start_simple_backend.py")
        return
    
    # Run complex calculations
    results = run_complex_calculations()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Health check: PASSED")
    print(f"Calculations run: {len(results)}")
    
    print(f"\nBackend is running at: {BASE_URL}")
    print(f"Open master_complex_viewer.html in your browser to use the visualizer")

if __name__ == "__main__":
    main()

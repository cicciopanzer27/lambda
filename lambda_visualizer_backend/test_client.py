#!/usr/bin/env python3
"""
Test Client for Lambda Visualizer Backend
Simple client to test the backend API
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
                print(f"   Services: {data['services']}")
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
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"Analysis error: {e}")
        return None

def test_visualize(expression, duration=5.0):
    """Test visualize endpoint"""
    print(f"\n🎬 Creating visualization for: {expression}")
    try:
        response = requests.post(f"{BASE_URL}/api/visualize", 
                               json={"expression": expression, "duration": duration})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Visualization created:")
            print(f"   Job ID: {data['job_id']}")
            print(f"   Animation File: {data['animation_file']}")
            print(f"   Total Frames: {data['total_frames']}")
            print(f"   Duration: {data['duration']}s")
            return data
        else:
            print(f"❌ Visualization failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Visualization error: {e}")
        return None

def test_complex_expressions():
    """Test complex expressions endpoint"""
    print(f"\n📚 Getting complex expressions...")
    try:
        response = requests.get(f"{BASE_URL}/api/expressions/complex")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data)} complex expressions:")
            for key, expr in data.items():
                print(f"   {key}: {expr['name']} (complexity: {expr['complexity']})")
            return data
        else:
            print(f"❌ Failed to get complex expressions: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting complex expressions: {e}")
        return None

def test_list_files():
    """Test list files endpoint"""
    print(f"\n📁 Listing animation files...")
    try:
        response = requests.get(f"{BASE_URL}/api/files")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data)} animation files:")
            for file_info in data:
                print(f"   {file_info['filename']} ({file_info['size']} bytes)")
            return data
        else:
            print(f"❌ Failed to list files: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error listing files: {e}")
        return None

def run_complex_calculations():
    """Run complex calculations"""
    print("\n" + "="*60)
    print("🧮 RUNNING COMPLEX LAMBDA CALCULATIONS")
    print("="*60)
    
    # Test expressions
    expressions = [
        "\\f.(\\x.f(x x))(\\x.f(x x))",  # Y-combinator
        "(\\m.\\n.\\f.\\x.m f (n f x)) (\\f.\\x.f(f x)) (\\f.\\x.f(f(f x)))",  # 2+3
        "(\\m.\\n.\\f.m(n f)) (\\f.\\x.f(f x)) (\\f.\\x.f(f(f x)))",  # 2*3
        "(\\m.\\n.n m) (\\f.\\x.f(f x)) (\\f.\\x.f(f(f x)))",  # 2^3
        "((\\f.\\g.\\h.\\x.f(g(h x))) (\\x.x)) ((\\y.\\z.y z) (\\a.\\b.a)) ((\\c.\\d.c d) (\\e.\\f.e)) g"  # Very complex
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
        print("\n❌ Backend is not running. Please start it first:")
        print("   python start_simple_backend.py")
        return
    
    # Test complex expressions
    complex_exprs = test_complex_expressions()
    
    # Test list files
    files = test_list_files()
    
    # Run complex calculations
    results = run_complex_calculations()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"✅ Health check: PASSED")
    print(f"✅ Complex expressions: {len(complex_exprs) if complex_exprs else 0} found")
    print(f"✅ Animation files: {len(files) if files else 0} found")
    print(f"✅ Calculations run: {len(results)}")
    
    print(f"\n🌐 Backend is running at: {BASE_URL}")
    print(f"📱 Open master_complex_viewer.html in your browser to use the visualizer")

if __name__ == "__main__":
    main()

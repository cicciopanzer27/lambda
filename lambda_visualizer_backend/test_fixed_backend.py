#!/usr/bin/env python3
"""
Test completo del backend con parser corretto.
"""

import requests
import json
import time

def test_backend():
    """Testa il backend con il parser corretto."""
    
    base_url = "http://localhost:5000"
    
    print("=" * 60)
    print("TEST BACKEND CON PARSER CORRETTO")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        {
            "name": "TEST 1: Identità semplice",
            "expression": "(\\x.x) y",
            "expected_final": "y"
        },
        {
            "name": "TEST 2: Costante K",
            "expression": "(\\x.\\y.x) a b",
            "expected_final": "a"
        },
        {
            "name": "TEST 3: Variabili concatenate (BUG FIX)",
            "expression": "(\\x.x x)",
            "expected_final": "\\x.(x x)"
        },
        {
            "name": "TEST 4: Applicazione n f",
            "expression": "n f",
            "expected_final": "(n f)"
        },
        {
            "name": "TEST 5: Applicazione f x y",
            "expression": "f x y",
            "expected_final": "((f x) y)"
        },
        {
            "name": "TEST 6: IsZero(0) - Espressione complessa utente",
            "expression": "((\\n.n(\\x.\\t.\\f.f)(\\t.\\f.t))(\\f.\\x.x))",
            "expected_final": "\\t.\\f.t"
        }
    ]
    
    for test in test_cases:
        print(f"\n{test['name']}")
        print("-" * 40)
        print(f"Input: {test['expression']}")
        
        try:
            # Test API
            response = requests.post(
                f"{base_url}/api/analyze",
                json={
                    "expression": test['expression'],
                    "max_steps": 50
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result['success']:
                    print(f"✅ SUCCESS")
                    print(f"   Parsed: {result['parsed_term']}")
                    print(f"   Final: {result['beta_reduction']['final_term']}")
                    print(f"   Steps: {result['beta_reduction']['steps_taken']}")
                    print(f"   Normal form: {result['beta_reduction']['is_normal_form']}")
                    
                    if result['beta_reduction'].get('combinator'):
                        print(f"   Combinator: {result['beta_reduction']['combinator']}")
                    
                    # Check if result matches expected
                    if result['beta_reduction']['final_term'] == test['expected_final']:
                        print(f"   ✅ Expected result: {test['expected_final']}")
                    else:
                        print(f"   ⚠️  Expected: {test['expected_final']}")
                        print(f"   ⚠️  Got: {result['beta_reduction']['final_term']}")
                else:
                    print(f"❌ API Error: {result.get('error', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Backend not running?")
            print("   Start backend with: python start_backend.py")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETATO")
    print("=" * 60)

if __name__ == "__main__":
    test_backend()

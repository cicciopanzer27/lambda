#!/usr/bin/env python3
"""
Test per identificare i bug nel parser lambda.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.complete_beta_reduction import LambdaParser, BetaReducer, ReductionStrategy

def test_parser_bugs():
    """Testa i bug identificati nel parser."""
    
    parser = LambdaParser()
    reducer = BetaReducer(ReductionStrategy.NORMAL_ORDER)
    
    print("=" * 60)
    print("TEST PARSER BUGS - Lambda Visualizer")
    print("=" * 60)
    
    # Test cases che dovrebbero fallire o dare risultati sbagliati
    test_cases = [
        {
            "name": "TEST 1: Variabili concatenate",
            "input": "(\\x.x x)",
            "expected_parsed": "Application(Variable(x), Variable(x))",
            "expected_reduction": "x"
        },
        {
            "name": "TEST 2: Applicazione n f",
            "input": "n f",
            "expected_parsed": "Application(Variable(n), Variable(f))",
            "expected_reduction": "n f"
        },
        {
            "name": "TEST 3: Costante K con sostituzione",
            "input": "(\\x.\\y.x) a b",
            "expected_parsed": "Application(Application(Lambda(x, Lambda(y, Variable(x))), Variable(a)), Variable(b))",
            "expected_reduction": "a"
        },
        {
            "name": "TEST 4: Applicazione f x y",
            "input": "f x y",
            "expected_parsed": "Application(Application(Variable(f), Variable(x)), Variable(y))",
            "expected_reduction": "f x y"
        },
        {
            "name": "TEST 5: Parentesi con applicazione",
            "input": "(p q) p",
            "expected_parsed": "Application(Application(Variable(p), Variable(q)), Variable(p))",
            "expected_reduction": "(p q) p"
        },
        {
            "name": "TEST 6: Identità applicata",
            "input": "(\\x.x) y",
            "expected_parsed": "Application(Lambda(x, Variable(x)), Variable(y))",
            "expected_reduction": "y"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{test['name']}")
        print("-" * 40)
        print(f"Input: {test['input']}")
        
        try:
            # Test parsing
            parsed = parser.parse(test['input'])
            print(f"Parsed: {parsed}")
            print(f"Expected: {test['expected_parsed']}")
            
            # Test reduction
            result = reducer.reduce(parsed, max_steps=10)
            print(f"Reduced: {result['final_term']}")
            print(f"Expected: {test['expected_reduction']}")
            print(f"Steps: {result['steps']}")
            
            # Check if parsing is correct
            parsed_str = str(parsed)
            if "xx" in parsed_str and "x x" in test['input']:
                print("BUG: Variabili concatenate!")
            elif "nf" in parsed_str and "n f" in test['input']:
                print("BUG: Applicazione non separata!")
            elif "fxy" in parsed_str and "f x y" in test['input']:
                print("BUG: Applicazione multipla non separata!")
            else:
                print("Parsing sembra corretto")
            
            # Check reduction
            if result['final_term'] == test['expected_reduction']:
                print("Riduzione corretta")
            else:
                print("Riduzione sbagliata")
                
        except Exception as e:
            print(f"ERRORE: {e}")
    
    print("\n" + "=" * 60)
    print("ANALISI TOKENIZZAZIONE")
    print("=" * 60)
    
    # Test tokenizzazione
    test_expressions = [
        "(\\x.x x)",
        "n f",
        "f x y",
        "(p q) p"
    ]
    
    for expr in test_expressions:
        print(f"\nInput: {expr}")
        tokens = parser._tokenize(expr)
        print(f"Tokens: {tokens}")
        
        # Mostra come viene processato
        processed = expr.replace('(', ' ( ').replace(')', ' ) ').replace('\\', ' \\ ').replace('.', ' . ')
        print(f"Processed: '{processed}'")
        print(f"Split: {[t for t in processed.split() if t]}")

if __name__ == "__main__":
    test_parser_bugs()

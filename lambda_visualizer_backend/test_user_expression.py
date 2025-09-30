#!/usr/bin/env python3
"""
Test con l'espressione complessa dell'utente.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.correct_lambda_parser import CorrectLambdaParser, CorrectBetaReducer, ReductionStrategy

def test_user_expression():
    """Testa l'espressione complessa dell'utente."""
    
    parser = CorrectLambdaParser()
    reducer = CorrectBetaReducer(ReductionStrategy.NORMAL_ORDER)
    
    # L'espressione complessa dell'utente: IsZero(0)
    expression = "((\\n.n(\\x.\\t.\\f.f)(\\t.\\f.t))(\\f.\\x.x))"
    
    print("=" * 60)
    print("TEST ESPRESSIONE COMPLESSA UTENTE")
    print("=" * 60)
    print(f"Input: {expression}")
    
    try:
        # Tokenizzazione
        tokens = parser._tokenize(expression)
        print(f"Tokens: {tokens}")
        
        # Parsing
        term = parser.parse(expression)
        print(f"Parsed: {term}")
        
        # Beta reduction
        result = reducer.reduce(term, max_steps=50)
        print(f"Final: {result['final_term']}")
        print(f"Steps: {result['steps']}")
        print(f"Normal form: {result['is_normal_form']}")
        
        if result['combinator']:
            print(f"Combinator: {result['combinator']}")
        
        print("\nReduction steps:")
        for step in result['reduction_steps']:
            print(f"  Step {step['step']}: {step['term']}")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_user_expression()

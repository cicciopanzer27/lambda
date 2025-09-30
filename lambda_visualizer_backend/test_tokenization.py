#!/usr/bin/env python3
"""
Test specifico per la tokenizzazione.
"""

import re

def test_tokenization():
    """Testa diversi approcci di tokenizzazione."""
    
    test_cases = [
        "(\\x.x x)",
        "n f",
        "f x y",
        "(p q) p",
        "\\x.\\y.x"
    ]
    
    for expr in test_cases:
        print(f"\nInput: {expr}")
        
        # Approccio 1: Regex semplice
        expr1 = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1 \2', expr)
        print(f"Regex simple: '{expr1}'")
        
        # Approccio 2: Regex più specifica
        expr2 = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1 \2', expr)
        expr2 = expr2.replace('(', ' ( ').replace(')', ' ) ').replace('\\', ' \\ ').replace('.', ' . ')
        tokens2 = [t for t in expr2.split() if t]
        print(f"With spaces: '{expr2}'")
        print(f"Tokens: {tokens2}")
        
        # Approccio 3: Tokenizzazione più intelligente
        tokens3 = []
        i = 0
        while i < len(expr):
            if expr[i] in '()\\.':
                tokens3.append(expr[i])
                i += 1
            elif expr[i].isalpha():
                # Leggi tutta la variabile
                var = ''
                while i < len(expr) and expr[i].isalpha():
                    var += expr[i]
                    i += 1
                tokens3.append(var)
            elif expr[i].isspace():
                i += 1
            else:
                i += 1
        
        print(f"Smart tokens: {tokens3}")

if __name__ == "__main__":
    test_tokenization()

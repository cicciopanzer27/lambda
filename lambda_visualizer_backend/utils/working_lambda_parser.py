#!/usr/bin/env python3
"""
Working Lambda Calculus Parser
Parser funzionante per lambda calculus.
"""

import re
from typing import Dict, List, Any, Optional, Set, Union

class WorkingLambdaParser:
    """Parser funzionante per lambda calculus."""
    
    def __init__(self):
        pass
    
    def parse(self, expression: str) -> Dict[str, Any]:
        """Parsa un'espressione lambda calculus."""
        try:
            # Preprocessing: converti λ in \ per consistenza
            expr = expression.replace('λ', '\\')
            
            # Parsa l'espressione usando regex
            ast = self._parse_expression(expr)
            
            return ast
            
        except Exception as e:
            raise ValueError(f"Parse error: {e}")
    
    def _parse_expression(self, expr: str) -> Dict[str, Any]:
        """Parsa un'espressione usando regex."""
        expr = expr.strip()
        
        # Rimuovi parentesi esterne se presenti
        if expr.startswith('(') and expr.endswith(')'):
            expr = expr[1:-1]
        
        # Cerca pattern lambda: \x.term
        lambda_match = re.match(r'^\\([a-zA-Z?@#$%&*+-=<>]+)\.(.+)$', expr)
        if lambda_match:
            param = lambda_match.group(1)
            body = lambda_match.group(2)
            return {
                "type": "lambda",
                "parameter": param,
                "body": self._parse_expression(body)
            }
        
        # Cerca applicazione: term1 term2
        # Trova il primo spazio che separa due termini
        paren_count = 0
        for i, char in enumerate(expr):
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
            elif char == ' ' and paren_count == 0:
                # Questo è il primo spazio che separa due termini
                left = expr[:i].strip()
                right = expr[i+1:].strip()
                return {
                    "type": "application",
                    "function": self._parse_expression(left),
                    "argument": self._parse_expression(right)
                }
        
        # Se non è né lambda né applicazione, è una variabile
        return {
            "type": "variable",
            "name": expr
        }
    
    def reduce(self, ast: Dict[str, Any], max_steps: int = 100) -> Dict[str, Any]:
        """Riduce un AST lambda calculus."""
        steps = []
        current = ast
        step_count = 0
        
        # Record initial state
        steps.append({
            "step": 0,
            "term": self._ast_to_string(current),
            "action": "initial"
        })
        
        while step_count < max_steps:
            # Find next redex
            redex = self._find_redex(current)
            if not redex:
                break
                
            # Perform reduction
            current = self._reduce_redex(current, redex)
            step_count += 1
            
            # Record step
            steps.append({
                "step": step_count,
                "term": self._ast_to_string(current),
                "action": "beta_reduction"
            })
        
        return {
            "original_term": self._ast_to_string(ast),
            "final_term": self._ast_to_string(current),
            "is_normal_form": self._find_redex(current) is None,
            "steps_taken": step_count,
            "max_steps_reached": step_count >= max_steps,
            "reduction_steps": steps
        }
    
    def _find_redex(self, ast: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Trova il prossimo redex."""
        if ast["type"] == "application":
            if ast["function"]["type"] == "lambda":
                return ast
            else:
                # Try left side
                left_redex = self._find_redex(ast["function"])
                if left_redex:
                    return left_redex
                # Try right side
                return self._find_redex(ast["argument"])
        elif ast["type"] == "lambda":
            return self._find_redex(ast["body"])
        else:
            return None
    
    def _reduce_redex(self, ast: Dict[str, Any], redex: Dict[str, Any]) -> Dict[str, Any]:
        """Riduce un redex specifico."""
        if ast == redex:
            # This is the redex
            return self._substitute(redex["function"]["body"], redex["function"]["parameter"], redex["argument"])
        elif ast["type"] == "application":
            new_function = self._reduce_redex(ast["function"], redex)
            if new_function != ast["function"]:
                return {"type": "application", "function": new_function, "argument": ast["argument"]}
            new_argument = self._reduce_redex(ast["argument"], redex)
            return {"type": "application", "function": ast["function"], "argument": new_argument}
        elif ast["type"] == "lambda":
            new_body = self._reduce_redex(ast["body"], redex)
            return {"type": "lambda", "parameter": ast["parameter"], "body": new_body}
        else:
            return ast
    
    def _substitute(self, ast: Dict[str, Any], var: str, replacement: Dict[str, Any]) -> Dict[str, Any]:
        """Sostituisce una variabile con un termine."""
        if ast["type"] == "variable":
            if ast["name"] == var:
                return replacement
            else:
                return ast
        elif ast["type"] == "application":
            return {
                "type": "application",
                "function": self._substitute(ast["function"], var, replacement),
                "argument": self._substitute(ast["argument"], var, replacement)
            }
        elif ast["type"] == "lambda":
            if ast["parameter"] == var:
                return ast
            else:
                return {
                    "type": "lambda",
                    "parameter": ast["parameter"],
                    "body": self._substitute(ast["body"], var, replacement)
                }
        else:
            return ast
    
    def _ast_to_string(self, ast: Dict[str, Any]) -> str:
        """Converte un AST in stringa."""
        if ast["type"] == "variable":
            return ast["name"]
        elif ast["type"] == "lambda":
            return f"λ{ast['parameter']}.{self._ast_to_string(ast['body'])}"
        elif ast["type"] == "application":
            func_str = self._ast_to_string(ast["function"])
            arg_str = self._ast_to_string(ast["argument"])
            return f"({func_str} {arg_str})"
        else:
            return str(ast)

# Test
if __name__ == "__main__":
    parser = WorkingLambdaParser()
    
    test_cases = [
        "(λx.x) y",
        "(λx.λy.x) a b",
        "λx.λy.x",
        "λx.λy.y"
    ]
    
    for expr in test_cases:
        try:
            print(f"\n=== Test: {expr} ===")
            ast = parser.parse(expr)
            print(f"Parsed: {ast}")
            result = parser.reduce(ast, max_steps=10)
            print(f"Result: {result['final_term']}")
            print(f"Steps: {result['steps_taken']}")
        except Exception as e:
            print(f"Error: {e}")

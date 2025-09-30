#!/usr/bin/env python3
"""
Simple Lambda Calculus Parser using PyParsing
Parser semplice per lambda calculus usando PyParsing.
"""

from pyparsing import *
import re

# Configurazione
ParserElement.enablePackrat()

# Token base
LPAR, RPAR = map(Suppress, "()")
DOT = Suppress(".")
LAMBDA = oneOf("λ \\")  # Accetta sia λ che \

# Variabile: lettere e caratteri speciali
VARIABLE = Word(alphas + "?@#$%&*+-=<>", alphanums + "?@#$%&*+-=<>")

# Definizione ricorsiva del termine
term = Forward()

# Atom: variabile o espressione tra parentesi
atom = VARIABLE | Group(LPAR + term + RPAR)

# Applicazione: atomo seguito da altri atomi
application = atom + ZeroOrMore(atom)

# Lambda: λ variabile . termine
lambda_expr = LAMBDA + VARIABLE + DOT + term

# Termine: applicazione o lambda
term <<= lambda_expr | application

def parse_lambda(expression):
    """Parsa un'espressione lambda calculus."""
    try:
        # Preprocessing: converti λ in \ per consistenza
        expr = expression.replace('λ', '\\')
        
        # Debug: stampa l'espressione processata
        print(f"Processed expression: {expr}")
        print(f"Expression bytes: {expr.encode('utf-8')}")
        
        # Parsa l'espressione
        result = term.parseString(expr, parseAll=True)
        
        # Converte in struttura dati semplice
        return _convert_to_ast(result[0])
        
    except ParseException as e:
        raise ValueError(f"Parse error: {e}")
    except Exception as e:
        raise ValueError(f"Parse error: {e}")

def _convert_to_ast(parsed):
    """Converte il risultato del parsing in AST."""
    if isinstance(parsed, str):
        return {"type": "variable", "name": parsed}
    elif isinstance(parsed, list):
        if len(parsed) == 1:
            return _convert_to_ast(parsed[0])
        else:
            # Applicazione
            result = _convert_to_ast(parsed[0])
            for i in range(1, len(parsed)):
                result = {
                    "type": "application",
                    "function": result,
                    "argument": _convert_to_ast(parsed[i])
                }
            return result
    else:
        return parsed

def reduce_lambda(ast, max_steps=100):
    """Riduce un AST lambda calculus."""
    steps = []
    current = ast
    step_count = 0
    
    # Record initial state
    steps.append({
        "step": 0,
        "term": _ast_to_string(current),
        "action": "initial"
    })
    
    while step_count < max_steps:
        # Find next redex
        redex = _find_redex(current)
        if not redex:
            break
            
        # Perform reduction
        current = _reduce_redex(current, redex)
        step_count += 1
        
        # Record step
        steps.append({
            "step": step_count,
            "term": _ast_to_string(current),
            "action": "beta_reduction"
        })
    
    return {
        "original_term": _ast_to_string(ast),
        "final_term": _ast_to_string(current),
        "is_normal_form": _find_redex(current) is None,
        "steps_taken": step_count,
        "max_steps_reached": step_count >= max_steps,
        "reduction_steps": steps
    }

def _find_redex(ast):
    """Trova il prossimo redex."""
    if ast["type"] == "application":
        if ast["function"]["type"] == "lambda":
            return ast
        else:
            # Try left side
            left_redex = _find_redex(ast["function"])
            if left_redex:
                return left_redex
            # Try right side
            return _find_redex(ast["argument"])
    elif ast["type"] == "lambda":
        return _find_redex(ast["body"])
    else:
        return None

def _reduce_redex(ast, redex):
    """Riduce un redex specifico."""
    if ast == redex:
        # This is the redex
        return _substitute(redex["function"]["body"], redex["function"]["parameter"], redex["argument"])
    elif ast["type"] == "application":
        new_function = _reduce_redex(ast["function"], redex)
        if new_function != ast["function"]:
            return {"type": "application", "function": new_function, "argument": ast["argument"]}
        new_argument = _reduce_redex(ast["argument"], redex)
        return {"type": "application", "function": ast["function"], "argument": new_argument}
    elif ast["type"] == "lambda":
        new_body = _reduce_redex(ast["body"], redex)
        return {"type": "lambda", "parameter": ast["parameter"], "body": new_body}
    else:
        return ast

def _substitute(ast, var, replacement):
    """Sostituisce una variabile con un termine."""
    if ast["type"] == "variable":
        if ast["name"] == var:
            return replacement
        else:
            return ast
    elif ast["type"] == "application":
        return {
            "type": "application",
            "function": _substitute(ast["function"], var, replacement),
            "argument": _substitute(ast["argument"], var, replacement)
        }
    elif ast["type"] == "lambda":
        if ast["parameter"] == var:
            return ast
        else:
            return {
                "type": "lambda",
                "parameter": ast["parameter"],
                "body": _substitute(ast["body"], var, replacement)
            }
    else:
        return ast

def _ast_to_string(ast):
    """Converte un AST in stringa."""
    if ast["type"] == "variable":
        return ast["name"]
    elif ast["type"] == "lambda":
        return f"λ{ast['parameter']}.{_ast_to_string(ast['body'])}"
    elif ast["type"] == "application":
        func_str = _ast_to_string(ast["function"])
        arg_str = _ast_to_string(ast["argument"])
        return f"({func_str} {arg_str})"
    else:
        return str(ast)

# Test
if __name__ == "__main__":
    test_cases = [
        "(λx.x) y",
        "(λx.λy.x) a b",
        "λx.λy.x",
        "λx.λy.y"
    ]
    
    for expr in test_cases:
        try:
            print(f"\n=== Test: {expr} ===")
            ast = parse_lambda(expr)
            print(f"Parsed: {ast}")
            result = reduce_lambda(ast, max_steps=10)
            print(f"Result: {result['final_term']}")
            print(f"Steps: {result['steps_taken']}")
        except Exception as e:
            print(f"Error: {e}")

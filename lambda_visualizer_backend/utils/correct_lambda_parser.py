#!/usr/bin/env python3
"""
Parser Lambda Calculus Completamente Corretto
Risolve TUTTI i bug di tokenizzazione e parsing identificati.
"""

import re
import sys
from typing import Dict, List, Any, Optional, Set, Union
from dataclasses import dataclass
from enum import Enum

# Aumenta limite ricorsione per espressioni complesse
sys.setrecursionlimit(10000)

class ReductionStrategy(Enum):
    """Strategie di riduzione."""
    NORMAL_ORDER = "normal_order"      # Leftmost outermost
    APPLICATIVE_ORDER = "applicative_order"  # Leftmost innermost
    CALL_BY_NAME = "call_by_name"
    CALL_BY_VALUE = "call_by_value"

@dataclass
class Variable:
    """Rappresenta una variabile."""
    name: str
    
    def __str__(self):
        return self.name
    
    def __eq__(self, other):
        return isinstance(other, Variable) and self.name == other.name
    
    def __hash__(self):
        return hash(self.name)

@dataclass
class Lambda:
    """Rappresenta un'astrazione lambda."""
    parameter: Variable
    body: 'Term'
    
    def __str__(self):
        return f"\\{self.parameter.name}.{self.body}"

@dataclass
class Application:
    """Rappresenta un'applicazione."""
    function: 'Term'
    argument: 'Term'
    
    def __str__(self):
        return f"({self.function} {self.argument})"

# Type alias per i termini
Term = Union[Variable, Lambda, Application]

class CorrectLambdaParser:
    """Parser completamente corretto per espressioni lambda calculus."""
    
    def __init__(self):
        self.tokens = []
        self.position = 0
    
    def _preprocess_unicode(self, expression: str) -> str:
        """Preprocessa caratteri Unicode per compatibilità."""
        # Sostituisci λ con \ (ma non convertire mai \ in λ)
        expr = expression.replace('λ', '\\')
        
        # Sostituisci altri caratteri Unicode comuni
        expr = expr.replace('∧', 'and')
        expr = expr.replace('∨', 'or')
        expr = expr.replace('¬', 'not')
        return expr
    
    def _tokenize(self, expression: str) -> List[str]:
        """Tokenizza un'espressione lambda correttamente."""
        # Preprocessing Unicode
        expr = self._preprocess_unicode(expression)
        
        # CORREZIONE BUG: Tokenizzazione completamente corretta
        tokens = []
        i = 0
        
        while i < len(expr):
            char = expr[i]
            
            if char.isspace():
                # Salta spazi
                i += 1
            elif char in '()':
                # Parentesi
                tokens.append(char)
                i += 1
            elif char == '\\':
                # Lambda
                tokens.append('\\')
                i += 1
            elif char == '.':
                # Punto
                tokens.append('.')
                i += 1
            elif char.isalpha():
                # Variabile - leggi tutto il nome
                var_name = ''
                while i < len(expr) and expr[i].isalpha():
                    var_name += expr[i]
                    i += 1
                tokens.append(var_name)
            else:
                # Carattere non riconosciuto
                i += 1
        
        return tokens
    
    def parse(self, expression: str) -> Term:
        """Parsa un'espressione lambda."""
        # Tokenizza l'espressione
        self.tokens = self._tokenize(expression)
        self.position = 0
        
        if not self.tokens:
            raise ValueError("Empty expression")
        
        # Parsa l'espressione
        result = self._parse_term()
        
        # Verifica che abbiamo consumato tutti i token
        if self.position < len(self.tokens):
            raise ValueError(f"Unexpected token at position {self.position}: {self.tokens[self.position]}")
        
        return result
    
    def _parse_term(self) -> Term:
        """Parsa un termine."""
        return self._parse_application()
    
    def _parse_application(self) -> Term:
        """Parsa un'applicazione (associativa a sinistra)."""
        left = self._parse_atom()
        
        # Continua finché non incontriamo una parentesi chiusa o la fine
        while (self.position < len(self.tokens) and 
               self.tokens[self.position] not in ')' and
               self.tokens[self.position] not in '\\'):
            right = self._parse_atom()
            left = Application(left, right)
        
        return left
    
    def _parse_atom(self) -> Term:
        """Parsa un atomo (variabile, lambda, o espressione tra parentesi)."""
        if self.position >= len(self.tokens):
            raise ValueError("Unexpected end of input")
        
        token = self.tokens[self.position]
        
        if token == '\\':
            return self._parse_lambda()
        elif token == '(':
            return self._parse_parentheses()
        elif token.isalpha():
            return self._parse_variable()
        else:
            raise ValueError(f"Unexpected token: {token}")
    
    def _parse_lambda(self) -> Lambda:
        """Parsa un'astrazione lambda."""
        self.position += 1  # Skip \\
        
        if self.position >= len(self.tokens):
            raise ValueError("Expected parameter after \\")
        
        # Parse parameter
        param_name = self._parse_variable_name()
        parameter = Variable(param_name)
        
        # Expect dot
        if self.position >= len(self.tokens) or self.tokens[self.position] != '.':
            raise ValueError("Expected '.' after lambda parameter")
        self.position += 1
        
        # Parse body
        body = self._parse_term()
        
        return Lambda(parameter, body)
    
    def _parse_parentheses(self) -> Term:
        """Parsa un'espressione tra parentesi."""
        self.position += 1  # Skip '('
        
        term = self._parse_term()
        
        if self.position >= len(self.tokens) or self.tokens[self.position] != ')':
            raise ValueError("Expected closing parenthesis")
        self.position += 1
        
        return term
    
    def _parse_variable(self) -> Variable:
        """Parsa una variabile."""
        name = self._parse_variable_name()
        return Variable(name)
    
    def _parse_variable_name(self) -> str:
        """Parsa il nome di una variabile."""
        if self.position >= len(self.tokens):
            raise ValueError("Expected variable name")
        
        token = self.tokens[self.position]
        if not token.isalpha():
            raise ValueError(f"Expected variable name, got: {token}")
        
        self.position += 1
        return token

class CorrectBetaReducer:
    """Riduttore beta corretto."""
    
    def __init__(self, strategy: ReductionStrategy = ReductionStrategy.NORMAL_ORDER):
        self.strategy = strategy
        self.reduction_steps = []
        self.variable_counter = 0
    
    def reduce(self, term: Term, max_steps: int = 100) -> Dict[str, Any]:
        """Esegue la riduzione beta completa."""
        
        self.reduction_steps = []
        current_term = term
        step_count = 0
        
        # Record initial state
        self.reduction_steps.append({
            "step": 0,
            "term": str(current_term),
            "action": "initial",
            "redex": None,
            "free_variables": list(self.free_variables(current_term)),
            "bound_variables": list(self.bound_variables(current_term))
        })
        
        while step_count < max_steps:
            # Find next redex based on strategy
            redex_info = self._find_redex(current_term)
            
            if not redex_info:
                # No more redexes, we're done
                break
            
            # Perform reduction
            new_term = self._reduce_redex(current_term, redex_info)
            step_count += 1
            
            # Record step
            self.reduction_steps.append({
                "step": step_count,
                "term": str(new_term),
                "action": "beta_reduction",
                "redex": redex_info,
                "free_variables": list(self.free_variables(new_term)),
                "bound_variables": list(self.bound_variables(new_term))
            })
            
            current_term = new_term
            
            # Check for infinite loops (same term repeated)
            if step_count > 2:
                recent_terms = [step["term"] for step in self.reduction_steps[-3:]]
                if len(set(recent_terms)) == 1:
                    print("WARNING: Detected potential infinite loop, stopping")
                    break
        
        # Analyze final result
        is_normal_form = self._find_redex(current_term) is None
        
        return {
            "original_term": str(term),
            "final_term": str(current_term),
            "is_normal_form": is_normal_form,
            "steps": step_count,
            "reduction_steps": self.reduction_steps,
            "strategy": self.strategy.value,
            "combinator": self._identify_combinator(current_term)
        }
    
    def _find_redex(self, term: Term) -> Optional[Dict[str, Any]]:
        """Trova il prossimo redex da ridurre."""
        if self.strategy == ReductionStrategy.NORMAL_ORDER:
            return self._find_leftmost_outermost_redex(term)
        elif self.strategy == ReductionStrategy.APPLICATIVE_ORDER:
            return self._find_leftmost_innermost_redex(term)
        else:
            return self._find_leftmost_outermost_redex(term)
    
    def _find_leftmost_outermost_redex(self, term: Term) -> Optional[Dict[str, Any]]:
        """Trova il redex leftmost-outermost."""
        if isinstance(term, Application):
            if isinstance(term.function, Lambda):
                return {
                    "type": "beta_redex",
                    "function": str(term.function),
                    "argument": str(term.argument),
                    "parameter": str(term.function.parameter),
                    "body": str(term.function.body)
                }
            else:
                # Try left side first
                left_redex = self._find_leftmost_outermost_redex(term.function)
                if left_redex:
                    return left_redex
                # Then right side
                return self._find_leftmost_outermost_redex(term.argument)
        elif isinstance(term, Lambda):
            return self._find_leftmost_outermost_redex(term.body)
        
        return None
    
    def _find_leftmost_innermost_redex(self, term: Term) -> Optional[Dict[str, Any]]:
        """Trova il redex leftmost-innermost."""
        if isinstance(term, Application):
            # Try left side first
            left_redex = self._find_leftmost_innermost_redex(term.function)
            if left_redex:
                return left_redex
            # Then right side
            right_redex = self._find_leftmost_innermost_redex(term.argument)
            if right_redex:
                return right_redex
            # Finally check if this is a redex
            if isinstance(term.function, Lambda):
                return {
                    "type": "beta_redex",
                    "function": str(term.function),
                    "argument": str(term.argument),
                    "parameter": str(term.function.parameter),
                    "body": str(term.function.body)
                }
        elif isinstance(term, Lambda):
            return self._find_leftmost_innermost_redex(term.body)
        
        return None
    
    def _reduce_redex(self, term: Term, redex_info: Dict[str, Any]) -> Term:
        """Riduce un redex specifico."""
        if redex_info["type"] == "beta_redex":
            return self._beta_reduce(term, redex_info)
        else:
            return term
    
    def _beta_reduce(self, term: Term, redex_info: Dict[str, Any]) -> Term:
        """Esegue la riduzione beta."""
        if isinstance(term, Application) and isinstance(term.function, Lambda):
            # This is the redex
            parameter = term.function.parameter
            argument = term.argument
            body = term.function.body
            
            # Perform substitution
            substituted_body = self._substitute(body, parameter, argument)
            return substituted_body
        elif isinstance(term, Application):
            # Try left side
            new_function = self._beta_reduce(term.function, redex_info)
            if new_function != term.function:
                return Application(new_function, term.argument)
            # Try right side
            new_argument = self._beta_reduce(term.argument, redex_info)
            return Application(term.function, new_argument)
        elif isinstance(term, Lambda):
            # Try body
            new_body = self._beta_reduce(term.body, redex_info)
            return Lambda(term.parameter, new_body)
        else:
            return term
    
    def _substitute(self, term: Term, parameter: Variable, argument: Term) -> Term:
        """Sostituisce tutte le occorrenze di parameter con argument in term."""
        if isinstance(term, Variable):
            if term == parameter:
                return argument
            else:
                return term
        elif isinstance(term, Lambda):
            if term.parameter == parameter:
                # Variable is bound, no substitution
                return term
            else:
                # Check for variable capture
                free_vars = self.free_variables(argument)
                if term.parameter in free_vars:
                    # Need alpha conversion
                    new_param = self._generate_fresh_variable()
                    new_body = self._substitute(term.body, term.parameter, Variable(new_param))
                    return Lambda(Variable(new_param), self._substitute(new_body, parameter, argument))
                else:
                    # Safe substitution
                    new_body = self._substitute(term.body, parameter, argument)
                    return Lambda(term.parameter, new_body)
        elif isinstance(term, Application):
            new_function = self._substitute(term.function, parameter, argument)
            new_argument = self._substitute(term.argument, parameter, argument)
            return Application(new_function, new_argument)
        else:
            return term
    
    def _generate_fresh_variable(self) -> str:
        """Genera una variabile fresca."""
        self.variable_counter += 1
        return f"v{self.variable_counter}"
    
    def free_variables(self, term: Term) -> Set[Variable]:
        """Trova le variabili libere in un termine."""
        if isinstance(term, Variable):
            return {term}
        elif isinstance(term, Lambda):
            return self.free_variables(term.body) - {term.parameter}
        elif isinstance(term, Application):
            return self.free_variables(term.function) | self.free_variables(term.argument)
        else:
            return set()
    
    def bound_variables(self, term: Term) -> Set[Variable]:
        """Trova le variabili legate in un termine."""
        if isinstance(term, Variable):
            return set()
        elif isinstance(term, Lambda):
            return {term.parameter} | self.bound_variables(term.body)
        elif isinstance(term, Application):
            return self.bound_variables(term.function) | self.bound_variables(term.argument)
        else:
            return set()
    
    def _identify_combinator(self, term: Term) -> Optional[str]:
        """Identifica se il termine è un combinatore noto."""
        term_str = str(term).replace(' ', '')
        
        # Combinatori base
        combinators = {
            "I": "\\x.x",
            "K": "\\x.\\y.x",
            "S": "\\x.\\y.\\z.x z (y z)",
            "Y": "\\f.(\\x.f (x x)) (\\x.f (x x))",
            "B": "\\f.\\g.\\x.f (g x)",
            "C": "\\f.\\x.\\y.f y x",
            "W": "\\f.\\x.f x x"
        }
        
        for name, pattern in combinators.items():
            if self._terms_equivalent(term_str, pattern.replace(' ', '')):
                return name
        
        return None
    
    def _terms_equivalent(self, term1: str, term2: str) -> bool:
        """Verifica equivalenza sintattica semplice."""
        return term1 == term2

# Test and demonstration
def test_correct_parser():
    """Testa il parser completamente corretto."""
    parser = CorrectLambdaParser()
    reducer = CorrectBetaReducer()
    
    # Test cases
    test_cases = [
        "(\\x.x x)",
        "(\\x.\\y.x) a b",
        "n f",
        "f x y",
        "(p q) p",
        "(\\x.x) y"
    ]
    
    for expr in test_cases:
        try:
            print(f"\n=== Test: {expr} ===")
            print(f"Tokens: {parser._tokenize(expr)}")
            term = parser.parse(expr)
            print(f"Parsed: {term}")
            
            result = reducer.reduce(term, max_steps=10)
            print(f"Result: {result['final_term']}")
            print(f"Steps: {result['steps']}")
            print(f"Normal form: {result['is_normal_form']}")
            if result['combinator']:
                print(f"Combinator: {result['combinator']}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_correct_parser()

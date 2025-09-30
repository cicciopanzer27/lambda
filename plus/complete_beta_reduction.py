#!/usr/bin/env python3
"""
Complete Beta Reduction System
Sistema completo e corretto per la riduzione beta nel lambda calculus.
Risolve la criticità 3.4: Semplificazione della Logica di Riduzione.
"""

import re
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        return f"λ{self.parameter}.{self.body}"

@dataclass
class Application:
    """Rappresenta un'applicazione di funzione."""
    function: 'Term'
    argument: 'Term'
    
    def __str__(self):
        func_str = str(self.function)
        arg_str = str(self.argument)
        
        # Add parentheses when necessary
        if isinstance(self.function, Application):
            func_str = f"({func_str})"
        if isinstance(self.argument, (Lambda, Application)):
            arg_str = f"({arg_str})"
            
        return f"{func_str} {arg_str}"

# Type alias for terms
Term = Union[Variable, Lambda, Application]

class LambdaParser:
    """Parser per espressioni lambda."""
    
    def __init__(self):
        self.position = 0
        self.text = ""
    
    def parse(self, expression: str) -> Term:
        """Parsa un'espressione lambda in un AST."""
        self.text = expression.replace(' ', '')  # Remove spaces
        self.position = 0
        
        try:
            result = self._parse_term()
            if self.position < len(self.text):
                raise ValueError(f"Unexpected character at position {self.position}: {self.text[self.position]}")
            return result
        except Exception as e:
            raise ValueError(f"Parse error: {e}")
    
    def _parse_term(self) -> Term:
        """Parsa un termine."""
        return self._parse_application()
    
    def _parse_application(self) -> Term:
        """Parsa un'applicazione (associativa a sinistra)."""
        left = self._parse_atom()
        
        while self.position < len(self.text) and self.text[self.position] not in ')':
            right = self._parse_atom()
            left = Application(left, right)
        
        return left
    
    def _parse_atom(self) -> Term:
        """Parsa un atomo (variabile, lambda, o espressione tra parentesi)."""
        if self.position >= len(self.text):
            raise ValueError("Unexpected end of input")
        
        char = self.text[self.position]
        
        if char == 'λ' or char == '\\':
            return self._parse_lambda()
        elif char == '(':
            return self._parse_parentheses()
        elif char.isalpha():
            return self._parse_variable()
        else:
            raise ValueError(f"Unexpected character: {char}")
    
    def _parse_lambda(self) -> Lambda:
        """Parsa un'astrazione lambda."""
        self.position += 1  # Skip λ or \\
        
        if self.position >= len(self.text):
            raise ValueError("Expected parameter after λ")
        
        # Parse parameter
        param_name = self._parse_variable_name()
        parameter = Variable(param_name)
        
        # Expect dot
        if self.position >= len(self.text) or self.text[self.position] != '.':
            raise ValueError("Expected '.' after lambda parameter")
        self.position += 1
        
        # Parse body
        body = self._parse_term()
        
        return Lambda(parameter, body)
    
    def _parse_parentheses(self) -> Term:
        """Parsa un'espressione tra parentesi."""
        self.position += 1  # Skip '('
        
        term = self._parse_term()
        
        if self.position >= len(self.text) or self.text[self.position] != ')':
            raise ValueError("Expected closing parenthesis")
        self.position += 1
        
        return term
    
    def _parse_variable(self) -> Variable:
        """Parsa una variabile."""
        name = self._parse_variable_name()
        return Variable(name)
    
    def _parse_variable_name(self) -> str:
        """Parsa il nome di una variabile."""
        if self.position >= len(self.text) or not self.text[self.position].isalpha():
            raise ValueError("Expected variable name")
        
        name = self.text[self.position]
        self.position += 1
        
        # Support multi-character variable names
        while (self.position < len(self.text) and 
               (self.text[self.position].isalnum() or self.text[self.position] == '_')):
            name += self.text[self.position]
            self.position += 1
        
        return name

class BetaReducer:
    """Riduttore beta completo e corretto."""
    
    def __init__(self, strategy: ReductionStrategy = ReductionStrategy.NORMAL_ORDER):
        self.strategy = strategy
        self.reduction_steps = []
        self.variable_counter = 0
    
    def reduce(self, term: Term, max_steps: int = 100) -> Dict[str, Any]:
        """Esegue la riduzione beta completa."""
        
        self.reduction_steps = []
        self.variable_counter = 0
        
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
                    logger.warning("Detected potential infinite loop, stopping")
                    break
        
        # Analyze final result
        is_normal_form = self._find_redex(current_term) is None
        
        return {
            "original_term": str(term),
            "final_term": str(current_term),
            "is_normal_form": is_normal_form,
            "steps_taken": step_count,
            "max_steps_reached": step_count >= max_steps,
            "strategy": self.strategy.value,
            "reduction_steps": self.reduction_steps,
            "analysis": self._analyze_result(current_term)
        }
    
    def _find_redex(self, term: Term) -> Optional[Dict[str, Any]]:
        """Trova il prossimo redex secondo la strategia."""
        
        if self.strategy == ReductionStrategy.NORMAL_ORDER:
            return self._find_leftmost_outermost_redex(term)
        elif self.strategy == ReductionStrategy.APPLICATIVE_ORDER:
            return self._find_leftmost_innermost_redex(term)
        else:
            # Default to normal order
            return self._find_leftmost_outermost_redex(term)
    
    def _find_leftmost_outermost_redex(self, term: Term, path: List[str] = None) -> Optional[Dict[str, Any]]:
        """Trova il redex leftmost outermost."""
        if path is None:
            path = []
        
        if isinstance(term, Application):
            # Check if this application is a redex
            if isinstance(term.function, Lambda):
                return {
                    "type": "beta_redex",
                    "path": path,
                    "function": term.function,
                    "argument": term.argument,
                    "parameter": term.function.parameter,
                    "body": term.function.body
                }
            
            # Otherwise, search in function first (leftmost)
            func_redex = self._find_leftmost_outermost_redex(term.function, path + ["function"])
            if func_redex:
                return func_redex
            
            # Then search in argument
            return self._find_leftmost_outermost_redex(term.argument, path + ["argument"])
        
        elif isinstance(term, Lambda):
            # Search in body
            return self._find_leftmost_outermost_redex(term.body, path + ["body"])
        
        # Variable has no redexes
        return None
    
    def _find_leftmost_innermost_redex(self, term: Term, path: List[str] = None) -> Optional[Dict[str, Any]]:
        """Trova il redex leftmost innermost."""
        if path is None:
            path = []
        
        if isinstance(term, Application):
            # First search in subterms (innermost)
            func_redex = self._find_leftmost_innermost_redex(term.function, path + ["function"])
            if func_redex:
                return func_redex
            
            arg_redex = self._find_leftmost_innermost_redex(term.argument, path + ["argument"])
            if arg_redex:
                return arg_redex
            
            # Then check if this application is a redex
            if isinstance(term.function, Lambda):
                return {
                    "type": "beta_redex",
                    "path": path,
                    "function": term.function,
                    "argument": term.argument,
                    "parameter": term.function.parameter,
                    "body": term.function.body
                }
        
        elif isinstance(term, Lambda):
            # Search in body
            return self._find_leftmost_innermost_redex(term.body, path + ["body"])
        
        return None
    
    def _reduce_redex(self, term: Term, redex_info: Dict[str, Any]) -> Term:
        """Riduce un redex specifico nel termine."""
        
        path = redex_info["path"]
        
        if not path:
            # Redex is at the root
            return self._perform_beta_reduction(
                redex_info["function"],
                redex_info["argument"]
            )
        
        # Navigate to the redex and replace it
        return self._replace_at_path(term, path, lambda app: self._perform_beta_reduction(
            redex_info["function"],
            redex_info["argument"]
        ))
    
    def _perform_beta_reduction(self, lambda_term: Lambda, argument: Term) -> Term:
        """Esegue la riduzione beta: (λx.M) N → M[x := N]."""
        
        parameter = lambda_term.parameter
        body = lambda_term.body
        
        # Perform substitution with alpha conversion if necessary
        return self._substitute(body, parameter, argument)
    
    def _substitute(self, term: Term, var: Variable, replacement: Term) -> Term:
        """Sostituisce tutte le occorrenze libere di var in term con replacement."""
        
        if isinstance(term, Variable):
            if term == var:
                return replacement
            else:
                return term
        
        elif isinstance(term, Application):
            new_function = self._substitute(term.function, var, replacement)
            new_argument = self._substitute(term.argument, var, replacement)
            return Application(new_function, new_argument)
        
        elif isinstance(term, Lambda):
            if term.parameter == var:
                # Variable is bound, no substitution
                return term
            
            # Check for variable capture
            replacement_free_vars = self.free_variables(replacement)
            
            if term.parameter.name in [v.name for v in replacement_free_vars]:
                # Need alpha conversion to avoid capture
                new_param = self._generate_fresh_variable(
                    self.free_variables(term.body) | replacement_free_vars | {var}
                )
                
                # Rename bound variable in body
                alpha_converted_body = self._substitute(term.body, term.parameter, new_param)
                
                # Now perform the original substitution
                new_body = self._substitute(alpha_converted_body, var, replacement)
                
                return Lambda(new_param, new_body)
            else:
                # No capture, proceed normally
                new_body = self._substitute(term.body, var, replacement)
                return Lambda(term.parameter, new_body)
    
    def _generate_fresh_variable(self, avoid: Set[Variable]) -> Variable:
        """Genera una variabile fresca che non è in avoid."""
        
        avoid_names = {v.name for v in avoid}
        
        # Try single letters first
        for char in "abcdefghijklmnopqrstuvwxyz":
            if char not in avoid_names:
                return Variable(char)
        
        # Use numbered variables
        counter = 0
        while True:
            name = f"x{counter}"
            if name not in avoid_names:
                return Variable(name)
            counter += 1
    
    def free_variables(self, term: Term) -> Set[Variable]:
        """Calcola le variabili libere in un termine."""
        
        if isinstance(term, Variable):
            return {term}
        
        elif isinstance(term, Application):
            return self.free_variables(term.function) | self.free_variables(term.argument)
        
        elif isinstance(term, Lambda):
            body_free = self.free_variables(term.body)
            return body_free - {term.parameter}
    
    def bound_variables(self, term: Term) -> Set[Variable]:
        """Calcola le variabili legate in un termine."""
        
        if isinstance(term, Variable):
            return set()
        
        elif isinstance(term, Application):
            return self.bound_variables(term.function) | self.bound_variables(term.argument)
        
        elif isinstance(term, Lambda):
            return {term.parameter} | self.bound_variables(term.body)
    
    def _replace_at_path(self, term: Term, path: List[str], replacer) -> Term:
        """Sostituisce un sottotermine al percorso specificato."""
        
        if not path:
            return replacer(term)
        
        direction = path[0]
        remaining_path = path[1:]
        
        if isinstance(term, Application):
            if direction == "function":
                new_function = self._replace_at_path(term.function, remaining_path, replacer)
                return Application(new_function, term.argument)
            elif direction == "argument":
                new_argument = self._replace_at_path(term.argument, remaining_path, replacer)
                return Application(term.function, new_argument)
        
        elif isinstance(term, Lambda):
            if direction == "body":
                new_body = self._replace_at_path(term.body, remaining_path, replacer)
                return Lambda(term.parameter, new_body)
        
        # Should not reach here with valid paths
        return term
    
    def _analyze_result(self, term: Term) -> Dict[str, Any]:
        """Analizza il risultato finale."""
        
        free_vars = self.free_variables(term)
        bound_vars = self.bound_variables(term)
        
        # Determine term type
        term_type = "unknown"
        if isinstance(term, Variable):
            term_type = "variable"
        elif isinstance(term, Lambda):
            if not free_vars:
                term_type = "closed_lambda" 
            else:
                term_type = "open_lambda"
        elif isinstance(term, Application):
            term_type = "application"
        
        # Count lambda abstractions
        lambda_count = self._count_lambdas(term)
        
        # Check for common combinators
        combinator = self._identify_combinator(term)
        
        return {
            "term_type": term_type,
            "free_variables": [v.name for v in free_vars],
            "bound_variables": [v.name for v in bound_vars],
            "lambda_count": lambda_count,
            "is_closed": len(free_vars) == 0,
            "combinator": combinator,
            "complexity": len(str(term))
        }
    
    def _count_lambdas(self, term: Term) -> int:
        """Conta il numero di astrazioni lambda."""
        
        if isinstance(term, Variable):
            return 0
        elif isinstance(term, Lambda):
            return 1 + self._count_lambdas(term.body)
        elif isinstance(term, Application):
            return self._count_lambdas(term.function) + self._count_lambdas(term.argument)
    
    def _identify_combinator(self, term: Term) -> Optional[str]:
        """Identifica combinatori comuni."""
        
        term_str = str(term).replace(' ', '')
        
        # Common combinators
        combinators = {
            "λx.x": "I (Identity)",
            "λx.λy.x": "K (Constant)", 
            "λx.λy.y": "KI (False)",
            "λx.λy.λz.xz(yz)": "S (Substitution)",
            "λf.λg.λx.f(gx)": "B (Composition)",
            "λf.(λx.f(xx))(λx.f(xx))": "Y (Fixed-point)",
            "λf.λx.f(fx)": "Church 2",
            "λf.λx.x": "Church 0",
            "λf.λx.fx": "Church 1"
        }
        
        for pattern, name in combinators.items():
            if self._terms_equivalent(term_str, pattern.replace(' ', '')):
                return name
        
        return None
    
    def _terms_equivalent(self, term1: str, term2: str) -> bool:
        """Verifica equivalenza sintattica semplice."""
        return term1 == term2


# Test and demonstration
def test_beta_reduction():
    """Testa il sistema di riduzione beta."""
    
    print("🧪 Testing Complete Beta Reduction System")
    print("=" * 60)
    
    parser = LambdaParser()
    reducer = BetaReducer(ReductionStrategy.NORMAL_ORDER)
    
    # Test cases
    test_cases = [
        # Simple identity application
        "(λx.x) y",
        
        # Constant function
        "(λx.λy.x) a b",
        
        # Function composition
        "(λf.λg.λx.f(gx)) (λy.y) (λz.z) w",
        
        # Church numeral arithmetic
        "(λn.λf.λx.f(nfx)) (λf.λx.fx)",
        
        # Y combinator (will not terminate, but we limit steps)
        "(λf.(λx.f(xx))(λx.f(xx))) (λg.λn.n)"
    ]
    
    for i, expression in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {expression}")
        print("-" * 40)
        
        try:
            # Parse
            term = parser.parse(expression)
            print(f"   Parsed: {term}")
            
            # Reduce
            result = reducer.reduce(term, max_steps=10)
            
            print(f"   Final: {result['final_term']}")
            print(f"   Steps: {result['steps_taken']}")
            print(f"   Normal form: {result['is_normal_form']}")
            
            if result['analysis']['combinator']:
                print(f"   Combinator: {result['analysis']['combinator']}")
            
            # Show first few reduction steps
            if len(result['reduction_steps']) > 1:
                print("   Reduction steps:")
                for step in result['reduction_steps'][:3]:
                    print(f"     {step['step']}: {step['term']}")
                if len(result['reduction_steps']) > 3:
                    print(f"     ... ({len(result['reduction_steps'])-3} more steps)")
            
        except Exception as e:
            print(f"   Error: {e}")
    
    print(f"\n🎉 Beta reduction tests completed!")


if __name__ == "__main__":
    test_beta_reduction()

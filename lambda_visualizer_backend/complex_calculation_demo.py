#!/usr/bin/env python3
"""
Complex Lambda Calculus Calculation Demo
Demonstrates advanced lambda calculus with Y-combinator and factorial
"""

import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.lambda_expression import LambdaExpression
from utils.complete_beta_reduction import BetaReducer, LambdaParser, ReductionStrategy
from utils.real_integrations import RealManimIntegration, RealVideoOutput
from utils.persistence_system import JobManager, JobStatus, JobPriority, PersistenceManager

class ComplexLambdaDemo:
    """Demo per calcoli lambda calculus complessi"""
    
    def __init__(self):
        # Initialize components
        self.lambda_parser = LambdaParser()
        self.beta_reducer = BetaReducer(ReductionStrategy.NORMAL_ORDER)
        self.manim_integration = RealManimIntegration("./manim_output")
        self.video_output = RealVideoOutput("./video_output")
        
        # Initialize persistence
        self.persistence_manager = PersistenceManager("./enhanced_lambda_visualizer.db")
        self.job_manager = JobManager(self.persistence_manager)
        
        print("Complex Lambda Calculus Demo initialized")
    
    def create_complex_expressions(self) -> Dict[str, str]:
        """Crea espressioni lambda complesse per la demo"""
        
        expressions = {
            # Y-combinator (fixed-point combinator)
            "y_combinator": "λf.(λx.f(x x))(λx.f(x x))",
            
            # Factorial function
            "factorial": "λn.if (n = 0) then 1 else n * (factorial (n-1))",
            
            # Y-combinator applied to factorial (recursive factorial)
            "y_factorial": "(λf.(λx.f(x x))(λx.f(x x))) (λf.λn.if (n = 0) then 1 else n * (f (n-1)))",
            
            # Church numerals
            "zero": "λf.λx.x",
            "one": "λf.λx.f x",
            "two": "λf.λx.f(f x)",
            "three": "λf.λx.f(f(f x))",
            
            # Successor function
            "successor": "λn.λf.λx.f(n f x)",
            
            # Addition
            "addition": "λm.λn.λf.λx.m f (n f x)",
            
            # Multiplication
            "multiplication": "λm.λn.λf.m(n f)",
            
            # Power function
            "power": "λm.λn.n m",
            
            # Complex nested application
            "complex_nested": "((λf.λg.λx.f(g x)) (λx.x*x)) ((λy.λz.y+z) 3) 4",
            
            # Self-application (leads to infinite reduction)
            "self_application": "(λx.x x) (λx.x x)",
            
            # Omega combinator
            "omega": "λx.x x",
            
            # Church boolean true
            "true": "λx.λy.x",
            
            # Church boolean false  
            "false": "λx.λy.y",
            
            # Church conditional
            "if_then_else": "λp.λa.λb.p a b",
            
            # Pair constructor
            "pair": "λx.λy.λf.f x y",
            
            # First projection
            "first": "λp.p (λx.λy.x)",
            
            # Second projection
            "second": "λp.p (λx.λy.y)",
            
            # Complex calculation: factorial of 3 using Y-combinator
            "factorial_3": "((λf.(λx.f(x x))(λx.f(x x))) (λf.λn.if (n = 0) then 1 else n * (f (n-1)))) 3",
            
            # List operations
            "cons": "λx.λy.λf.f x y",
            "car": "λl.l (λx.λy.x)",
            "cdr": "λl.l (λx.λy.y)",
            "nil": "λx.λy.y",
            
            # Map function
            "map": "λf.λl.λg.l (λx.λy.g (f x) (map f y))",
            
            # Fold function
            "fold": "λf.λz.λl.l (λx.λy.f x (fold f z y)) z",
            
            # Complex list operation: map successor over [1,2,3]
            "map_successor": "((λf.λl.λg.l (λx.λy.g (f x) (map f y)) nil) (λn.λf.λx.f(n f x))) (cons (λf.λx.f x) (cons (λf.λx.f(f x)) (cons (λf.λx.f(f(f x))) nil)))"
        }
        
        return expressions
    
    def analyze_expression(self, expression: str, name: str) -> Dict[str, Any]:
        """Analizza un'espressione lambda complessa"""
        print(f"\nAnalyzing: {name}")
        print(f"Expression: {expression}")
        
        try:
            # Parse the expression
            term = self.lambda_parser.parse(expression)
            print(f"Parsed successfully")
            
            # Get structural analysis
            analysis = {
                "name": name,
                "expression": expression,
                "parsed": str(term),
                "complexity": self._calculate_complexity(term),
                "variables": self._extract_variables(term),
                "depth": self._calculate_depth(term),
                "applications": self._count_applications(term),
                "abstractions": self._count_abstractions(term)
            }
            
            # Try beta reduction (with limit to avoid infinite loops)
            try:
                reduction_result = self.beta_reducer.reduce(term, max_steps=50)
                analysis["reduction_steps"] = len(reduction_result.steps)
                analysis["final_form"] = str(reduction_result.final_term)
                analysis["reduction_complete"] = reduction_result.is_complete
                analysis["reduction_steps_detail"] = [str(step) for step in reduction_result.steps[:10]]  # First 10 steps
                
                print(f"Reduction: {len(reduction_result.steps)} steps")
                print(f"Final form: {str(reduction_result.final_term)[:100]}...")
                
            except Exception as e:
                analysis["reduction_error"] = str(e)
                print(f"Reduction failed: {e}")
            
            return analysis
            
        except Exception as e:
            print(f"Analysis failed: {e}")
            return {
                "name": name,
                "expression": expression,
                "error": str(e)
            }
    
    def _calculate_complexity(self, term) -> int:
        """Calcola la complessità di un termine"""
        if hasattr(term, 'complexity'):
            return term.complexity
        return len(str(term))
    
    def _extract_variables(self, term) -> List[str]:
        """Estrae le variabili da un termine"""
        variables = set()
        if hasattr(term, 'variables'):
            variables.update(term.variables)
        return list(variables)
    
    def _calculate_depth(self, term) -> int:
        """Calcola la profondità di un termine"""
        if hasattr(term, 'depth'):
            return term.depth
        return 1
    
    def _count_applications(self, term) -> int:
        """Conta le applicazioni in un termine"""
        if hasattr(term, 'applications'):
            return term.applications
        return str(term).count('(')
    
    def _count_abstractions(self, term) -> int:
        """Conta le astrazioni in un termine"""
        if hasattr(term, 'abstractions'):
            return term.abstractions
        return str(term).count('λ')
    
    def create_animation_frames(self, expression: str, name: str, duration: float = 10.0) -> Dict[str, Any]:
        """Crea frame di animazione per un'espressione complessa"""
        print(f"\nCreating animation for: {name}")
        
        try:
            # Parse expression
            term = self.lambda_parser.parse(expression)
            
            # Perform reduction to get steps
            reduction_result = self.beta_reducer.reduce(term, max_steps=100)
            
            # Create frames
            frames = []
            total_frames = int(duration * 30)  # 30 FPS
            steps = reduction_result.steps
            
            for frame_num in range(total_frames):
                progress = frame_num / (total_frames - 1)
                
                # Determine which step to show
                step_index = min(int(progress * len(steps)), len(steps) - 1)
                current_step = steps[step_index] if steps else term
                
                frame = {
                    "frame_number": frame_num,
                    "timestamp": frame_num / 30.0,
                    "content": {
                        "expression": str(current_step),
                        "progress": progress,
                        "analysis": f"Step {step_index + 1}/{len(steps)} - {name}",
                        "step_index": step_index,
                        "total_steps": len(steps),
                        "reduction_progress": step_index / max(len(steps) - 1, 1)
                    }
                }
                frames.append(frame)
            
            # Add metadata
            animation_data = {
                "frames": frames,
                "metadata": {
                    "total_frames": total_frames,
                    "duration": duration,
                    "fps": 30,
                    "expression_name": name,
                    "original_expression": expression,
                    "total_reduction_steps": len(steps),
                    "created_at": datetime.now().isoformat(),
                    "animation_id": str(uuid.uuid4())
                }
            }
            
            print(f"Created {total_frames} frames for {len(steps)} reduction steps")
            return animation_data
            
        except Exception as e:
            print(f"Animation creation failed: {e}")
            return {"error": str(e)}
    
    def save_animation_data(self, animation_data: Dict[str, Any], filename: str):
        """Salva i dati di animazione in un file JSON"""
        filepath = f"./video_output/{filename}"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(animation_data, f, indent=2, ensure_ascii=False)
        
        print(f"Animation data saved: {filepath}")
        return filepath
    
    def run_complex_demo(self):
        """Esegue la demo completa con calcoli complessi"""
        print("Starting Complex Lambda Calculus Demo")
        print("=" * 60)
        
        # Get complex expressions
        expressions = self.create_complex_expressions()
        
        # Select interesting expressions for demo
        demo_expressions = [
            "y_combinator",
            "factorial_3", 
            "complex_nested",
            "map_successor",
            "power"
        ]
        
        results = {}
        
        for expr_name in demo_expressions:
            if expr_name in expressions:
                print(f"\n{'='*20} {expr_name.upper()} {'='*20}")
                
                # Analyze expression
                analysis = self.analyze_expression(expressions[expr_name], expr_name)
                results[expr_name] = analysis
                
                # Create animation
                animation_data = self.create_animation_frames(
                    expressions[expr_name], 
                    expr_name, 
                    duration=8.0
                )
                
                if "error" not in animation_data:
                    # Save animation data
                    filename = f"complex_{expr_name}_{uuid.uuid4().hex[:8]}_frames.json"
                    self.save_animation_data(animation_data, filename)
                    
                    # Add to results
                    results[expr_name]["animation_file"] = filename
        
        # Save summary
        summary = {
            "demo_results": results,
            "total_expressions": len(demo_expressions),
            "successful_animations": len([r for r in results.values() if "animation_file" in r]),
            "created_at": datetime.now().isoformat()
        }
        
        with open("./video_output/complex_demo_summary.json", 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\nDemo completed!")
        print(f"Processed {len(demo_expressions)} expressions")
        print(f"Created {summary['successful_animations']} animations")
        print(f"Results saved in ./video_output/")
        
        return summary

def main():
    """Main function to run the complex demo"""
    demo = ComplexLambdaDemo()
    results = demo.run_complex_demo()
    
    print("\n" + "="*60)
    print("DEMO SUMMARY")
    print("="*60)
    
    for name, result in results["demo_results"].items():
        if "error" not in result:
            print(f"\n{name.upper()}:")
            print(f"   Expression: {result['expression'][:50]}...")
            print(f"   Complexity: {result.get('complexity', 'N/A')}")
            print(f"   Variables: {', '.join(result.get('variables', []))}")
            if 'reduction_steps' in result:
                print(f"   Reduction Steps: {result['reduction_steps']}")
            if 'animation_file' in result:
                print(f"   Animation: {result['animation_file']}")
        else:
            print(f"\nERROR {name.upper()}: {result['error']}")

if __name__ == "__main__":
    main()

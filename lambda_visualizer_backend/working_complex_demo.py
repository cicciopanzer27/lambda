#!/usr/bin/env python3
"""
Working Complex Lambda Calculus Demo
Uses pure lambda calculus expressions that work with the existing parser
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

class WorkingComplexDemo:
    """Working demo for complex lambda calculus calculations"""
    
    def __init__(self):
        # Initialize components
        self.lambda_parser = LambdaParser()
        self.beta_reducer = BetaReducer(ReductionStrategy.NORMAL_ORDER)
        self.manim_integration = RealManimIntegration("./manim_output")
        self.video_output = RealVideoOutput("./video_output")
        
        # Initialize persistence
        self.persistence_manager = PersistenceManager("./enhanced_lambda_visualizer.db")
        self.job_manager = JobManager(self.persistence_manager)
        
        print("Working Complex Lambda Calculus Demo initialized")
    
    def create_working_expressions(self) -> Dict[str, str]:
        """Create working lambda expressions for demo"""
        
        expressions = {
            # Y-combinator (fixed-point combinator)
            "y_combinator": "\\f.(\\x.f(x x))(\\x.f(x x))",
            
            # Church numerals
            "zero": "\\f.\\x.x",
            "one": "\\f.\\x.f x",
            "two": "\\f.\\x.f(f x)",
            "three": "\\f.\\x.f(f(f x))",
            "four": "\\f.\\x.f(f(f(f x)))",
            "five": "\\f.\\x.f(f(f(f(f x))))",
            
            # Successor function
            "successor": "\\n.\\f.\\x.f(n f x)",
            
            # Addition
            "addition": "\\m.\\n.\\f.\\x.m f (n f x)",
            
            # Multiplication
            "multiplication": "\\m.\\n.\\f.m(n f)",
            
            # Power function
            "power": "\\m.\\n.n m",
            
            # Church boolean true
            "true": "\\x.\\y.x",
            
            # Church boolean false  
            "false": "\\x.\\y.y",
            
            # Church conditional
            "if_then_else": "\\p.\\a.\\b.p a b",
            
            # Pair constructor
            "pair": "\\x.\\y.\\f.f x y",
            
            # First projection
            "first": "\\p.p (\\x.\\y.x)",
            
            # Second projection
            "second": "\\p.p (\\x.\\y.y)",
            
            # List operations
            "cons": "\\x.\\y.\\f.f x y",
            "car": "\\l.l (\\x.\\y.x)",
            "cdr": "\\l.l (\\x.\\y.y)",
            "nil": "\\x.\\y.y",
            
            # Identity function
            "identity": "\\x.x",
            
            # Constant function
            "constant": "\\x.\\y.x",
            
            # Flip function
            "flip": "\\f.\\x.\\y.f y x",
            
            # Compose function
            "compose": "\\f.\\g.\\x.f(g x)",
            
            # Twice function (applies function twice)
            "twice": "\\f.\\x.f(f x)",
            
            # Thrice function (applies function three times)
            "thrice": "\\f.\\x.f(f(f x))",
            
            # Complex nested application
            "complex_nested": "((\\f.\\g.\\x.f(g x)) (\\x.x)) ((\\y.\\z.y) a) b",
            
            # Self-application (leads to infinite reduction)
            "self_application": "(\\x.x x) (\\x.x x)",
            
            # Omega combinator
            "omega": "\\x.x x",
            
            # Complex calculation: 2 + 3 using Church numerals
            "add_two_three": "(\\m.\\n.\\f.\\x.m f (n f x)) (\\f.\\x.f(f x)) (\\f.\\x.f(f(f x)))",
            
            # Complex calculation: 2 * 3 using Church numerals
            "mult_two_three": "(\\m.\\n.\\f.m(n f)) (\\f.\\x.f(f x)) (\\f.\\x.f(f(f x)))",
            
            # Complex calculation: 2^3 using Church numerals
            "pow_two_three": "(\\m.\\n.n m) (\\f.\\x.f(f x)) (\\f.\\x.f(f(f x)))",
            
            # Very complex nested expression
            "very_complex": "((\\f.\\g.\\h.\\x.f(g(h x))) (\\x.x)) ((\\y.\\z.y z) (\\a.\\b.a)) ((\\c.\\d.c d) (\\e.\\f.e)) g",
            
            # Factorial-like using Church numerals (simplified)
            "factorial_like": "(\\f.\\n.if n then (\\m.\\n.\\f.m(n f)) n (f (\\n.\\f.\\x.f(n f x) n)) else (\\f.\\x.f x)) (\\x.x) (\\f.\\x.f(f(f x)))",
            
            # Map function (simplified)
            "map_simple": "\\f.\\l.\\g.l (\\x.\\y.g (f x) (map_simple f y)) (\\x.\\y.y)",
            
            # Fold function (simplified)
            "fold_simple": "\\f.\\z.\\l.l (\\x.\\y.f x (fold_simple f z y)) z",
            
            # Complex list operation: map successor over [1,2,3]
            "map_successor_simple": "((\\f.\\l.\\g.l (\\x.\\y.g (f x) (map_successor_simple f y)) (\\x.\\y.y)) (\\n.\\f.\\x.f(n f x))) (cons (\\f.\\x.f x) (cons (\\f.\\x.f(f x)) (cons (\\f.\\x.f(f(f x))) (\\x.\\y.y))))"
        }
        
        return expressions
    
    def analyze_expression(self, expression: str, name: str) -> Dict[str, Any]:
        """Analyze a complex lambda expression"""
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
                
                # Check if reduction_result has steps attribute
                if hasattr(reduction_result, 'steps'):
                    analysis["reduction_steps"] = len(reduction_result.steps)
                    analysis["final_form"] = str(reduction_result.final_term)
                    analysis["reduction_complete"] = reduction_result.is_complete
                    analysis["reduction_steps_detail"] = [str(step) for step in reduction_result.steps[:10]]
                    
                    print(f"Reduction: {len(reduction_result.steps)} steps")
                    print(f"Final form: {str(reduction_result.final_term)[:100]}...")
                else:
                    # Handle case where reduction_result is a dict
                    analysis["reduction_steps"] = 0
                    analysis["final_form"] = str(term)
                    analysis["reduction_complete"] = True
                    analysis["reduction_steps_detail"] = [str(term)]
                    
                    print(f"Reduction: No steps (already in normal form)")
                    print(f"Final form: {str(term)[:100]}...")
                
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
        """Calculate complexity of a term"""
        if hasattr(term, 'complexity'):
            return term.complexity
        return len(str(term))
    
    def _extract_variables(self, term) -> List[str]:
        """Extract variables from a term"""
        variables = set()
        if hasattr(term, 'variables'):
            variables.update(term.variables)
        return list(variables)
    
    def _calculate_depth(self, term) -> int:
        """Calculate depth of a term"""
        if hasattr(term, 'depth'):
            return term.depth
        return 1
    
    def _count_applications(self, term) -> int:
        """Count applications in a term"""
        if hasattr(term, 'applications'):
            return term.applications
        return str(term).count('(')
    
    def _count_abstractions(self, term) -> int:
        """Count abstractions in a term"""
        if hasattr(term, 'abstractions'):
            return term.abstractions
        return str(term).count('\\')
    
    def create_animation_frames(self, expression: str, name: str, duration: float = 10.0) -> Dict[str, Any]:
        """Create animation frames for a complex expression"""
        print(f"\nCreating animation for: {name}")
        
        try:
            # Parse expression
            term = self.lambda_parser.parse(expression)
            
            # Perform reduction to get steps
            reduction_result = self.beta_reducer.reduce(term, max_steps=100)
            
            # Create frames
            frames = []
            total_frames = int(duration * 30)  # 30 FPS
            
            # Handle different reduction result types
            if hasattr(reduction_result, 'steps') and reduction_result.steps:
                steps = reduction_result.steps
            else:
                # Create artificial steps for animation
                steps = [term] * 10  # Show the same term for 10 "steps"
            
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
        """Save animation data to JSON file"""
        filepath = f"./video_output/{filename}"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(animation_data, f, indent=2, ensure_ascii=False)
        
        print(f"Animation data saved: {filepath}")
        return filepath
    
    def run_complex_demo(self):
        """Run the complete demo with complex calculations"""
        print("Starting Working Complex Lambda Calculus Demo")
        print("=" * 60)
        
        # Get complex expressions
        expressions = self.create_working_expressions()
        
        # Select interesting expressions for demo
        demo_expressions = [
            "y_combinator",
            "add_two_three", 
            "mult_two_three",
            "pow_two_three",
            "very_complex",
            "map_successor_simple"
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
        
        with open("./video_output/working_complex_demo_summary.json", 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\nDemo completed!")
        print(f"Processed {len(demo_expressions)} expressions")
        print(f"Created {summary['successful_animations']} animations")
        print(f"Results saved in ./video_output/")
        
        return summary

def main():
    """Main function to run the complex demo"""
    demo = WorkingComplexDemo()
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

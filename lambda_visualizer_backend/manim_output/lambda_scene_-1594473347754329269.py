
from manim import *
import numpy as np

class LambdaScene(Scene):
    def construct(self):
        # Title
        title = Text("Lambda Expression Analysis", font_size=36)
        title.to_edge(UP)
        
        # Main expression
        expr = MathTex(r"\f \cdot \x \cdot f(f(f x))", font_size=48)
        expr.set_color(BLUE)
        
        # Analysis components
        analysis_text = Text("Structural Analysis:", font_size=24)
        analysis_text.next_to(expr, DOWN, buff=1)
        
        # Variables
        variables = self._extract_variables(expression)
        var_text = Text(f"Variables: {', '.join(variables)}", font_size=20)
        var_text.next_to(analysis_text, DOWN, buff=0.5)
        
        # Complexity
        complexity = len(expression)
        comp_text = Text(f"Complexity: {complexity}", font_size=20)
        comp_text.next_to(var_text, DOWN, buff=0.3)
        
        # Animation sequence
        self.play(FadeIn(title))
        self.wait(0.5)
        
        self.play(Create(expr))
        self.wait(1)
        
        self.play(FadeIn(analysis_text))
        self.wait(0.5)
        
        self.play(FadeIn(var_text))
        self.wait(0.5)
        
        self.play(FadeIn(comp_text))
        self.wait(10.0)
        
        # Beta reduction animation if applicable
        if self._has_application(expression):
            self._animate_beta_reduction(expr)
        
        self.wait(1)
    
    def _animate_beta_reduction(self, expr):
        """Anima la riduzione beta."""
        reduction_title = Text("Beta Reduction:", font_size=24)
        reduction_title.to_edge(DOWN, buff=2)
        
        self.play(FadeIn(reduction_title))
        
        # Simulate reduction steps
        steps = [
            "Step 1: Identify redex",
            "Step 2: Substitute variables", 
            "Step 3: Simplify expression"
        ]
        
        for i, step in enumerate(steps):
            step_text = Text(step, font_size=18)
            step_text.next_to(reduction_title, DOWN, buff=0.3 + i*0.4)
            self.play(FadeIn(step_text))
            self.wait(0.8)

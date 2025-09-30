#!/usr/bin/env python3
"""
Advanced Complex Lambda Calculus Visualizer
Specialized visualizer for complex lambda expressions with advanced features
"""

import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, Arrow
import numpy as np
from typing import Dict, List, Any
import argparse
import os
import re
from datetime import datetime

class AdvancedComplexVisualizer:
    def __init__(self, json_file_path: str):
        """Initialize the advanced visualizer with complex frame data"""
        self.json_file_path = json_file_path
        self.frames_data = self.load_frames_data()
        self.current_frame = 0
        
    def load_frames_data(self) -> Dict[str, Any]:
        """Load frame data from JSON file"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"Loaded {len(data['frames'])} frames from {self.json_file_path}")
            return data
        except Exception as e:
            print(f"Error loading JSON file: {e}")
            return {}
    
    def get_frame_data(self, frame_number: int) -> Dict[str, Any]:
        """Get data for a specific frame"""
        if frame_number < len(self.frames_data.get('frames', [])):
            return self.frames_data['frames'][frame_number]
        return {}
    
    def parse_lambda_expression(self, expression: str) -> Dict[str, Any]:
        """Parse lambda expression into components for visualization"""
        # Extract abstractions (\\x. ...)
        abstractions = re.findall(r'\\[a-zA-Z]+\.', expression)
        
        # Extract applications (parentheses)
        applications = expression.count('(')
        
        # Extract variables
        variables = set(re.findall(r'\\[a-zA-Z]+', expression))
        
        # Calculate nesting depth
        depth = 0
        max_depth = 0
        for char in expression:
            if char == '(':
                depth += 1
                max_depth = max(max_depth, depth)
            elif char == ')':
                depth -= 1
        
        return {
            'abstractions': abstractions,
            'applications': applications,
            'variables': list(variables),
            'nesting_depth': max_depth,
            'complexity': len(expression),
            'structure': self._analyze_structure(expression)
        }
    
    def _analyze_structure(self, expression: str) -> Dict[str, Any]:
        """Analyze the structural components of the expression"""
        # Count different types of constructs
        lambda_count = expression.count('\\')
        paren_count = expression.count('(')
        dot_count = expression.count('.')
        
        # Identify main components
        components = []
        if '\\' in expression:
            components.append('abstraction')
        if '(' in expression:
            components.append('application')
        if '.' in expression:
            components.append('binding')
        
        return {
            'lambda_count': lambda_count,
            'paren_count': paren_count,
            'dot_count': dot_count,
            'components': components
        }
    
    def create_advanced_plots(self):
        """Create advanced plots for complex lambda expressions"""
        frames = self.frames_data.get('frames', [])
        if not frames:
            print("No frame data available")
            return
        
        # Extract data for plotting
        frame_numbers = [frame['frame_number'] for frame in frames]
        timestamps = [frame['timestamp'] for frame in frames]
        progress_values = [frame['content']['progress'] for frame in frames]
        expressions = [frame['content']['expression'] for frame in frames]
        
        # Parse expressions for analysis
        parsed_expressions = [self.parse_lambda_expression(expr) for expr in expressions]
        
        # Create advanced subplots
        fig = plt.figure(figsize=(20, 15))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # Main title
        fig.suptitle('Advanced Lambda Calculus Complex Expression Analysis', fontsize=20, fontweight='bold')
        
        # Plot 1: Expression Complexity Over Time
        ax1 = fig.add_subplot(gs[0, 0])
        complexities = [p['complexity'] for p in parsed_expressions]
        ax1.plot(timestamps, complexities, 'b-', linewidth=2, alpha=0.7)
        ax1.set_xlabel('Time (seconds)')
        ax1.set_ylabel('Expression Complexity')
        ax1.set_title('Expression Complexity Over Time')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Nesting Depth Analysis
        ax2 = fig.add_subplot(gs[0, 1])
        depths = [p['nesting_depth'] for p in parsed_expressions]
        ax2.plot(timestamps, depths, 'g-', linewidth=2, alpha=0.7)
        ax2.set_xlabel('Time (seconds)')
        ax2.set_ylabel('Nesting Depth')
        ax2.set_title('Nesting Depth Over Time')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Abstraction vs Application Ratio
        ax3 = fig.add_subplot(gs[0, 2])
        abs_counts = [p['structure']['lambda_count'] for p in parsed_expressions]
        app_counts = [p['structure']['paren_count'] for p in parsed_expressions]
        ratios = [a/max(app, 1) for a, app in zip(abs_counts, app_counts)]
        ax3.plot(timestamps, ratios, 'r-', linewidth=2, alpha=0.7)
        ax3.set_xlabel('Time (seconds)')
        ax3.set_ylabel('Abstraction/Application Ratio')
        ax3.set_title('Abstraction vs Application Ratio')
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Variable Usage Distribution
        ax4 = fig.add_subplot(gs[1, 0])
        var_counts = [len(p['variables']) for p in parsed_expressions]
        ax4.hist(var_counts, bins=20, alpha=0.7, color='orange', edgecolor='black')
        ax4.set_xlabel('Number of Variables')
        ax4.set_ylabel('Frequency')
        ax4.set_title('Variable Usage Distribution')
        ax4.grid(True, alpha=0.3)
        
        # Plot 5: 3D Complexity Surface
        ax5 = fig.add_subplot(gs[1, 1], projection='3d')
        X = np.array(timestamps)
        Y = np.array(complexities)
        Z = np.array(depths)
        ax5.plot_surface(X.reshape(-1, 1), Y.reshape(-1, 1), Z.reshape(-1, 1), 
                        alpha=0.6, cmap='viridis')
        ax5.set_xlabel('Time')
        ax5.set_ylabel('Complexity')
        ax5.set_zlabel('Depth')
        ax5.set_title('3D Complexity Surface')
        
        # Plot 6: Expression Evolution Heatmap
        ax6 = fig.add_subplot(gs[1, 2])
        # Create a heatmap of expression characteristics
        heatmap_data = np.array([
            complexities,
            depths,
            abs_counts,
            app_counts
        ])
        im = ax6.imshow(heatmap_data, aspect='auto', cmap='YlOrRd')
        ax6.set_xlabel('Frame Number')
        ax6.set_ylabel('Characteristic')
        ax6.set_yticks([0, 1, 2, 3])
        ax6.set_yticklabels(['Complexity', 'Depth', 'Abstractions', 'Applications'])
        ax6.set_title('Expression Characteristics Heatmap')
        plt.colorbar(im, ax=ax6)
        
        # Plot 7: Progress vs Complexity Scatter
        ax7 = fig.add_subplot(gs[2, 0])
        scatter = ax7.scatter(progress_values, complexities, c=depths, 
                            cmap='plasma', s=50, alpha=0.7)
        ax7.set_xlabel('Progress (0-1)')
        ax7.set_ylabel('Expression Complexity')
        ax7.set_title('Progress vs Complexity (colored by depth)')
        plt.colorbar(scatter, ax=ax7, label='Nesting Depth')
        
        # Plot 8: Expression Length Distribution
        ax8 = fig.add_subplot(gs[2, 1])
        lengths = [len(expr) for expr in expressions]
        ax8.hist(lengths, bins=30, alpha=0.7, color='purple', edgecolor='black')
        ax8.set_xlabel('Expression Length')
        ax8.set_ylabel('Frequency')
        ax8.set_title('Expression Length Distribution')
        ax8.grid(True, alpha=0.3)
        
        # Plot 9: Real-time Expression Analysis
        ax9 = fig.add_subplot(gs[2, 2])
        # Show the current expression with highlighting
        current_expr = expressions[-1] if expressions else "No expression"
        ax9.text(0.1, 0.5, f"Current Expression:\n{current_expr[:100]}...", 
                fontsize=10, verticalalignment='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))
        ax9.set_xlim(0, 1)
        ax9.set_ylim(0, 1)
        ax9.axis('off')
        ax9.set_title('Current Expression')
        
        return fig
    
    def create_lambda_tree_visualization(self, frame_number: int = 0):
        """Create an advanced tree visualization of the lambda expression"""
        frame_data = self.get_frame_data(frame_number)
        if not frame_data:
            return None
        
        expression = frame_data['content']['expression']
        progress = frame_data['content']['progress']
        
        fig, ax = plt.subplots(1, 1, figsize=(16, 12))
        ax.set_xlim(0, 20)
        ax.set_ylim(0, 15)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Title
        ax.text(10, 14, 'Advanced Lambda Expression Tree Visualization', 
                ha='center', va='center', fontsize=18, fontweight='bold')
        ax.text(10, 13.5, f'Frame {frame_number} | Progress: {progress:.3f}', 
                ha='center', va='center', fontsize=14, color='gray')
        
        # Parse and visualize the lambda expression
        parsed = self.parse_lambda_expression(expression)
        
        # Draw the main structure
        y_pos = 12
        
        # Draw abstractions
        for i, abstraction in enumerate(parsed['abstractions']):
            x_pos = 2 + i * 3
            self._draw_abstraction_node(ax, x_pos, y_pos, abstraction, 'blue', progress)
        
        # Draw applications
        for i in range(parsed['applications']):
            x_pos = 5 + i * 2
            self._draw_application_node(ax, x_pos, y_pos - 2, f'App {i+1}', 'red', progress)
        
        # Draw variables
        for i, variable in enumerate(parsed['variables']):
            x_pos = 8 + i * 2
            self._draw_variable_node(ax, x_pos, y_pos - 4, variable, 'green', progress)
        
        # Add expression text
        ax.text(10, 8, f'Expression: {expression}', 
                ha='center', va='center', fontsize=12, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))
        
        # Add analysis
        analysis_text = f"""
        Analysis:
        • Complexity: {parsed['complexity']}
        • Nesting Depth: {parsed['nesting_depth']}
        • Abstractions: {len(parsed['abstractions'])}
        • Applications: {parsed['applications']}
        • Variables: {len(parsed['variables'])}
        """
        ax.text(10, 6, analysis_text, ha='center', va='center', fontsize=10, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.7))
        
        # Add progress bar
        self._draw_advanced_progress_bar(ax, 10, 4, progress, parsed)
        
        # Add complexity indicator
        self._draw_complexity_indicator(ax, 10, 2, parsed['complexity'])
        
        return fig
    
    def _draw_abstraction_node(self, ax, x, y, abstraction, color, progress):
        """Draw an abstraction node"""
        # Lambda symbol
        circle = Circle((x, y), 0.3, fill=False, color=color, linewidth=3)
        ax.add_patch(circle)
        
        # Variable text
        ax.text(x, y, abstraction[1], ha='center', va='center', fontsize=12, 
                color=color, fontweight='bold')
        
        # Highlight based on progress
        if progress > 0.5:
            highlight = Circle((x, y), 0.4, fill=False, color=color, 
                             linewidth=2, alpha=progress)
            ax.add_patch(highlight)
    
    def _draw_application_node(self, ax, x, y, label, color, progress):
        """Draw an application node"""
        # Application symbol
        rect = Rectangle((x-0.3, y-0.2), 0.6, 0.4, fill=False, color=color, linewidth=2)
        ax.add_patch(rect)
        
        # Label
        ax.text(x, y, label, ha='center', va='center', fontsize=10, 
                color=color, fontweight='bold')
        
        # Highlight based on progress
        if progress > 0.3:
            highlight = Rectangle((x-0.4, y-0.3), 0.8, 0.6, fill=False, color=color, 
                                linewidth=1, alpha=progress)
            ax.add_patch(highlight)
    
    def _draw_variable_node(self, ax, x, y, variable, color, progress):
        """Draw a variable node"""
        # Variable circle
        circle = Circle((x, y), 0.2, fill=True, color=color, alpha=0.7)
        ax.add_patch(circle)
        
        # Variable text
        ax.text(x, y, variable[1:], ha='center', va='center', fontsize=10, 
                color='white', fontweight='bold')
        
        # Pulse effect
        if progress > 0.7:
            pulse = Circle((x, y), 0.3, fill=False, color=color, 
                          linewidth=2, alpha=progress)
            ax.add_patch(pulse)
    
    def _draw_advanced_progress_bar(self, ax, x, y, progress, parsed):
        """Draw an advanced progress bar with multiple indicators"""
        # Background
        bg_rect = Rectangle((x-4, y-0.3), 8, 0.6, facecolor='lightgray', alpha=0.5)
        ax.add_patch(bg_rect)
        
        # Progress fill
        progress_rect = Rectangle((x-4, y-0.3), 8 * progress, 0.6, 
                                 facecolor='green', alpha=0.7)
        ax.add_patch(progress_rect)
        
        # Complexity indicator
        complexity_progress = min(parsed['complexity'] / 200, 1.0)
        complexity_rect = Rectangle((x-4, y-0.1), 8 * complexity_progress, 0.2, 
                                   facecolor='blue', alpha=0.7)
        ax.add_patch(complexity_rect)
        
        # Text
        ax.text(x, y, f'{progress:.1%}', ha='center', va='center', 
                fontsize=12, fontweight='bold')
        ax.text(x, y-0.5, f'Complexity: {parsed["complexity"]}', 
                ha='center', va='center', fontsize=10)
    
    def _draw_complexity_indicator(self, ax, x, y, complexity):
        """Draw a complexity indicator"""
        # Complexity meter
        max_complexity = 200
        complexity_ratio = min(complexity / max_complexity, 1.0)
        
        # Background
        bg_rect = Rectangle((x-2, y-0.2), 4, 0.4, facecolor='lightgray', alpha=0.5)
        ax.add_patch(bg_rect)
        
        # Complexity fill
        color = 'green' if complexity_ratio < 0.5 else 'orange' if complexity_ratio < 0.8 else 'red'
        complexity_rect = Rectangle((x-2, y-0.2), 4 * complexity_ratio, 0.4, 
                                   facecolor=color, alpha=0.7)
        ax.add_patch(complexity_rect)
        
        # Text
        ax.text(x, y, f'Complexity: {complexity}', ha='center', va='center', 
                fontsize=10, fontweight='bold')
    
    def create_interactive_html(self, output_file: str = "advanced_complex_visualization.html"):
        """Create an advanced interactive HTML visualization"""
        frames = self.frames_data.get('frames', [])
        if not frames:
            print("No frame data available")
            return
        
        # Get metadata
        metadata = self.frames_data.get('metadata', {})
        expression_name = metadata.get('expression_name', 'Complex Expression')
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Complex Lambda Calculus Visualizer</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(45deg, #2196F3, #21CBF3);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .controls {{
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }}
        .main-content {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 20px;
        }}
        .expression-panel {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
        }}
        .analysis-panel {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
        }}
        .lambda-expression {{
            font-family: 'Courier New', monospace;
            font-size: 18px;
            background: #e3f2fd;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 5px solid #2196F3;
            word-break: break-all;
        }}
        .progress-container {{
            margin: 20px 0;
        }}
        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #e0e0e0;
            border-radius: 15px;
            overflow: hidden;
            position: relative;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #8BC34A);
            transition: width 0.3s ease;
            border-radius: 15px;
        }}
        .progress-text {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-weight: bold;
            color: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }}
        .frame-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .info-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #2196F3;
            text-align: center;
        }}
        .info-card h3 {{
            margin: 0 0 10px 0;
            color: #2196F3;
            font-size: 14px;
        }}
        .info-card p {{
            margin: 0;
            font-size: 16px;
            font-weight: bold;
        }}
        .controls input[type="range"] {{
            width: 100%;
            margin: 10px 0;
        }}
        .btn {{
            background: #2196F3;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
            font-size: 14px;
        }}
        .btn:hover {{
            background: #1976D2;
        }}
        .btn:disabled {{
            background: #ccc;
            cursor: not-allowed;
        }}
        .complexity-meter {{
            margin: 20px 0;
        }}
        .complexity-bar {{
            width: 100%;
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            position: relative;
        }}
        .complexity-fill {{
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #FF9800, #F44336);
            transition: width 0.3s ease;
            border-radius: 10px;
        }}
        .complexity-text {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-weight: bold;
            color: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }}
        .tree-visualization {{
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.6;
            text-align: left;
            background: white;
            padding: 20px;
            border-radius: 8px;
            border: 2px solid #e0e0e0;
            margin: 20px 0;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            text-align: center;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #2196F3;
        }}
        .stat-label {{
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Advanced Complex Lambda Calculus Visualizer</h1>
            <p>Interactive visualization of complex lambda expression: {expression_name}</p>
        </div>
        
        <div class="controls">
            <h3>Advanced Controls</h3>
            <input type="range" id="frameSlider" min="0" max="{len(frames)-1}" value="0" step="1">
            <div>
                <button class="btn" id="playBtn">▶️ Play</button>
                <button class="btn" id="pauseBtn" disabled>⏸️ Pause</button>
                <button class="btn" id="resetBtn">🔄 Reset</button>
                <button class="btn" id="exportBtn">💾 Export Frame</button>
                <button class="btn" id="analyzeBtn">🔍 Analyze</button>
            </div>
        </div>
        
        <div class="main-content">
            <div class="expression-panel">
                <h3>Expression Analysis</h3>
                <div class="lambda-expression" id="expressionDisplay">
                    {frames[0]['content']['expression']}
                </div>
                
                <div class="progress-container">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill" style="width: 0%"></div>
                        <div class="progress-text" id="progressText">0%</div>
                    </div>
                </div>
                
                <div class="complexity-meter">
                    <h4>Complexity Meter</h4>
                    <div class="complexity-bar">
                        <div class="complexity-fill" id="complexityFill" style="width: 0%"></div>
                        <div class="complexity-text" id="complexityText">0</div>
                    </div>
                </div>
                
                <div class="frame-info">
                    <div class="info-card">
                        <h3>Frame Number</h3>
                        <p id="frameNumber">0</p>
                    </div>
                    <div class="info-card">
                        <h3>Timestamp</h3>
                        <p id="timestamp">0.000s</p>
                    </div>
                    <div class="info-card">
                        <h3>Progress</h3>
                        <p id="progress">0.000</p>
                    </div>
                    <div class="info-card">
                        <h3>Step</h3>
                        <p id="stepInfo">1/1</p>
                    </div>
                </div>
            </div>
            
            <div class="analysis-panel">
                <h3>Advanced Analysis</h3>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value" id="complexityValue">0</div>
                        <div class="stat-label">Complexity</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="depthValue">0</div>
                        <div class="stat-label">Nesting Depth</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="abstractionsValue">0</div>
                        <div class="stat-label">Abstractions</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="applicationsValue">0</div>
                        <div class="stat-label">Applications</div>
                    </div>
                </div>
                
                <div class="tree-visualization" id="treeVisualization">
                    <pre>
Loading tree visualization...
                    </pre>
                </div>
            </div>
        </div>
    </div>

    <script>
        const frames = {json.dumps(frames)};
        let currentFrame = 0;
        let isPlaying = false;
        let animationId = null;
        
        const frameSlider = document.getElementById('frameSlider');
        const expressionDisplay = document.getElementById('expressionDisplay');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        const frameNumber = document.getElementById('frameNumber');
        const timestamp = document.getElementById('timestamp');
        const progress = document.getElementById('progress');
        const stepInfo = document.getElementById('stepInfo');
        
        const complexityFill = document.getElementById('complexityFill');
        const complexityText = document.getElementById('complexityText');
        const complexityValue = document.getElementById('complexityValue');
        const depthValue = document.getElementById('depthValue');
        const abstractionsValue = document.getElementById('abstractionsValue');
        const applicationsValue = document.getElementById('applicationsValue');
        const treeVisualization = document.getElementById('treeVisualization');
        
        const playBtn = document.getElementById('playBtn');
        const pauseBtn = document.getElementById('pauseBtn');
        const resetBtn = document.getElementById('resetBtn');
        const exportBtn = document.getElementById('exportBtn');
        const analyzeBtn = document.getElementById('analyzeBtn');
        
        function analyzeExpression(expression) {{
            // Simple analysis function
            const abstractions = (expression.match(/\\\\/g) || []).length;
            const applications = (expression.match(/\\(/g) || []).length;
            const variables = new Set(expression.match(/\\\\[a-zA-Z]+/g) || []).size;
            const complexity = expression.length;
            
            // Calculate nesting depth
            let depth = 0;
            let maxDepth = 0;
            for (let char of expression) {{
                if (char === '(') {{
                    depth++;
                    maxDepth = Math.max(maxDepth, depth);
                }} else if (char === ')') {{
                    depth--;
                }}
            }}
            
            return {{
                complexity,
                depth: maxDepth,
                abstractions,
                applications,
                variables
            }};
        }}
        
        function updateDisplay(frameIndex) {{
            const frame = frames[frameIndex];
            currentFrame = frameIndex;
            
            expressionDisplay.textContent = frame.content.expression;
            progressFill.style.width = (frame.content.progress * 100) + '%';
            progressText.textContent = (frame.content.progress * 100).toFixed(1) + '%';
            frameNumber.textContent = frame.frame_number;
            timestamp.textContent = frame.timestamp.toFixed(3) + 's';
            progress.textContent = frame.content.progress.toFixed(3);
            stepInfo.textContent = `${{frame.content.step_index + 1}}/${{frame.content.total_steps}}`;
            
            // Analyze expression
            const analysis = analyzeExpression(frame.content.expression);
            
            // Update complexity meter
            const complexityRatio = Math.min(analysis.complexity / 200, 1);
            complexityFill.style.width = (complexityRatio * 100) + '%';
            complexityText.textContent = analysis.complexity;
            
            // Update stats
            complexityValue.textContent = analysis.complexity;
            depthValue.textContent = analysis.depth;
            abstractionsValue.textContent = analysis.abstractions;
            applicationsValue.textContent = analysis.applications;
            
            // Update tree visualization
            const treeHtml = `
                <pre>
Expression Tree Analysis:
=======================

Complexity: ${{analysis.complexity}}
Nesting Depth: ${{analysis.depth}}
Abstractions: ${{analysis.abstractions}}
Applications: ${{analysis.applications}}
Variables: ${{analysis.variables}}

Expression Structure:
${{frame.content.expression}}

Progress: ${{(frame.content.progress * 100).toFixed(1)}}%
Frame: ${{frame.frame_number}}/${{frames.length - 1}}
Step: ${{frame.content.step_index + 1}}/${{frame.content.total_steps}}
                </pre>
            `;
            treeVisualization.innerHTML = treeHtml;
        }}
        
        function play() {{
            isPlaying = true;
            playBtn.disabled = true;
            pauseBtn.disabled = false;
            
            function animate() {{
                if (isPlaying) {{
                    currentFrame = (currentFrame + 1) % frames.length;
                    frameSlider.value = currentFrame;
                    updateDisplay(currentFrame);
                    animationId = setTimeout(animate, 50); // ~20 FPS
                }}
            }}
            animate();
        }}
        
        function pause() {{
            isPlaying = false;
            playBtn.disabled = false;
            pauseBtn.disabled = true;
            if (animationId) {{
                clearTimeout(animationId);
            }}
        }}
        
        function reset() {{
            pause();
            currentFrame = 0;
            frameSlider.value = 0;
            updateDisplay(0);
        }}
        
        function exportFrame() {{
            const frame = frames[currentFrame];
            const data = {{
                frame_number: frame.frame_number,
                timestamp: frame.timestamp,
                expression: frame.content.expression,
                progress: frame.content.progress,
                analysis: frame.content.analysis,
                step_index: frame.content.step_index,
                total_steps: frame.content.total_steps
            }};
            
            const blob = new Blob([JSON.stringify(data, null, 2)], {{type: 'application/json'}});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `complex_lambda_frame_${{frame.frame_number}}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }}
        
        function analyze() {{
            const frame = frames[currentFrame];
            const analysis = analyzeExpression(frame.content.expression);
            
            alert(`Expression Analysis:
Complexity: ${{analysis.complexity}}
Nesting Depth: ${{analysis.depth}}
Abstractions: ${{analysis.abstractions}}
Applications: ${{analysis.applications}}
Variables: ${{analysis.variables}}`);
        }}
        
        // Event listeners
        frameSlider.addEventListener('input', (e) => {{
            pause();
            updateDisplay(parseInt(e.target.value));
        }});
        
        playBtn.addEventListener('click', play);
        pauseBtn.addEventListener('click', pause);
        resetBtn.addEventListener('click', reset);
        exportBtn.addEventListener('click', exportFrame);
        analyzeBtn.addEventListener('click', analyze);
        
        // Initialize
        updateDisplay(0);
    </script>
</body>
</html>
        """
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Advanced interactive HTML visualization created: {output_file}")
        return output_file

def main():
    parser = argparse.ArgumentParser(description='Advanced Complex Lambda Calculus Visualizer')
    parser.add_argument('json_file', help='Path to the JSON frame data file')
    parser.add_argument('--output-dir', default='.', help='Output directory for generated files')
    parser.add_argument('--create-all', action='store_true', help='Create all visualization types')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.json_file):
        print(f"Error: File {args.json_file} not found")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize visualizer
    visualizer = AdvancedComplexVisualizer(args.json_file)
    
    if args.create_all:
        print("Creating all advanced visualizations...")
        
        # Advanced plots
        print("Creating advanced plots...")
        fig1 = visualizer.create_advanced_plots()
        if fig1:
            advanced_plot_path = os.path.join(args.output_dir, 'advanced_complex_analysis.png')
            fig1.savefig(advanced_plot_path, dpi=300, bbox_inches='tight')
            print(f"Advanced plots saved: {advanced_plot_path}")
        
        # Tree visualization
        print("Creating tree visualization...")
        fig2 = visualizer.create_lambda_tree_visualization(0)
        if fig2:
            tree_plot_path = os.path.join(args.output_dir, 'complex_lambda_tree.png')
            fig2.savefig(tree_plot_path, dpi=300, bbox_inches='tight')
            print(f"Tree visualization saved: {tree_plot_path}")
        
        # Interactive HTML
        print("Creating advanced interactive HTML...")
        html_path = os.path.join(args.output_dir, 'advanced_complex_visualization.html')
        visualizer.create_interactive_html(html_path)
        
        print(f"\nAll advanced visualizations created in: {args.output_dir}")
        print(f"Open {html_path} in your browser for interactive visualization")
    
    else:
        # Just create the interactive HTML by default
        html_path = os.path.join(args.output_dir, 'advanced_complex_visualization.html')
        visualizer.create_interactive_html(html_path)
        print(f"Advanced interactive visualization created: {html_path}")

if __name__ == "__main__":
    main()

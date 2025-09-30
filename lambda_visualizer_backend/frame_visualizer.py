#!/usr/bin/env python3
"""
Frame Data Visualizer for Lambda Calculus Animation
Visualizes the JSON frame data from the lambda visualizer backend
"""

import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
import numpy as np
from typing import Dict, List, Any
import argparse
import os

class LambdaFrameVisualizer:
    def __init__(self, json_file_path: str):
        """Initialize the visualizer with frame data from JSON file"""
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
    
    def create_static_plots(self):
        """Create static plots showing the progression data"""
        frames = self.frames_data.get('frames', [])
        if not frames:
            print("No frame data available")
            return
        
        # Extract data for plotting
        frame_numbers = [frame['frame_number'] for frame in frames]
        timestamps = [frame['timestamp'] for frame in frames]
        progress_values = [frame['content']['progress'] for frame in frames]
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Lambda Calculus Animation Frame Analysis', fontsize=16, fontweight='bold')
        
        # Plot 1: Progress over time
        ax1.plot(timestamps, progress_values, 'b-', linewidth=2, alpha=0.7)
        ax1.set_xlabel('Time (seconds)')
        ax1.set_ylabel('Progress (0.0 - 1.0)')
        ax1.set_title('Animation Progress Over Time')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 1)
        
        # Plot 2: Frame rate analysis
        if len(timestamps) > 1:
            frame_rates = [1.0 / (timestamps[i+1] - timestamps[i]) for i in range(len(timestamps)-1)]
            ax2.plot(frame_numbers[1:], frame_rates, 'g-', linewidth=2, alpha=0.7)
            ax2.set_xlabel('Frame Number')
            ax2.set_ylabel('Frame Rate (fps)')
            ax2.set_title('Frame Rate Over Time')
            ax2.grid(True, alpha=0.3)
        
        # Plot 3: Progress distribution
        ax3.hist(progress_values, bins=50, alpha=0.7, color='orange', edgecolor='black')
        ax3.set_xlabel('Progress Value')
        ax3.set_ylabel('Frequency')
        ax3.set_title('Progress Value Distribution')
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Timeline visualization
        ax4.scatter(timestamps, frame_numbers, c=progress_values, cmap='viridis', s=20, alpha=0.7)
        ax4.set_xlabel('Time (seconds)')
        ax4.set_ylabel('Frame Number')
        ax4.set_title('Frame Timeline (colored by progress)')
        cbar = plt.colorbar(ax4.collections[0], ax=ax4)
        cbar.set_label('Progress')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def create_lambda_expression_visualization(self, frame_number: int = 0):
        """Create a visual representation of the lambda expression"""
        frame_data = self.get_frame_data(frame_number)
        if not frame_data:
            return None
        
        expression = frame_data['content']['expression']
        progress = frame_data['content']['progress']
        
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 6)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Title
        ax.text(5, 5.5, f'Lambda Expression Visualization', 
                ha='center', va='center', fontsize=16, fontweight='bold')
        ax.text(5, 5, f'Frame {frame_number} | Progress: {progress:.3f}', 
                ha='center', va='center', fontsize=12, color='gray')
        
        # Parse and visualize the lambda expression: \f.\x.f(f(f x))
        # This is a complex lambda expression, let's break it down visually
        
        # Draw the main structure
        y_pos = 4
        
        # \f
        self._draw_lambda_symbol(ax, 1, y_pos, 'f', 'blue')
        
        # \x
        self._draw_lambda_symbol(ax, 2.5, y_pos, 'x', 'green')
        
        # f(f(f x))
        self._draw_function_application(ax, 4, y_pos, 'f', 'f(f(f x))', 'red', progress)
        
        # Add expression text
        ax.text(5, 2.5, f'Expression: {expression}', 
                ha='center', va='center', fontsize=14, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))
        
        # Add analysis
        analysis = frame_data['content']['analysis']
        ax.text(5, 2, f'Analysis: {analysis}', 
                ha='center', va='center', fontsize=12, color='darkblue')
        
        # Add progress bar
        self._draw_progress_bar(ax, 5, 1.5, progress)
        
        return fig
    
    def _draw_lambda_symbol(self, ax, x, y, variable, color):
        """Draw a lambda symbol with variable"""
        # Lambda symbol (simplified)
        lambda_x = [x, x+0.3, x+0.6]
        lambda_y = [y+0.2, y, y+0.2]
        ax.plot(lambda_x, lambda_y, color=color, linewidth=3)
        ax.text(x+0.8, y, f'.{variable}', fontsize=14, color=color, fontweight='bold')
    
    def _draw_function_application(self, ax, x, y, func_name, expression, color, progress):
        """Draw function application structure"""
        # Function name
        ax.text(x, y+0.3, func_name, ha='center', va='center', fontsize=14, 
                color=color, fontweight='bold', 
                bbox=dict(boxstyle="round,pad=0.2", facecolor=color, alpha=0.3))
        
        # Parentheses
        ax.plot([x-0.3, x-0.3], [y-0.3, y+0.3], color=color, linewidth=2)
        ax.plot([x+0.3, x+0.3], [y-0.3, y+0.3], color=color, linewidth=2)
        
        # Expression inside
        ax.text(x, y, expression, ha='center', va='center', fontsize=10, color=color)
        
        # Highlight based on progress
        if progress > 0.5:
            circle = Circle((x, y), 0.4, fill=False, color=color, linewidth=3, alpha=progress)
            ax.add_patch(circle)
    
    def _draw_progress_bar(self, ax, x, y, progress):
        """Draw a progress bar"""
        # Background
        bg_rect = Rectangle((x-2, y-0.2), 4, 0.4, facecolor='lightgray', alpha=0.5)
        ax.add_patch(bg_rect)
        
        # Progress fill
        progress_rect = Rectangle((x-2, y-0.2), 4 * progress, 0.4, facecolor='green', alpha=0.7)
        ax.add_patch(progress_rect)
        
        # Text
        ax.text(x, y, f'{progress:.1%}', ha='center', va='center', fontsize=12, fontweight='bold')
    
    def create_animation(self, output_file: str = None):
        """Create an animated visualization"""
        frames = self.frames_data.get('frames', [])
        if not frames:
            print("No frame data available for animation")
            return
        
        # Sample frames for animation (every 10th frame to keep it manageable)
        sample_frames = frames[::10]
        
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 6)
        ax.set_aspect('equal')
        ax.axis('off')
        
        def animate(frame_idx):
            ax.clear()
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 6)
            ax.set_aspect('equal')
            ax.axis('off')
            
            frame_data = sample_frames[frame_idx]
            expression = frame_data['content']['expression']
            progress = frame_data['content']['progress']
            frame_number = frame_data['frame_number']
            
            # Title
            ax.text(5, 5.5, f'Lambda Expression Animation', 
                    ha='center', va='center', fontsize=16, fontweight='bold')
            ax.text(5, 5, f'Frame {frame_number} | Progress: {progress:.3f}', 
                    ha='center', va='center', fontsize=12, color='gray')
            
            # Visualize the expression
            y_pos = 4
            self._draw_lambda_symbol(ax, 1, y_pos, 'f', 'blue')
            self._draw_lambda_symbol(ax, 2.5, y_pos, 'x', 'green')
            self._draw_function_application(ax, 4, y_pos, 'f', 'f(f(f x))', 'red', progress)
            
            # Expression text
            ax.text(5, 2.5, f'Expression: {expression}', 
                    ha='center', va='center', fontsize=14, 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))
            
            # Progress bar
            self._draw_progress_bar(ax, 5, 1.5, progress)
            
            # Add pulsing effect based on progress
            pulse_alpha = 0.3 + 0.7 * progress
            circle = Circle((5, 3.5), 1 + progress, fill=False, color='purple', 
                          linewidth=2, alpha=pulse_alpha)
            ax.add_patch(circle)
        
        anim = animation.FuncAnimation(fig, animate, frames=len(sample_frames), 
                                     interval=100, repeat=True)
        
        if output_file:
            anim.save(output_file, writer='pillow', fps=10)
            print(f"Animation saved to {output_file}")
        
        return anim
    
    def create_interactive_html(self, output_file: str = "lambda_visualization.html"):
        """Create an interactive HTML visualization"""
        frames = self.frames_data.get('frames', [])
        if not frames:
            print("No frame data available")
            return
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lambda Calculus Frame Visualizer</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .container {{
            max-width: 1200px;
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
        .frame-display {{
            padding: 30px;
            text-align: center;
        }}
        .lambda-expression {{
            font-family: 'Courier New', monospace;
            font-size: 24px;
            background: #e3f2fd;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 5px solid #2196F3;
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
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .info-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #2196F3;
        }}
        .info-card h3 {{
            margin: 0 0 10px 0;
            color: #2196F3;
        }}
        .info-card p {{
            margin: 0;
            font-size: 18px;
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
        .visualization {{
            margin: 20px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        .lambda-tree {{
            font-family: 'Courier New', monospace;
            font-size: 18px;
            line-height: 1.6;
            text-align: left;
            background: white;
            padding: 20px;
            border-radius: 8px;
            border: 2px solid #e0e0e0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧮 Lambda Calculus Frame Visualizer</h1>
            <p>Interactive visualization of lambda expression animation frames</p>
        </div>
        
        <div class="controls">
            <h3>Frame Controls</h3>
            <input type="range" id="frameSlider" min="0" max="{len(frames)-1}" value="0" step="1">
            <div>
                <button class="btn" id="playBtn">▶️ Play</button>
                <button class="btn" id="pauseBtn" disabled>⏸️ Pause</button>
                <button class="btn" id="resetBtn">🔄 Reset</button>
                <button class="btn" id="exportBtn">💾 Export Frame</button>
            </div>
        </div>
        
        <div class="frame-display">
            <div class="lambda-expression" id="expressionDisplay">
                {frames[0]['content']['expression']}
            </div>
            
            <div class="progress-container">
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill" style="width: 0%"></div>
                    <div class="progress-text" id="progressText">0%</div>
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
                    <h3>Analysis</h3>
                    <p id="analysis">Frame 1/600</p>
                </div>
            </div>
            
            <div class="visualization">
                <h3>Lambda Expression Tree</h3>
                <div class="lambda-tree" id="lambdaTree">
                    <pre>
λf.λx.f(f(f x))

Tree Structure:
    λf
    └── λx
        └── f
            └── f
                └── f
                    └── x
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
        const analysis = document.getElementById('analysis');
        const lambdaTree = document.getElementById('lambdaTree');
        
        const playBtn = document.getElementById('playBtn');
        const pauseBtn = document.getElementById('pauseBtn');
        const resetBtn = document.getElementById('resetBtn');
        const exportBtn = document.getElementById('exportBtn');
        
        function updateDisplay(frameIndex) {{
            const frame = frames[frameIndex];
            currentFrame = frameIndex;
            
            expressionDisplay.textContent = frame.content.expression;
            progressFill.style.width = (frame.content.progress * 100) + '%';
            progressText.textContent = (frame.content.progress * 100).toFixed(1) + '%';
            frameNumber.textContent = frame.frame_number;
            timestamp.textContent = frame.timestamp.toFixed(3) + 's';
            analysis.textContent = frame.content.analysis;
            
            // Update lambda tree visualization
            const treeHtml = `
                <pre>
λf.λx.f(f(f x))

Tree Structure:
    λf
    └── λx
        └── f
            └── f
                └── f
                    └── x

Progress: ` + (frame.content.progress * 100).toFixed(1) + `%
Frame: ` + frame.frame_number + `/` + (frames.length - 1) + `
                </pre>
            `;
            lambdaTree.innerHTML = treeHtml;
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
                analysis: frame.content.analysis
            }};
            
            const blob = new Blob([JSON.stringify(data, null, 2)], {{type: 'application/json'}});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `lambda_frame_${{frame.frame_number}}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
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
        
        // Initialize
        updateDisplay(0);
    </script>
</body>
</html>
        """
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Interactive HTML visualization created: {output_file}")
        return output_file

def main():
    parser = argparse.ArgumentParser(description='Visualize lambda calculus frame data')
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
    visualizer = LambdaFrameVisualizer(args.json_file)
    
    if args.create_all:
        print("Creating all visualizations...")
        
        # Static plots
        print("Creating static plots...")
        fig1 = visualizer.create_static_plots()
        if fig1:
            static_plot_path = os.path.join(args.output_dir, 'lambda_frame_analysis.png')
            fig1.savefig(static_plot_path, dpi=300, bbox_inches='tight')
            print(f"Static plots saved: {static_plot_path}")
        
        # Expression visualization
        print("Creating expression visualization...")
        fig2 = visualizer.create_lambda_expression_visualization(0)
        if fig2:
            expr_plot_path = os.path.join(args.output_dir, 'lambda_expression_viz.png')
            fig2.savefig(expr_plot_path, dpi=300, bbox_inches='tight')
            print(f"Expression visualization saved: {expr_plot_path}")
        
        # Animation
        print("Creating animation...")
        anim_path = os.path.join(args.output_dir, 'lambda_animation.gif')
        visualizer.create_animation(anim_path)
        
        # Interactive HTML
        print("Creating interactive HTML...")
        html_path = os.path.join(args.output_dir, 'lambda_visualization.html')
        visualizer.create_interactive_html(html_path)
        
        print(f"\nAll visualizations created in: {args.output_dir}")
        print(f"Open {html_path} in your browser for interactive visualization")
    
    else:
        # Just create the interactive HTML by default
        html_path = os.path.join(args.output_dir, 'lambda_visualization.html')
        visualizer.create_interactive_html(html_path)
        print(f"Interactive visualization created: {html_path}")

if __name__ == "__main__":
    main()

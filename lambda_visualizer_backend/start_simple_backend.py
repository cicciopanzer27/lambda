#!/usr/bin/env python3
"""
Simple Backend Starter for Lambda Visualizer
Simplified version that works with the existing system
"""

import os
import sys
import logging
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import json
import uuid

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from models.lambda_expression import LambdaExpression
from utils.complete_beta_reduction import BetaReducer, LambdaParser, ReductionStrategy
from utils.real_integrations import RealManimIntegration, RealVideoOutput

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize components
lambda_parser = LambdaParser()
beta_reducer = BetaReducer(ReductionStrategy.NORMAL_ORDER)
manim_integration = RealManimIntegration("./manim_output")
video_output = RealVideoOutput("./video_output")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0-simple',
        'services': {
            'lambda_parser': True,
            'beta_reducer': True,
            'manim': manim_integration.manim_available,
            'video_output': True
        }
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_expression():
    """Analyze a lambda expression"""
    try:
        data = request.get_json()
        expression = data.get('expression', '')
        
        if not expression:
            return jsonify({'error': 'No expression provided'}), 400
        
        logger.info(f"Analyzing expression: {expression}")
        
        # Parse expression
        term = lambda_parser.parse(expression)
        
        # Get basic analysis
        analysis = {
            'expression': expression,
            'parsed': str(term),
            'complexity': len(expression),
            'variables': list(set(expression.split('\\')[1:]) if '\\' in expression else []),
            'abstractions': expression.count('\\'),
            'applications': expression.count('('),
            'timestamp': datetime.now().isoformat()
        }
        
        # Try beta reduction
        try:
            reduction_result = beta_reducer.reduce(term, max_steps=50)
            if hasattr(reduction_result, 'steps'):
                analysis['reduction_steps'] = len(reduction_result.steps)
                analysis['final_form'] = str(reduction_result.final_term)
                analysis['reduction_complete'] = reduction_result.is_complete
            else:
                analysis['reduction_steps'] = 0
                analysis['final_form'] = str(term)
                analysis['reduction_complete'] = True
        except Exception as e:
            analysis['reduction_error'] = str(e)
            analysis['reduction_steps'] = 0
            analysis['final_form'] = str(term)
            analysis['reduction_complete'] = False
        
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"Error analyzing expression: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/visualize', methods=['POST'])
def create_visualization():
    """Create visualization for a lambda expression"""
    try:
        data = request.get_json()
        expression = data.get('expression', '')
        duration = data.get('duration', 5.0)
        
        if not expression:
            return jsonify({'error': 'No expression provided'}), 400
        
        logger.info(f"Creating visualization for: {expression}")
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Parse expression
        term = lambda_parser.parse(expression)
        
        # Create animation frames
        frames = []
        total_frames = int(duration * 30)  # 30 FPS
        
        # Try to get reduction steps
        try:
            reduction_result = beta_reducer.reduce(term, max_steps=100)
            if hasattr(reduction_result, 'steps') and reduction_result.steps:
                steps = reduction_result.steps
            else:
                steps = [term] * 10
        except:
            steps = [term] * 10
        
        for frame_num in range(total_frames):
            progress = frame_num / (total_frames - 1)
            step_index = min(int(progress * len(steps)), len(steps) - 1)
            current_step = steps[step_index] if steps else term
            
            frame = {
                "frame_number": frame_num,
                "timestamp": frame_num / 30.0,
                "content": {
                    "expression": str(current_step),
                    "progress": progress,
                    "analysis": f"Step {step_index + 1}/{len(steps)} - {expression[:30]}...",
                    "step_index": step_index,
                    "total_steps": len(steps),
                    "reduction_progress": step_index / max(len(steps) - 1, 1)
                }
            }
            frames.append(frame)
        
        # Save animation data
        animation_data = {
            "frames": frames,
            "metadata": {
                "total_frames": total_frames,
                "duration": duration,
                "fps": 30,
                "expression_name": "Custom Expression",
                "original_expression": expression,
                "total_reduction_steps": len(steps),
                "created_at": datetime.now().isoformat(),
                "animation_id": job_id
            }
        }
        
        # Save to file
        filename = f"custom_expression_{job_id[:8]}_frames.json"
        filepath = f"./video_output/{filename}"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(animation_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'job_id': job_id,
            'status': 'completed',
            'animation_file': filename,
            'total_frames': total_frames,
            'duration': duration,
            'message': 'Visualization created successfully'
        })
        
    except Exception as e:
        logger.error(f"Error creating visualization: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/expressions/complex', methods=['GET'])
def get_complex_expressions():
    """Get predefined complex expressions"""
    expressions = {
        "y_combinator": {
            "name": "Y-Combinator",
            "expression": "\\f.(\\x.f(x x))(\\x.f(x x))",
            "description": "Fixed-point combinator for recursion",
            "complexity": 20,
            "type": "combinator"
        },
        "church_addition": {
            "name": "Church Addition (2+3)",
            "expression": "(\\m.\\n.\\f.\\x.m f (n f x)) (\\f.\\x.f(f x)) (\\f.\\x.f(f(f x)))",
            "description": "Addition of Church numerals 2 + 3",
            "complexity": 50,
            "type": "arithmetic"
        },
        "church_multiplication": {
            "name": "Church Multiplication (2*3)",
            "expression": "(\\m.\\n.\\f.m(n f)) (\\f.\\x.f(f x)) (\\f.\\x.f(f(f x)))",
            "description": "Multiplication of Church numerals 2 * 3",
            "complexity": 45,
            "type": "arithmetic"
        },
        "church_power": {
            "name": "Church Power (2^3)",
            "expression": "(\\m.\\n.n m) (\\f.\\x.f(f x)) (\\f.\\x.f(f(f x)))",
            "description": "Power operation 2^3 using Church numerals",
            "complexity": 40,
            "type": "arithmetic"
        },
        "very_complex": {
            "name": "Very Complex",
            "expression": "((\\f.\\g.\\h.\\x.f(g(h x))) (\\x.x)) ((\\y.\\z.y z) (\\a.\\b.a)) ((\\c.\\d.c d) (\\e.\\f.e)) g",
            "description": "Highly nested function composition",
            "complexity": 77,
            "type": "composition"
        },
        "map_successor": {
            "name": "Map Successor",
            "expression": "((\\f.\\l.\\g.l (\\x.\\y.g (f x) (map_successor_simple f y)) (\\x.\\y.y)) (\\n.\\f.\\x.f(n f x))) (cons (\\f.\\x.f x) (cons (\\f.\\x.f(f x)) (cons (\\f.\\x.f(f(f x))) (\\x.\\y.y))))",
            "description": "Map successor function over a list",
            "complexity": 157,
            "type": "list_operation"
        }
    }
    
    return jsonify(expressions)

@app.route('/api/files', methods=['GET'])
def list_animation_files():
    """List available animation files"""
    try:
        video_dir = "./video_output"
        if not os.path.exists(video_dir):
            return jsonify([])
        
        files = []
        for filename in os.listdir(video_dir):
            if filename.endswith('_frames.json'):
                filepath = os.path.join(video_dir, filename)
                stat = os.stat(filepath)
                files.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        return jsonify(files)
        
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/<filename>', methods=['GET'])
def get_animation_file(filename):
    """Get animation file content"""
    try:
        filepath = f"./video_output/{filename}"
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify(data)
        
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Simple Lambda Visualizer Backend")
    print("=" * 50)
    print("Available endpoints:")
    print("  GET  /health                    - Health check")
    print("  POST /api/analyze               - Analyze lambda expression")
    print("  POST /api/visualize             - Create visualization")
    print("  GET  /api/expressions/complex   - Get complex expressions")
    print("  GET  /api/files                 - List animation files")
    print("  GET  /api/files/<filename>      - Get animation file")
    print("=" * 50)
    print("Starting server on http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

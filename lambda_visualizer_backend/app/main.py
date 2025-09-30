"""
Applicazione Flask principale per il Lambda Visualizer Backend.
"""

import os
import logging
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from typing import Dict, Any

# Import dei moduli locali
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from models.lambda_expression import LambdaExpression
from utils.ollama_service import OllamaService
from utils.visualization_service import VisualizationService, VisualizationConfig
from utils.correct_lambda_parser import CorrectBetaReducer as BetaReducer, CorrectLambdaParser as LambdaParser, ReductionStrategy
from app.business_api import business_bp


# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inizializzazione Flask
app = Flask(__name__)
CORS(app)  # Abilita CORS per tutte le route

# Registra blueprint per API business
app.register_blueprint(business_bp)

# Configurazione
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
upload_folder = os.path.join(parent_dir, 'static', 'videos')
os.makedirs(upload_folder, exist_ok=True)
app.config['UPLOAD_FOLDER'] = upload_folder

# Inizializzazione servizi
ollama_service = OllamaService()
visualization_service = VisualizationService()
lambda_parser = LambdaParser()
beta_reducer = BetaReducer(ReductionStrategy.NORMAL_ORDER)


@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint per il controllo dello stato dell'applicazione."""
    return jsonify({
        'status': 'healthy',
        'services': {
            'ollama': ollama_service.is_available(),
            'visualization': True
        }
    })


@app.route('/api/models', methods=['GET'])
def get_available_models():
    """Ottiene la lista dei modelli Ollama disponibili."""
    try:
        models = ollama_service.get_available_models()
        return jsonify({
            'success': True,
            'models': models
        })
    except Exception as e:
        logger.error(f"Errore nel recupero modelli: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_lambda_expression():
    """Analizza un'espressione lambda con beta reduction completa."""
    try:
        data = request.get_json()
        
        if not data or 'expression' not in data:
            return jsonify({
                'success': False,
                'error': 'Espressione lambda richiesta'
            }), 400
        
        expression = data['expression'].strip()
        
        if not expression:
            return jsonify({
                'success': False,
                'error': 'Espressione lambda non può essere vuota'
            }), 400
        
        # Parse con il nuovo parser complesso
        logger.info(f"Parsing expression: {expression}")
        term = lambda_parser.parse(expression)
        logger.info(f"Parsed successfully: {term}")
        
        # Esegue beta reduction completa
        max_steps = data.get('max_steps', 100)
        strategy = data.get('strategy', 'normal_order')
        
        # Cambia strategia se richiesto
        if strategy != 'normal_order':
            beta_reducer.strategy = ReductionStrategy(strategy)
        
        logger.info(f"Performing beta reduction (max_steps={max_steps}, strategy={strategy})")
        reduction_result = beta_reducer.reduce(term, max_steps=max_steps)
        logger.info(f"Reduction complete: {reduction_result['steps']} steps taken")
        
        # Crea anche la vecchia struttura per compatibilità
        lambda_expr = LambdaExpression(expression)
        
        # Analizza con Ollama se disponibile
        ollama_analysis = None
        if ollama_service.is_available():
            ollama_response = ollama_service.analyze_lambda_expression(expression)
            if ollama_response.success:
                ollama_analysis = ollama_response.data
        
        # Prepara risposta completa
        response_data = {
            'success': True,
            'expression': expression,
            'parsed_term': str(term),
            'beta_reduction': {
                'original_term': reduction_result['original_term'],
                'final_term': reduction_result['final_term'],
                'is_normal_form': reduction_result['is_normal_form'],
                'steps_taken': reduction_result['steps'],
                'max_steps_reached': reduction_result['steps'] >= max_steps,
                'strategy': reduction_result['strategy'],
                'combinator': reduction_result.get('combinator'),
                'reduction_steps': reduction_result['reduction_steps']
            },
            'structure': lambda_expr.to_dict(),
            'metrics': lambda_expr.get_complexity_metrics(),
            'ollama_analysis': ollama_analysis
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Errore nell'analisi: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/visualize', methods=['POST'])
def create_visualization():
    """Crea una visualizzazione dell'espressione lambda."""
    try:
        data = request.get_json()
        
        if not data or 'expression' not in data:
            return jsonify({
                'success': False,
                'error': 'Espressione lambda richiesta'
            }), 400
        
        expression = data['expression'].strip()
        config_data = data.get('config', {})
        
        # Crea oggetto LambdaExpression
        lambda_expr = LambdaExpression(expression)
        lambda_data = lambda_expr.to_dict()
        
        # Configurazione visualizzazione
        config = VisualizationConfig(
            width=config_data.get('width', 800),
            height=config_data.get('height', 600),
            fps=config_data.get('fps', 30),
            duration=config_data.get('duration', 5.0),
            quality=config_data.get('quality', 'medium')
        )
        
        # Genera visualizzazione
        video_id = visualization_service.generate_lambda_diagram_video(lambda_data, config)
        
        if video_id:
            return jsonify({
                'success': True,
                'video_id': video_id,
                'expression': expression,
                'config': {
                    'width': config.width,
                    'height': config.height,
                    'fps': config.fps,
                    'duration': config.duration
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Errore nella generazione della visualizzazione'
            }), 500
            
    except Exception as e:
        logger.error(f"Errore nella visualizzazione: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/visualize/static', methods=['POST'])
def create_static_visualization():
    """Crea una visualizzazione statica dell'espressione lambda."""
    try:
        data = request.get_json()
        
        if not data or 'expression' not in data:
            return jsonify({
                'success': False,
                'error': 'Espressione lambda richiesta'
            }), 400
        
        expression = data['expression'].strip()
        
        # Crea oggetto LambdaExpression
        lambda_expr = LambdaExpression(expression)
        lambda_data = lambda_expr.to_dict()
        
        # Genera immagine statica
        image_id = visualization_service.generate_static_image(lambda_data)
        
        if image_id:
            return jsonify({
                'success': True,
                'image_id': image_id,
                'expression': expression
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Errore nella generazione dell\'immagine'
            }), 500
            
    except Exception as e:
        logger.error(f"Errore nella visualizzazione statica: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/video/<video_id>', methods=['GET'])
def get_video(video_id):
    """Serve un video generato."""
    try:
        video_info = visualization_service.get_video_info(video_id)
        
        if not video_info or not video_info['exists']:
            return jsonify({
                'success': False,
                'error': 'Video non trovato'
            }), 404
        
        return send_file(
            video_info['path'],
            mimetype='video/mp4',
            as_attachment=False
        )
        
    except Exception as e:
        logger.error(f"Errore nel servire video: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/image/<image_id>', methods=['GET'])
def get_image(image_id):
    """Serve un'immagine generata."""
    try:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{image_id}.png")
        
        if not os.path.exists(image_path):
            return jsonify({
                'success': False,
                'error': 'Immagine non trovata'
            }), 404
        
        return send_file(
            image_path,
            mimetype='image/png',
            as_attachment=False
        )
        
    except Exception as e:
        logger.error(f"Errore nel servire immagine: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/content', methods=['GET'])
def list_content():
    """Lista tutto il contenuto generato."""
    try:
        content = visualization_service.list_generated_content()
        return jsonify({
            'success': True,
            'content': content
        })
    except Exception as e:
        logger.error(f"Errore nel listing contenuto: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/cleanup', methods=['POST'])
def cleanup_old_content():
    """Pulisce il contenuto vecchio."""
    try:
        data = request.get_json() or {}
        max_age_hours = data.get('max_age_hours', 24)
        
        visualization_service.cleanup_old_videos(max_age_hours)
        
        return jsonify({
            'success': True,
            'message': f'Pulizia completata per contenuto più vecchio di {max_age_hours} ore'
        })
    except Exception as e:
        logger.error(f"Errore nella pulizia: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/examples', methods=['GET'])
def get_examples():
    """Restituisce esempi di espressioni lambda."""
    examples = [
        {
            'name': 'Identità',
            'expression': 'λx.x',
            'description': 'La funzione identità restituisce il suo argomento invariato'
        },
        {
            'name': 'Costante K',
            'expression': 'λx.λy.x',
            'description': 'La funzione costante restituisce sempre il primo argomento'
        },
        {
            'name': 'Falso',
            'expression': 'λx.λy.y',
            'description': 'Rappresentazione del valore booleano falso'
        },
        {
            'name': 'Combinatore S',
            'expression': 'λx.λy.λz.(x z)(y z)',
            'description': 'Il combinatore S per l\'applicazione distribuita'
        },
        {
            'name': 'Numerale 2',
            'expression': 'λf.λx.f(f x)',
            'description': 'Il numerale di Church per il numero 2'
        },
        {
            'name': 'Omega',
            'expression': '(λx.x x)(λx.x x)',
            'description': 'Il combinatore Omega che non termina'
        }
    ]
    
    return jsonify({
        'success': True,
        'examples': examples
    })


@app.errorhandler(404)
def not_found(error):
    """Handler per errori 404."""
    return jsonify({
        'success': False,
        'error': 'Endpoint non trovato'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handler per errori 500."""
    return jsonify({
        'success': False,
        'error': 'Errore interno del server'
    }), 500


if __name__ == '__main__':
    # Crea directory necessarie
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Avvia l'applicazione
    logger.info("Avvio Lambda Visualizer Backend...")
    logger.info(f"Ollama disponibile: {ollama_service.is_available()}")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

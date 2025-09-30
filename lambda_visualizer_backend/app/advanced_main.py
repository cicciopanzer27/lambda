"""
Applicazione Flask Avanzata per Lambda Visualizer
Integra il motore unificato con tutti i sottosistemi avanzati.
"""

import logging
import time
import uuid
from typing import Dict, Any
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys

# Aggiungi il path per importare i moduli engine
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from engine.unified_engine import unified_engine, RenderQuality, SceneType
from models.lambda_expression import LambdaExpression
from utils.ollama_service import OllamaService

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inizializza Flask
app = Flask(__name__)
CORS(app)

# Servizi
ollama_service = OllamaService()

# Directory per file generati
STATIC_DIR = os.path.join(os.path.dirname(__file__), '..', 'static')
VIDEOS_DIR = os.path.join(STATIC_DIR, 'videos')
IMAGES_DIR = os.path.join(STATIC_DIR, 'images')

# Crea directory se non esistono
os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint con informazioni dettagliate."""
    try:
        engine_metrics = unified_engine.get_system_metrics()
        
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "services": {
                "unified_engine": engine_metrics["state"] == "ready",
                "ollama": ollama_service.is_available(),
                "gpu_acceleration": engine_metrics["gpu_info"]["cuda_available"]
            },
            "engine_metrics": {
                "active_jobs": engine_metrics["active_jobs"],
                "queued_jobs": engine_metrics["queued_jobs"],
                "success_rate": engine_metrics["metrics"]["successful_renders"] / 
                               max(1, engine_metrics["metrics"]["total_jobs_processed"]),
                "gpu_device": engine_metrics["gpu_info"]["current_device"]
            }
        }
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"Errore nel health check: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_expression():
    """Analizza un'espressione lambda con tutti i sottosistemi."""
    try:
        data = request.get_json()
        expression = data.get('expression', '')
        
        if not expression:
            return jsonify({
                "success": False,
                "error": "Espressione lambda mancante"
            }), 400
        
        # Parse dell'espressione
        lambda_expr = LambdaExpression(expression)
        parsed_result = lambda_expr._parse_expression()
        
        if not parsed_result.get("success"):
            return jsonify({
                "success": False,
                "error": f"Errore nel parsing: {parsed_result.get('error', 'Sconosciuto')}"
            }), 400
        
        # Analisi strutturale
        structure = lambda_expr.to_dict()
        metrics = lambda_expr.get_complexity_metrics()
        
        # Analisi AI con Ollama (se disponibile)
        ollama_analysis = None
        if ollama_service.is_available():
            try:
                ollama_analysis = ollama_service.analyze_lambda_expression(expression)
            except Exception as e:
                logger.warning(f"Errore nell'analisi Ollama: {str(e)}")
        
        # Calcolo riduzioni beta (semplificato)
        reduction_steps = []
        if "λ" in expression and "(" in expression:
            # Simula passi di riduzione
            reduction_steps = [
                {
                    "step": 0,
                    "expression": expression,
                    "type": "initial",
                    "description": "Espressione iniziale"
                },
                {
                    "step": 1,
                    "expression": expression.replace("λx.", "").replace("(", "").replace(")", ""),
                    "type": "beta_reduction",
                    "description": "Riduzione beta applicata"
                }
            ]
        
        result = {
            "success": True,
            "expression": expression,
            "parsed": parsed_result,
            "structure": {
                "nodes": structure[0],
                "edges": structure[1]
            },
            "metrics": metrics,
            "reduction_steps": reduction_steps,
            "ollama_analysis": ollama_analysis,
            "analysis_timestamp": time.time()
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Errore nell'analisi: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/visualize/advanced', methods=['POST'])
def create_advanced_visualization():
    """Crea visualizzazioni avanzate usando il motore unificato."""
    try:
        data = request.get_json()
        expression = data.get('expression', '')
        
        if not expression:
            return jsonify({
                "success": False,
                "error": "Espressione lambda mancante"
            }), 400
        
        # Configurazione visualizzazione
        quality = RenderQuality(data.get('quality', 'standard'))
        scene_type = SceneType(data.get('scene_type', 'lambda_basic'))
        
        # Parametri personalizzati
        custom_params = {
            "style": data.get('style', 'modern'),
            "color_scheme": data.get('color_scheme', 'default'),
            "animation_speed": data.get('animation_speed', 1.0),
            "show_labels": data.get('show_labels', True),
            "highlight_reductions": data.get('highlight_reductions', True)
        }
        
        # Callback per progresso (semplificato)
        def progress_callback(job_id, progress):
            logger.info(f"Job {job_id} progresso: {progress:.1%}")
        
        # Sottometti job al motore unificato
        job_id = unified_engine.create_lambda_visualization(
            expression=expression,
            quality=quality,
            scene_type=scene_type,
            progress_callback=progress_callback,
            **custom_params
        )
        
        return jsonify({
            "success": True,
            "job_id": job_id,
            "message": "Visualizzazione avviata",
            "estimated_completion": time.time() + 30  # Stima 30 secondi
        })
        
    except Exception as e:
        logger.error(f"Errore nella visualizzazione avanzata: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/visualize/reduction', methods=['POST'])
def create_reduction_animation():
    """Crea animazioni di riduzione beta avanzate."""
    try:
        data = request.get_json()
        expression = data.get('expression', '')
        
        if not expression:
            return jsonify({
                "success": False,
                "error": "Espressione lambda mancante"
            }), 400
        
        # Analizza l'espressione per ottenere i passi di riduzione
        lambda_expr = LambdaExpression(expression)
        parsed_result = lambda_expr._parse_expression()
        
        if not parsed_result.get("success"):
            return jsonify({
                "success": False,
                "error": "Errore nel parsing dell'espressione"
            }), 400
        
        # Genera passi di riduzione (semplificato)
        reduction_steps = []
        current_expr = expression
        
        # Simula una sequenza di riduzioni
        for i in range(data.get('max_steps', 5)):
            step = {
                "step": i,
                "expression": current_expr,
                "type": "beta_reduction" if i > 0 else "initial",
                "redex_position": i * 2 if i > 0 else None,
                "description": f"Passo {i}" if i > 0 else "Espressione iniziale",
                "timestamp": i * data.get('step_duration', 2.0)
            }
            reduction_steps.append(step)
            
            # Simula una trasformazione
            if "λ" in current_expr and i < 2:
                current_expr = current_expr.replace("λx.", "λy.", 1)
        
        # Configurazione animazione
        quality = RenderQuality(data.get('quality', 'high'))
        animation_params = {
            "step_duration": data.get('step_duration', 2.0),
            "highlight_duration": data.get('highlight_duration', 0.5),
            "easing": data.get('easing', 'smooth'),
            "show_intermediate_steps": data.get('show_intermediate_steps', True)
        }
        
        # Sottometti job di animazione
        job_id = unified_engine.create_beta_reduction_animation(
            expression=expression,
            reduction_steps=reduction_steps,
            quality=quality,
            **animation_params
        )
        
        return jsonify({
            "success": True,
            "job_id": job_id,
            "reduction_steps": len(reduction_steps),
            "estimated_duration": len(reduction_steps) * animation_params["step_duration"],
            "message": "Animazione di riduzione avviata"
        })
        
    except Exception as e:
        logger.error(f"Errore nell'animazione di riduzione: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/visualize/interactive', methods=['POST'])
def create_interactive_exploration():
    """Crea visualizzazioni interattive esplorabili."""
    try:
        data = request.get_json()
        expression = data.get('expression', '')
        
        if not expression:
            return jsonify({
                "success": False,
                "error": "Espressione lambda mancante"
            }), 400
        
        # Configurazione interattività
        interaction_params = {
            "enable_hover": data.get('enable_hover', True),
            "enable_click": data.get('enable_click', True),
            "show_tooltips": data.get('show_tooltips', True),
            "highlight_connections": data.get('highlight_connections', True),
            "enable_drag": data.get('enable_drag', False),
            "show_reduction_preview": data.get('show_reduction_preview', True)
        }
        
        quality = RenderQuality(data.get('quality', 'high'))
        
        # Sottometti job interattivo
        job_id = unified_engine.create_interactive_exploration(
            expression=expression,
            quality=quality,
            **interaction_params
        )
        
        return jsonify({
            "success": True,
            "job_id": job_id,
            "message": "Esplorazione interattiva avviata",
            "features": list(interaction_params.keys())
        })
        
    except Exception as e:
        logger.error(f"Errore nell'esplorazione interattiva: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/jobs/<job_id>/status', methods=['GET'])
def get_job_status(job_id):
    """Ottiene lo status di un job di rendering."""
    try:
        status = unified_engine.get_job_status(job_id)
        
        if not status:
            return jsonify({
                "success": False,
                "error": "Job non trovato"
            }), 404
        
        return jsonify({
            "success": True,
            "job_status": status
        })
        
    except Exception as e:
        logger.error(f"Errore nel recupero status job: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/jobs/<job_id>/result', methods=['GET'])
def get_job_result(job_id):
    """Ottiene il risultato di un job completato."""
    try:
        status = unified_engine.get_job_status(job_id)
        
        if not status:
            return jsonify({
                "success": False,
                "error": "Job non trovato"
            }), 404
        
        if status.get("status") != "completed":
            return jsonify({
                "success": False,
                "error": f"Job non completato (status: {status.get('status')})"
            }), 400
        
        result = status.get("result", {})
        
        # Se il risultato contiene frame, salva come file
        if "frames" in result:
            output_file = self._save_render_result(job_id, result)
            result["output_file"] = output_file
        
        return jsonify({
            "success": True,
            "result": result
        })
        
    except Exception as e:
        logger.error(f"Errore nel recupero risultato job: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/jobs/<job_id>/cancel', methods=['POST'])
def cancel_job(job_id):
    """Cancella un job di rendering."""
    try:
        success = unified_engine.cancel_job(job_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Job {job_id} cancellato"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Job non può essere cancellato"
            }), 400
        
    except Exception as e:
        logger.error(f"Errore nella cancellazione job: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/system/metrics', methods=['GET'])
def get_system_metrics():
    """Ottiene le metriche del sistema."""
    try:
        metrics = unified_engine.get_system_metrics()
        return jsonify({
            "success": True,
            "metrics": metrics
        })
        
    except Exception as e:
        logger.error(f"Errore nel recupero metriche: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/examples/advanced', methods=['GET'])
def get_advanced_examples():
    """Ottiene esempi avanzati per il sistema."""
    examples = [
        {
            "name": "Identità",
            "expression": "λx.x",
            "description": "Funzione identità - restituisce l'argomento invariato",
            "complexity": "basic",
            "recommended_scene": "lambda_basic",
            "features": ["tromp_diagram", "basic_animation"]
        },
        {
            "name": "Composizione",
            "expression": "λf.λg.λx.f(g(x))",
            "description": "Combinatore di composizione di funzioni",
            "complexity": "intermediate",
            "recommended_scene": "lambda_reduction",
            "features": ["beta_reduction", "step_by_step"]
        },
        {
            "name": "Combinatore Y",
            "expression": "λf.(λx.f(x x))(λx.f(x x))",
            "description": "Combinatore di punto fisso per ricorsione",
            "complexity": "advanced",
            "recommended_scene": "lambda_graph",
            "features": ["3d_visualization", "interactive_exploration"]
        },
        {
            "name": "Numerale di Church 2",
            "expression": "λf.λx.f(f(x))",
            "description": "Rappresentazione del numero 2 in lambda calculus",
            "complexity": "intermediate",
            "recommended_scene": "lambda_reduction",
            "features": ["church_encoding", "animation"]
        },
        {
            "name": "Booleano True",
            "expression": "λx.λy.x",
            "description": "Rappresentazione del valore booleano True",
            "complexity": "basic",
            "recommended_scene": "lambda_basic",
            "features": ["boolean_logic", "simple_diagram"]
        }
    ]
    
    return jsonify({
        "success": True,
        "examples": examples,
        "total_examples": len(examples)
    })


def _save_render_result(job_id: str, result: Dict) -> str:
    """Salva il risultato del rendering su file."""
    try:
        # Determina il tipo di output
        if result.get("config", {}).get("fps", 0) > 1:
            # Video
            output_file = os.path.join(VIDEOS_DIR, f"{job_id}.json")
        else:
            # Immagine statica
            output_file = os.path.join(IMAGES_DIR, f"{job_id}.json")
        
        # Salva i dati (in una implementazione reale, si convertirebbe in formato video/immagine)
        with open(output_file, 'w') as f:
            import json
            json.dump(result, f, indent=2)
        
        return output_file
        
    except Exception as e:
        logger.error(f"Errore nel salvataggio risultato: {str(e)}")
        return None


@app.route('/api/files/<path:filename>')
def serve_generated_file(filename):
    """Serve i file generati."""
    try:
        # Cerca prima nelle immagini, poi nei video
        for directory in [IMAGES_DIR, VIDEOS_DIR]:
            file_path = os.path.join(directory, filename)
            if os.path.exists(file_path):
                return send_file(file_path)
        
        return jsonify({
            "success": False,
            "error": "File non trovato"
        }), 404
        
    except Exception as e:
        logger.error(f"Errore nel servire file: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == '__main__':
    try:
        logger.info("Avvio Lambda Visualizer Advanced Backend...")
        
        # Verifica che il motore unificato sia pronto
        max_wait = 30
        waited = 0
        while unified_engine.state.value != "ready" and waited < max_wait:
            time.sleep(1)
            waited += 1
        
        if unified_engine.state.value != "ready":
            logger.error("Motore unificato non pronto dopo 30 secondi")
            sys.exit(1)
        
        logger.info("Motore unificato pronto - avvio server Flask")
        
        # Avvia il server Flask
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,  # Disabilitato per performance
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("Interruzione da tastiera ricevuta")
    except Exception as e:
        logger.error(f"Errore critico: {str(e)}")
    finally:
        logger.info("Spegnimento sistema...")
        unified_engine.shutdown()
        logger.info("Sistema spento")

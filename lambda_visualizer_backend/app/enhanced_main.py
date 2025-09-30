"""
Enhanced Lambda Visualizer Backend
Applicazione Flask principale con integrazione completa di tutti i sistemi avanzati.
Integra: Persistenza, Beta Reduction, Manim, CuPy, WebSocket, FFmpeg
"""

import os
import logging
import asyncio
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from typing import Dict, Any

# Import dei moduli locali
import sys
sys.path.append('/home/ubuntu/lambda_visualizer_backend')

# Import existing modules
from models.lambda_expression import LambdaExpression
from utils.ollama_service import OllamaService

# Import new enhanced modules
from utils.persistence_system import PersistenceManager, JobManager, JobStatus, JobPriority, SystemStateManager, PerformanceTracker
from utils.complete_beta_reduction import BetaReducer, LambdaParser, ReductionStrategy
from utils.real_integrations import RealManimIntegration, RealGPUAcceleration, RealVideoOutput
from utils.websocket_communication import LambdaVisualizerWebSocketServer, FlaskSocketIOIntegration, MessageType

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedLambdaVisualizer:
    """Sistema Lambda Visualizer completo e integrato."""
    
    def __init__(self):
        # Initialize Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Configuration
        self.app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
        self.app.config['UPLOAD_FOLDER'] = '/home/ubuntu/lambda_visualizer_backend/static/videos'
        
        # Initialize core services
        self.ollama_service = OllamaService()
        
        # Initialize persistence system
        self.persistence_manager = PersistenceManager("./enhanced_lambda_visualizer.db")
        self.job_manager = JobManager(self.persistence_manager)
        self.system_state_manager = SystemStateManager(self.persistence_manager)
        self.performance_tracker = PerformanceTracker(self.persistence_manager)
        
        # Initialize processing components
        self.lambda_parser = LambdaParser()
        self.beta_reducer = BetaReducer(ReductionStrategy.NORMAL_ORDER)
        
        # Initialize integration components
        self.manim_integration = RealManimIntegration("./manim_output")
        self.gpu_acceleration = RealGPUAcceleration()
        self.video_output = RealVideoOutput("./video_output")
        
        # Initialize WebSocket server
        self.websocket_server = LambdaVisualizerWebSocketServer("localhost", 8765)
        self.websocket_thread = None
        
        # Worker management
        self.workers = []
        self.shutdown_event = threading.Event()
        
        # Register routes
        self._register_routes()
        
        # Register WebSocket handlers
        self._register_websocket_handlers()
        
        logger.info("🚀 Enhanced Lambda Visualizer initialized")
    
    def _register_routes(self):
        """Registra tutte le route dell'applicazione."""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Endpoint per il controllo dello stato dell'applicazione."""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '2.0.0-enhanced',
                'services': {
                    'ollama': self.ollama_service.is_available(),
                    'persistence': True,
                    'manim': self.manim_integration.manim_available,
                    'gpu': self.gpu_acceleration.cupy_available,
                    'websocket': True
                },
                'gpu_info': self.gpu_acceleration.device_info
            })
        
        @self.app.route('/api/analyze', methods=['POST'])
        def analyze_lambda_expression():
            """Analizza un'espressione lambda con il nuovo sistema di beta reduction."""
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
                
                # Parse with new system
                term = self.lambda_parser.parse(expression)
                
                # Perform beta reduction
                max_steps = data.get('max_steps', 100)
                strategy = data.get('strategy', 'normal_order')
                
                if strategy != 'normal_order':
                    self.beta_reducer.strategy = ReductionStrategy(strategy)
                
                reduction_result = self.beta_reducer.reduce(term, max_steps=max_steps)
                
                # Record performance metrics
                self.performance_tracker.record_metric(
                    "analysis_time", 
                    reduction_result['steps_taken'],
                    metadata={"expression": expression, "strategy": strategy}
                )
                
                # Ollama analysis if available
                ollama_analysis = None
                if self.ollama_service.is_available():
                    ollama_response = self.ollama_service.analyze_lambda_expression(expression)
                    if ollama_response.success:
                        ollama_analysis = ollama_response.data
                
                # Prepare response
                response_data = {
                    'success': True,
                    'expression': expression,
                    'beta_reduction': reduction_result,
                    'ollama_analysis': ollama_analysis,
                    'gpu_used': self.gpu_acceleration.cupy_available,
                    'timestamp': datetime.now().isoformat()
                }
                
                return jsonify(response_data)
                
            except Exception as e:
                logger.error(f"Errore nell'analisi: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/visualize', methods=['POST'])
        def create_visualization():
            """Crea una visualizzazione avanzata dell'espressione lambda."""
            try:
                data = request.get_json()
                
                if not data or 'expression' not in data:
                    return jsonify({
                        'success': False,
                        'error': 'Espressione lambda richiesta'
                    }), 400
                
                expression = data['expression'].strip()
                config_data = data.get('config', {})
                
                # Create job for visualization
                job_id = self.job_manager.create_job(
                    job_type="lambda_visualization",
                    input_data={
                        "expression": expression,
                        "config": config_data
                    },
                    priority=JobPriority.NORMAL,
                    estimated_duration=30.0
                )
                
                # Start processing in background
                threading.Thread(
                    target=self._process_visualization_job,
                    args=(job_id,),
                    daemon=True
                ).start()
                
                return jsonify({
                    'success': True,
                    'job_id': job_id,
                    'status': 'submitted',
                    'message': 'Visualization job submitted successfully'
                })
                
            except Exception as e:
                logger.error(f"Errore nella visualizzazione: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/jobs/<job_id>', methods=['GET'])
        def get_job_status(job_id):
            """Ottiene lo stato di un job."""
            try:
                job = self.job_manager.get_job(job_id)
                if not job:
                    return jsonify({
                        'success': False,
                        'error': 'Job non trovato'
                    }), 404
                
                return jsonify({
                    'success': True,
                    'job_id': job.job_id,
                    'status': job.status.value,
                    'progress': job.progress,
                    'created_at': job.created_at.isoformat(),
                    'started_at': job.started_at.isoformat() if job.started_at else None,
                    'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                    'result': job.result_data,
                    'error': job.error_message
                })
                
            except Exception as e:
                logger.error(f"Errore nel recupero job: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/jobs', methods=['GET'])
        def list_jobs():
            """Lista tutti i job."""
            try:
                status_filter = request.args.get('status')
                limit = int(request.args.get('limit', 50))
                
                if status_filter:
                    status = JobStatus(status_filter)
                    jobs = self.job_manager.get_jobs_by_status(status, limit)
                else:
                    jobs = self.job_manager.get_jobs_by_status(JobStatus.PENDING, limit)
                    jobs.extend(self.job_manager.get_jobs_by_status(JobStatus.RUNNING, limit))
                    jobs.extend(self.job_manager.get_jobs_by_status(JobStatus.COMPLETED, limit))
                
                return jsonify({
                    'success': True,
                    'jobs': [
                        {
                            'job_id': job.job_id,
                            'job_type': job.job_type,
                            'status': job.status.value,
                            'progress': job.progress,
                            'created_at': job.created_at.isoformat(),
                            'input_data': job.input_data
                        }
                        for job in jobs[:limit]
                    ]
                })
                
            except Exception as e:
                logger.error(f"Errore nel listing job: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/statistics', methods=['GET'])
        def get_statistics():
            """Ottiene statistiche del sistema."""
            try:
                stats = self.job_manager.get_job_statistics()
                
                return jsonify({
                    'success': True,
                    'system_stats': stats,
                    'gpu_info': self.gpu_acceleration.device_info,
                    'manim_available': self.manim_integration.manim_available,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Errore nelle statistiche: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/video/<video_id>', methods=['GET'])
        def get_video(video_id):
            """Serve un video generato."""
            try:
                # Check if video exists in new output directory
                video_path = Path("./video_output") / f"{video_id}.mp4"
                
                if not video_path.exists():
                    # Fallback to old location
                    video_path = Path(self.app.config['UPLOAD_FOLDER']) / f"{video_id}.mp4"
                
                if not video_path.exists():
                    return jsonify({
                        'success': False,
                        'error': 'Video non trovato'
                    }), 404
                
                return send_file(
                    str(video_path),
                    mimetype='video/mp4',
                    as_attachment=False
                )
                
            except Exception as e:
                logger.error(f"Errore nel servire video: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/examples', methods=['GET'])
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
        
        @self.app.errorhandler(404)
        def not_found(error):
            """Handler per errori 404."""
            return jsonify({
                'success': False,
                'error': 'Endpoint non trovato'
            }), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            """Handler per errori 500."""
            return jsonify({
                'success': False,
                'error': 'Errore interno del server'
            }), 500
    
    def _register_websocket_handlers(self):
        """Registra handler personalizzati per WebSocket."""
        
        # Override job submission handler
        async def handle_job_submit(message):
            """Gestisce sottomissione job via WebSocket."""
            
            client_id = message.client_id
            job_data = message.data
            
            try:
                job_id = self.job_manager.create_job(
                    job_type="lambda_visualization_ws",
                    input_data=job_data,
                    priority=JobPriority.NORMAL,
                    metadata={"client_id": client_id}
                )
                
                await self.websocket_server.manager.send_to_client(
                    client_id, MessageType.JOB_UPDATE, {
                        "job_id": job_id,
                        "status": "submitted",
                        "message": "Job submitted successfully"
                    }
                )
                
                # Start processing
                threading.Thread(
                    target=self._process_websocket_job,
                    args=(job_id, client_id),
                    daemon=True
                ).start()
                
                logger.info(f"🚀 WebSocket job {job_id} submitted by {client_id}")
                
            except Exception as e:
                await self.websocket_server.manager.send_error(
                    client_id, f"Job submission failed: {e}"
                )
        
        self.websocket_server.manager.message_handlers[MessageType.JOB_SUBMIT] = handle_job_submit
    
    def _process_visualization_job(self, job_id: str):
        """Processa un job di visualizzazione."""
        try:
            # Update status to running
            self.job_manager.update_job_status(job_id, JobStatus.RUNNING, progress=0.0)
            
            job = self.job_manager.get_job(job_id)
            if not job:
                return
            
            expression = job.input_data["expression"]
            config = job.input_data.get("config", {})
            
            # Step 1: Parse and analyze (20%)
            term = self.lambda_parser.parse(expression)
            reduction_result = self.beta_reducer.reduce(term, max_steps=100)
            
            self.job_manager.update_job_status(job_id, JobStatus.RUNNING, progress=0.2)
            
            # Step 2: Create Manim animation (60%)
            scene_config = {
                "duration": config.get("duration", 5.0),
                "quality": config.get("quality", "medium_quality"),
                "fps": config.get("fps", 30)
            }
            
            animation_result = self.manim_integration.create_lambda_animation(
                expression, scene_config
            )
            
            self.job_manager.update_job_status(job_id, JobStatus.RUNNING, progress=0.8)
            
            # Step 3: Generate final video if needed (90%)
            final_video_path = None
            
            if animation_result["success"] and animation_result.get("frames"):
                video_result = self.video_output.frames_to_video(
                    animation_result["frames"],
                    f"lambda_viz_{job_id}",
                    fps=scene_config["fps"],
                    quality=scene_config["quality"]
                )
                
                if video_result["success"]:
                    final_video_path = video_result["video_path"]
            
            # Step 4: Compile final result (100%)
            result = {
                "expression": expression,
                "beta_reduction": reduction_result,
                "animation": animation_result,
                "video_path": final_video_path,
                "video_id": f"lambda_viz_{job_id}",
                "processing_info": {
                    "gpu_used": self.gpu_acceleration.cupy_available,
                    "manim_used": self.manim_integration.manim_available,
                    "video_generated": final_video_path is not None
                }
            }
            
            # Save result and mark as completed
            self.job_manager.save_job_result(job_id, result)
            self.job_manager.update_job_status(job_id, JobStatus.COMPLETED, progress=1.0)
            
            logger.info(f"✅ Job {job_id} completed successfully")
            
        except Exception as e:
            # Mark job as failed
            self.job_manager.update_job_status(
                job_id, JobStatus.FAILED, 
                error_message=str(e)
            )
            logger.error(f"❌ Job {job_id} failed: {e}")
    
    def _process_websocket_job(self, job_id: str, client_id: str):
        """Processa un job WebSocket con notifiche real-time."""
        try:
            # Update status to running
            self.job_manager.update_job_status(job_id, JobStatus.RUNNING, progress=0.0)
            
            # Notify WebSocket client
            asyncio.run(self.websocket_server.manager.send_to_client(
                client_id, MessageType.JOB_UPDATE, {
                    "job_id": job_id,
                    "status": "running",
                    "progress": 0.0
                }
            ))
            
            job = self.job_manager.get_job(job_id)
            if not job:
                return
            
            expression = job.input_data["expression"]
            
            # Step 1: Parse and analyze (20%)
            term = self.lambda_parser.parse(expression)
            reduction_result = self.beta_reducer.reduce(term, max_steps=100)
            
            self.job_manager.update_job_status(job_id, JobStatus.RUNNING, progress=0.2)
            
            # Notify progress
            asyncio.run(self.websocket_server.manager.send_to_client(
                client_id, MessageType.JOB_UPDATE, {
                    "job_id": job_id,
                    "status": "running",
                    "progress": 0.2,
                    "message": "Analysis completed"
                }
            ))
            
            # Step 2: Create visualization (80%)
            scene_config = {
                "duration": 3.0,
                "quality": "low_quality",
                "fps": 30
            }
            
            animation_result = self.manim_integration.create_lambda_animation(
                expression, scene_config
            )
            
            self.job_manager.update_job_status(job_id, JobStatus.RUNNING, progress=0.8)
            
            # Notify progress
            asyncio.run(self.websocket_server.manager.send_to_client(
                client_id, MessageType.JOB_UPDATE, {
                    "job_id": job_id,
                    "status": "running",
                    "progress": 0.8,
                    "message": "Visualization completed"
                }
            ))
            
            # Step 3: Generate video (100%)
            final_video_path = None
            
            if animation_result["success"] and animation_result.get("frames"):
                video_result = self.video_output.frames_to_video(
                    animation_result["frames"],
                    f"lambda_viz_{job_id}",
                    fps=scene_config["fps"],
                    quality=scene_config["quality"]
                )
                
                if video_result["success"]:
                    final_video_path = video_result["video_path"]
            
            # Compile final result
            result = {
                "expression": expression,
                "beta_reduction": reduction_result,
                "animation": animation_result,
                "video_path": final_video_path,
                "video_id": f"lambda_viz_{job_id}",
                "processing_info": {
                    "gpu_used": self.gpu_acceleration.cupy_available,
                    "manim_used": self.manim_integration.manim_available,
                    "video_generated": final_video_path is not None
                }
            }
            
            # Save result and mark as completed
            self.job_manager.save_job_result(job_id, result)
            self.job_manager.update_job_status(job_id, JobStatus.COMPLETED, progress=1.0)
            
            # Notify completion
            asyncio.run(self.websocket_server.manager.send_to_client(
                client_id, MessageType.JOB_COMPLETED, {
                    "job_id": job_id,
                    "status": "completed",
                    "progress": 1.0,
                    "result": result
                }
            ))
            
            logger.info(f"✅ WebSocket job {job_id} completed successfully")
            
        except Exception as e:
            # Mark job as failed
            self.job_manager.update_job_status(
                job_id, JobStatus.FAILED, 
                error_message=str(e)
            )
            
            # Notify failure
            asyncio.run(self.websocket_server.manager.send_to_client(
                client_id, MessageType.JOB_FAILED, {
                    "job_id": job_id,
                    "status": "failed",
                    "error": str(e)
                }
            ))
            
            logger.error(f"❌ WebSocket job {job_id} failed: {e}")
    
    def start_websocket_server(self):
        """Avvia il server WebSocket in un thread separato."""
        def run_websocket():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.websocket_server.start_server())
            loop.run_forever()
        
        self.websocket_thread = threading.Thread(target=run_websocket, daemon=True)
        self.websocket_thread.start()
        logger.info("🔌 WebSocket server started")
    
    def run(self, host='0.0.0.0', port=5000, debug=True):
        """Avvia l'applicazione completa."""
        # Create necessary directories
        os.makedirs(self.app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs("./manim_output", exist_ok=True)
        os.makedirs("./video_output", exist_ok=True)
        
        # Start WebSocket server
        self.start_websocket_server()
        
        # Log startup information
        logger.info("🚀 Starting Enhanced Lambda Visualizer Backend...")
        logger.info(f"   - Ollama available: {self.ollama_service.is_available()}")
        logger.info(f"   - Manim available: {self.manim_integration.manim_available}")
        logger.info(f"   - GPU available: {self.gpu_acceleration.cupy_available}")
        logger.info(f"   - GPU device: {self.gpu_acceleration.device_info['type']}")
        logger.info(f"   - WebSocket: ws://localhost:8765")
        
        # Start Flask app
        self.app.run(host=host, port=port, debug=debug, threaded=True)

# Create and run the application
if __name__ == '__main__':
    app = EnhancedLambdaVisualizer()
    app.run()

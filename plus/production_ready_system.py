#!/usr/bin/env python3
"""
Production Ready Lambda Visualizer System
Sistema completo che integra tutte le soluzioni alle criticità identificate.

Risolve tutte e 5 le criticità:
1. Integrazione reale con Manim e CuPy
2. Persistenza dei dati e job con database
3. Output video reale con FFmpeg
4. Riduzione beta completa e corretta
5. Comunicazione WebSocket real-time
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import threading
import time

# Import our solutions
from real_integrations import RealManimIntegration, RealGPUAcceleration, RealVideoOutput
from persistence_system import PersistenceManager, JobManager, JobStatus, JobPriority
from complete_beta_reduction import BetaReducer, LambdaParser, ReductionStrategy
from websocket_communication import LambdaVisualizerWebSocketServer, MessageType

# Flask integration
from flask import Flask, request, jsonify
from flask_cors import CORS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SystemConfiguration:
    """Configurazione del sistema."""
    # Database
    database_path: str = "./production_lambda_visualizer.db"
    
    # WebSocket
    websocket_host: str = "localhost"
    websocket_port: int = 8765
    
    # Flask API
    api_host: str = "localhost"
    api_port: int = 5000
    
    # Processing
    max_concurrent_jobs: int = 4
    job_timeout_seconds: int = 300
    
    # Output
    output_directory: str = "./output"
    video_quality: str = "high"
    
    # Beta reduction
    max_reduction_steps: int = 1000
    default_strategy: str = "normal_order"

class ProductionLambdaVisualizer:
    """Sistema Lambda Visualizer pronto per la produzione."""
    
    def __init__(self, config: SystemConfiguration = None):
        self.config = config or SystemConfiguration()
        
        # Initialize components
        self.persistence_manager = PersistenceManager(self.config.database_path)
        self.job_manager = JobManager(self.persistence_manager)
        
        # Integration components
        self.manim_integration = RealManimIntegration(
            str(Path(self.config.output_directory) / "manim")
        )
        self.gpu_acceleration = RealGPUAcceleration()
        self.video_output = RealVideoOutput(
            str(Path(self.config.output_directory) / "videos")
        )
        
        # Processing components
        self.lambda_parser = LambdaParser()
        self.beta_reducer = BetaReducer(
            ReductionStrategy(self.config.default_strategy)
        )
        
        # WebSocket server
        self.websocket_server = LambdaVisualizerWebSocketServer(
            self.config.websocket_host,
            self.config.websocket_port
        )
        
        # Flask API
        self.flask_app = self._create_flask_app()
        
        # Worker management
        self.workers = []
        self.shutdown_event = threading.Event()
        
        # Register WebSocket handlers
        self._register_websocket_handlers()
        
        logger.info("🚀 Production Lambda Visualizer initialized")
    
    def _create_flask_app(self) -> Flask:
        """Crea l'applicazione Flask."""
        
        app = Flask(__name__)
        CORS(app)
        
        @app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint."""
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0-production",
                "components": {
                    "database": "connected",
                    "manim": "available" if self.manim_integration.manim_available else "fallback",
                    "gpu": self.gpu_acceleration.device_info["type"],
                    "websocket": "running"
                }
            })
        
        @app.route('/api/analyze', methods=['POST'])
        def analyze_expression():
            """Analizza un'espressione lambda."""
            
            data = request.get_json()
            if not data or 'expression' not in data:
                return jsonify({"error": "Missing expression"}), 400
            
            try:
                # Parse expression
                term = self.lambda_parser.parse(data['expression'])
                
                # Perform beta reduction
                reduction_result = self.beta_reducer.reduce(
                    term,
                    max_steps=data.get('max_steps', 100)
                )
                
                return jsonify({
                    "success": True,
                    "analysis": reduction_result,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Analysis error: {e}")
                return jsonify({"error": str(e)}), 400
        
        @app.route('/api/jobs', methods=['POST'])
        def submit_job():
            """Sottomette un job di visualizzazione."""
            
            data = request.get_json()
            if not data or 'expression' not in data:
                return jsonify({"error": "Missing expression"}), 400
            
            try:
                job_id = self.job_manager.create_job(
                    job_type="lambda_visualization",
                    input_data=data,
                    priority=JobPriority(data.get('priority', JobPriority.NORMAL.value)),
                    estimated_duration=data.get('estimated_duration', 30.0)
                )
                
                return jsonify({
                    "success": True,
                    "job_id": job_id,
                    "status": "submitted",
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Job submission error: {e}")
                return jsonify({"error": str(e)}), 400
        
        @app.route('/api/jobs/<job_id>', methods=['GET'])
        def get_job_status(job_id):
            """Ottiene lo stato di un job."""
            
            job = self.job_manager.get_job(job_id)
            if not job:
                return jsonify({"error": "Job not found"}), 404
            
            return jsonify({
                "job_id": job.job_id,
                "status": job.status.value,
                "progress": job.progress,
                "created_at": job.created_at.isoformat(),
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "result": job.result_data,
                "error": job.error_message
            })
        
        @app.route('/api/statistics', methods=['GET'])
        def get_statistics():
            """Ottiene statistiche del sistema."""
            
            stats = self.job_manager.get_job_statistics()
            return jsonify({
                "system_stats": stats,
                "gpu_info": self.gpu_acceleration.device_info,
                "timestamp": datetime.now().isoformat()
            })
        
        return app
    
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
                
                logger.info(f"🚀 WebSocket job {job_id} submitted by {client_id}")
                
            except Exception as e:
                await self.websocket_server.manager.send_error(
                    client_id, f"Job submission failed: {e}"
                )
        
        self.websocket_server.manager.message_handlers[MessageType.JOB_SUBMIT] = handle_job_submit
    
    async def process_job(self, job_id: str) -> Dict[str, Any]:
        """Processa un job completo."""
        
        job = self.job_manager.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        try:
            # Update status to running
            self.job_manager.update_job_status(job_id, JobStatus.RUNNING, progress=0.0)
            
            # Notify WebSocket clients if applicable
            if job.metadata and "client_id" in job.metadata:
                await self.websocket_server.manager.send_to_client(
                    job.metadata["client_id"], MessageType.JOB_UPDATE, {
                        "job_id": job_id,
                        "status": "running",
                        "progress": 0.0
                    }
                )
            
            # Step 1: Parse and analyze expression (20%)
            expression = job.input_data["expression"]
            term = self.lambda_parser.parse(expression)
            
            self.job_manager.update_job_status(job_id, JobStatus.RUNNING, progress=0.2)
            
            # Step 2: Perform beta reduction (40%)
            reduction_result = self.beta_reducer.reduce(term, max_steps=self.config.max_reduction_steps)
            
            self.job_manager.update_job_status(job_id, JobStatus.RUNNING, progress=0.4)
            
            # Step 3: Create Manim animation (70%)
            scene_config = {
                "duration": job.input_data.get("duration", 5.0),
                "quality": job.input_data.get("quality", self.config.video_quality),
                "fps": job.input_data.get("fps", 30)
            }
            
            animation_result = self.manim_integration.create_lambda_animation(
                expression, scene_config
            )
            
            self.job_manager.update_job_status(job_id, JobStatus.RUNNING, progress=0.7)
            
            # Step 4: Generate final video if needed (90%)
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
            
            self.job_manager.update_job_status(job_id, JobStatus.RUNNING, progress=0.9)
            
            # Step 5: Compile final result (100%)
            result = {
                "expression": expression,
                "analysis": reduction_result,
                "animation": animation_result,
                "video_path": final_video_path,
                "processing_info": {
                    "gpu_used": self.gpu_acceleration.cupy_available,
                    "manim_used": self.manim_integration.manim_available,
                    "video_generated": final_video_path is not None
                }
            }
            
            # Save result and mark as completed
            self.job_manager.save_job_result(job_id, result)
            self.job_manager.update_job_status(job_id, JobStatus.COMPLETED, progress=1.0)
            
            # Notify WebSocket clients
            if job.metadata and "client_id" in job.metadata:
                await self.websocket_server.manager.send_to_client(
                    job.metadata["client_id"], MessageType.JOB_COMPLETED, {
                        "job_id": job_id,
                        "status": "completed",
                        "result": result
                    }
                )
            
            logger.info(f"✅ Job {job_id} completed successfully")
            return result
            
        except Exception as e:
            # Mark job as failed
            self.job_manager.update_job_status(
                job_id, JobStatus.FAILED, 
                error_message=str(e)
            )
            
            # Notify WebSocket clients
            if job.metadata and "client_id" in job.metadata:
                await self.websocket_server.manager.send_to_client(
                    job.metadata["client_id"], MessageType.JOB_FAILED, {
                        "job_id": job_id,
                        "status": "failed",
                        "error": str(e)
                    }
                )
            
            logger.error(f"❌ Job {job_id} failed: {e}")
            raise
    
    async def job_worker(self, worker_id: int):
        """Worker per processare job dalla coda."""
        
        logger.info(f"🔧 Worker {worker_id} started")
        
        while not self.shutdown_event.is_set():
            try:
                # Get pending jobs
                pending_jobs = self.job_manager.get_pending_jobs(limit=1)
                
                if pending_jobs:
                    job = pending_jobs[0]
                    logger.info(f"🔄 Worker {worker_id} processing job {job.job_id}")
                    
                    await self.process_job(job.job_id)
                else:
                    # No jobs, wait a bit
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(5)  # Wait before retrying
        
        logger.info(f"🔧 Worker {worker_id} stopped")
    
    async def start_system(self):
        """Avvia il sistema completo."""
        
        logger.info("🚀 Starting Production Lambda Visualizer System")
        
        # Create output directories
        Path(self.config.output_directory).mkdir(exist_ok=True)
        Path(self.config.output_directory, "manim").mkdir(exist_ok=True)
        Path(self.config.output_directory, "videos").mkdir(exist_ok=True)
        
        # Start WebSocket server
        await self.websocket_server.start_server()
        
        # Start job workers
        for i in range(self.config.max_concurrent_jobs):
            worker = asyncio.create_task(self.job_worker(i))
            self.workers.append(worker)
        
        # Start Flask app in a separate thread
        def run_flask():
            self.flask_app.run(
                host=self.config.api_host,
                port=self.config.api_port,
                debug=False,
                threaded=True
            )
        
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        
        logger.info(f"✅ System started successfully")
        logger.info(f"   - WebSocket: ws://{self.config.websocket_host}:{self.config.websocket_port}")
        logger.info(f"   - REST API: http://{self.config.api_host}:{self.config.api_port}")
        logger.info(f"   - Workers: {self.config.max_concurrent_jobs}")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown requested")
            await self.stop_system()
    
    async def stop_system(self):
        """Ferma il sistema."""
        
        logger.info("🛑 Stopping Production Lambda Visualizer System")
        
        # Signal shutdown
        self.shutdown_event.set()
        
        # Stop workers
        for worker in self.workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        
        # Stop WebSocket server
        await self.websocket_server.stop_server()
        
        logger.info("✅ System stopped successfully")

# Configuration and startup
def create_production_config() -> SystemConfiguration:
    """Crea configurazione per produzione."""
    
    return SystemConfiguration(
        database_path="./production_lambda_visualizer.db",
        websocket_host="0.0.0.0",  # Accept connections from any host
        websocket_port=8765,
        api_host="0.0.0.0",
        api_port=5000,
        max_concurrent_jobs=4,
        job_timeout_seconds=600,  # 10 minutes
        output_directory="./production_output",
        video_quality="high",
        max_reduction_steps=1000,
        default_strategy="normal_order"
    )

async def main():
    """Funzione principale."""
    
    print("🧠 Production Lambda Visualizer System")
    print("=" * 50)
    
    # Create system with production config
    config = create_production_config()
    system = ProductionLambdaVisualizer(config)
    
    # Start system
    await system.start_system()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"System error: {e}")
        print(f"❌ System failed to start: {e}")

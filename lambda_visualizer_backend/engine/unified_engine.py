"""
Sistema Unificato Lambda Visualizer Engine
Integra tutti i componenti: Scene Manager, GPU Acceleration, Temporal Control, Manim Integration
"""

import logging
import asyncio
import threading
import time
import uuid
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np

from .scene_manager import SceneManager, SceneType, RenderConfig, BaseScene
from .gpu_acceleration import GPUAccelerator, ComputeJob, ComputeTask, ComputeDevice
from .temporal_control import TemporalController, AnimationTimeline, StateTransitionManager
from .manim_integration import LambdaScene, LambdaSceneFactory, AnimationType

logger = logging.getLogger(__name__)


class EngineState(Enum):
    """Stati del motore unificato."""
    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    RENDERING = "rendering"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class RenderQuality(Enum):
    """Livelli di qualità del rendering."""
    PREVIEW = "preview"      # 480p, 30fps, CPU only
    STANDARD = "standard"    # 720p, 60fps, GPU assisted
    HIGH = "high"           # 1080p, 60fps, GPU accelerated
    ULTRA = "ultra"         # 4K, 60fps, Full GPU pipeline


@dataclass
class EngineConfig:
    """Configurazione del motore unificato."""
    # Configurazione generale
    max_concurrent_renders: int = 4
    gpu_acceleration: bool = True
    temporal_precision: float = 0.016  # ~60fps
    
    # Configurazioni di qualità
    quality_presets: Dict[RenderQuality, RenderConfig] = field(default_factory=lambda: {
        RenderQuality.PREVIEW: RenderConfig(
            width=854, height=480, fps=30, quality="low",
            use_gpu_acceleration=False
        ),
        RenderQuality.STANDARD: RenderConfig(
            width=1280, height=720, fps=60, quality="medium",
            use_gpu_acceleration=True
        ),
        RenderQuality.HIGH: RenderConfig(
            width=1920, height=1080, fps=60, quality="high",
            use_gpu_acceleration=True
        ),
        RenderQuality.ULTRA: RenderConfig(
            width=3840, height=2160, fps=60, quality="ultra",
            use_gpu_acceleration=True
        )
    })
    
    # Limiti di risorse
    max_memory_usage_mb: int = 4096
    max_gpu_memory_usage_mb: int = 2048
    render_timeout_seconds: int = 300


@dataclass
class RenderJob:
    """Job di rendering completo."""
    job_id: str
    scene_type: SceneType
    lambda_data: Dict[str, Any]
    config: RenderConfig
    quality: RenderQuality
    
    # Parametri avanzati
    animation_timeline: Optional[AnimationTimeline] = None
    custom_parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Callback per progresso
    progress_callback: Optional[Callable[[str, float], None]] = None
    completion_callback: Optional[Callable[[str, bool, Any], None]] = None
    
    # Metadati
    created_at: float = field(default_factory=time.time)
    priority: int = 0  # 0 = massima priorità


class UnifiedEngine:
    """
    Motore unificato che coordina tutti i sottosistemi.
    Fornisce un'interfaccia semplificata per rendering avanzati.
    """
    
    def __init__(self, config: EngineConfig = None):
        self.config = config or EngineConfig()
        self.state = EngineState.INITIALIZING
        self.engine_id = str(uuid.uuid4())[:8]
        
        # Sottosistemi
        self.scene_manager = SceneManager()
        self.gpu_accelerator = GPUAccelerator()
        self.temporal_controller = TemporalController()
        self.state_manager = StateTransitionManager()
        
        # Job management
        self.render_queue: List[RenderJob] = []
        self.active_jobs: Dict[str, RenderJob] = {}
        self.completed_jobs: Dict[str, Dict[str, Any]] = {}
        
        # Threading e sincronizzazione
        self.lock = threading.RLock()
        self.worker_threads: List[threading.Thread] = []
        self.shutdown_event = threading.Event()
        
        # Metriche e monitoring
        self.metrics = {
            "total_jobs_processed": 0,
            "successful_renders": 0,
            "failed_renders": 0,
            "total_render_time": 0.0,
            "gpu_utilization": 0.0,
            "memory_usage": 0.0
        }
        
        # Inizializza il motore
        self._initialize_engine()
        
        logger.info(f"UnifiedEngine {self.engine_id} inizializzato")
    
    def _initialize_engine(self):
        """Inizializza tutti i sottosistemi."""
        try:
            # Avvia worker threads
            for i in range(self.config.max_concurrent_renders):
                worker = threading.Thread(
                    target=self._render_worker,
                    name=f"RenderWorker-{i}",
                    daemon=True
                )
                worker.start()
                self.worker_threads.append(worker)
            
            # Avvia thread di monitoring
            monitor_thread = threading.Thread(
                target=self._monitoring_worker,
                name="MonitoringWorker",
                daemon=True
            )
            monitor_thread.start()
            self.worker_threads.append(monitor_thread)
            
            self.state = EngineState.READY
            logger.info("Tutti i sottosistemi inizializzati con successo")
            
        except Exception as e:
            self.state = EngineState.ERROR
            logger.error(f"Errore nell'inizializzazione: {str(e)}")
            raise
    
    def submit_render_job(self, job: RenderJob) -> str:
        """Sottomette un job di rendering alla coda."""
        with self.lock:
            # Assegna ID se non presente
            if not job.job_id:
                job.job_id = f"render_{uuid.uuid4().hex[:8]}"
            
            # Aggiungi alla coda con priorità
            self.render_queue.append(job)
            self.render_queue.sort(key=lambda j: j.priority, reverse=True)
            
            logger.info(f"Job {job.job_id} aggiunto alla coda (tipo: {job.scene_type.value})")
            return job.job_id
    
    def create_lambda_visualization(self, expression: str, 
                                  quality: RenderQuality = RenderQuality.STANDARD,
                                  scene_type: SceneType = SceneType.LAMBDA_BASIC,
                                  **kwargs) -> str:
        """Crea una visualizzazione lambda con configurazione semplificata."""
        
        # Prepara i dati lambda
        lambda_data = {
            "expression": expression,
            "structure": kwargs.get("structure", {}),
            "metrics": kwargs.get("metrics", {}),
            "reduction_steps": kwargs.get("reduction_steps", [])
        }
        
        # Crea il job di rendering
        job = RenderJob(
            job_id="",  # Verrà assegnato automaticamente
            scene_type=scene_type,
            lambda_data=lambda_data,
            config=self.config.quality_presets[quality],
            quality=quality,
            custom_parameters=kwargs,
            progress_callback=kwargs.get("progress_callback"),
            completion_callback=kwargs.get("completion_callback")
        )
        
        return self.submit_render_job(job)
    
    def create_beta_reduction_animation(self, expression: str, reduction_steps: List[Dict],
                                      quality: RenderQuality = RenderQuality.STANDARD,
                                      **kwargs) -> str:
        """Crea un'animazione di riduzione beta."""
        
        # Crea timeline per l'animazione
        timeline = AnimationTimeline(duration=len(reduction_steps) * 2.0)
        
        # Aggiungi keyframes per ogni step
        for i, step in enumerate(reduction_steps):
            time_fraction = i / len(reduction_steps)
            # In una implementazione reale, qui si aggiungerebbero keyframes specifici
        
        lambda_data = {
            "expression": expression,
            "reduction_steps": reduction_steps,
            "structure": kwargs.get("structure", {}),
            "animation_config": {
                "step_duration": kwargs.get("step_duration", 2.0),
                "highlight_duration": kwargs.get("highlight_duration", 0.5),
                "transition_easing": kwargs.get("easing", "smooth")
            }
        }
        
        job = RenderJob(
            job_id="",
            scene_type=SceneType.LAMBDA_REDUCTION,
            lambda_data=lambda_data,
            config=self.config.quality_presets[quality],
            quality=quality,
            animation_timeline=timeline,
            custom_parameters=kwargs
        )
        
        return self.submit_render_job(job)
    
    def create_interactive_exploration(self, expression: str,
                                     quality: RenderQuality = RenderQuality.HIGH,
                                     **kwargs) -> str:
        """Crea una visualizzazione interattiva esplorabile."""
        
        lambda_data = {
            "expression": expression,
            "structure": kwargs.get("structure", {}),
            "interaction_config": {
                "enable_hover": kwargs.get("enable_hover", True),
                "enable_click": kwargs.get("enable_click", True),
                "show_tooltips": kwargs.get("show_tooltips", True),
                "highlight_connections": kwargs.get("highlight_connections", True)
            }
        }
        
        job = RenderJob(
            job_id="",
            scene_type=SceneType.LAMBDA_GRAPH,
            lambda_data=lambda_data,
            config=self.config.quality_presets[quality],
            quality=quality,
            custom_parameters=kwargs
        )
        
        return self.submit_render_job(job)
    
    def _render_worker(self):
        """Worker thread per l'esecuzione dei job di rendering."""
        worker_name = threading.current_thread().name
        logger.info(f"{worker_name} avviato")
        
        while not self.shutdown_event.is_set():
            try:
                # Prendi il prossimo job dalla coda
                job = self._get_next_job()
                if not job:
                    time.sleep(0.1)
                    continue
                
                logger.info(f"{worker_name} inizia rendering job {job.job_id}")
                
                # Esegui il rendering
                success, result = self._execute_render_job(job)
                
                # Gestisci il risultato
                self._handle_job_completion(job, success, result)
                
            except Exception as e:
                logger.error(f"Errore in {worker_name}: {str(e)}")
                time.sleep(1.0)
        
        logger.info(f"{worker_name} terminato")
    
    def _get_next_job(self) -> Optional[RenderJob]:
        """Ottiene il prossimo job dalla coda."""
        with self.lock:
            if self.render_queue:
                return self.render_queue.pop(0)
            return None
    
    def _execute_render_job(self, job: RenderJob) -> Tuple[bool, Any]:
        """Esegue un job di rendering."""
        start_time = time.time()
        
        try:
            with self.lock:
                self.active_jobs[job.job_id] = job
            
            # Notifica inizio
            if job.progress_callback:
                job.progress_callback(job.job_id, 0.0)
            
            # Fase 1: Preparazione dati (10%)
            prepared_data = self._prepare_render_data(job)
            if job.progress_callback:
                job.progress_callback(job.job_id, 0.1)
            
            # Fase 2: Calcoli GPU se necessario (30%)
            if job.config.use_gpu_acceleration:
                gpu_result = self._execute_gpu_computations(job, prepared_data)
                prepared_data.update(gpu_result)
            if job.progress_callback:
                job.progress_callback(job.job_id, 0.3)
            
            # Fase 3: Creazione scene (50%)
            scene = self._create_scene(job, prepared_data)
            if job.progress_callback:
                job.progress_callback(job.job_id, 0.5)
            
            # Fase 4: Rendering frame (90%)
            rendered_frames = self._render_scene_frames(job, scene)
            if job.progress_callback:
                job.progress_callback(job.job_id, 0.9)
            
            # Fase 5: Post-processing e finalizzazione (100%)
            final_result = self._finalize_render(job, rendered_frames)
            if job.progress_callback:
                job.progress_callback(job.job_id, 1.0)
            
            # Aggiorna metriche
            render_time = time.time() - start_time
            with self.lock:
                self.metrics["total_jobs_processed"] += 1
                self.metrics["successful_renders"] += 1
                self.metrics["total_render_time"] += render_time
            
            logger.info(f"Job {job.job_id} completato in {render_time:.2f}s")
            return True, final_result
            
        except Exception as e:
            # Aggiorna metriche di errore
            with self.lock:
                self.metrics["total_jobs_processed"] += 1
                self.metrics["failed_renders"] += 1
            
            logger.error(f"Errore nel rendering job {job.job_id}: {str(e)}")
            return False, str(e)
        
        finally:
            with self.lock:
                if job.job_id in self.active_jobs:
                    del self.active_jobs[job.job_id]
    
    def _prepare_render_data(self, job: RenderJob) -> Dict[str, Any]:
        """Prepara i dati per il rendering."""
        data = job.lambda_data.copy()
        
        # Aggiungi configurazioni di rendering
        data["render_config"] = {
            "width": job.config.width,
            "height": job.config.height,
            "fps": job.config.fps,
            "duration": job.config.duration,
            "quality": job.quality.value
        }
        
        # Aggiungi parametri personalizzati
        data.update(job.custom_parameters)
        
        return data
    
    def _execute_gpu_computations(self, job: RenderJob, data: Dict[str, Any]) -> Dict[str, Any]:
        """Esegue calcoli GPU se necessario."""
        gpu_results = {}
        
        # Calcolo layout grafo se necessario
        if "structure" in data and data["structure"].get("nodes"):
            layout_job = ComputeJob(
                job_id=f"{job.job_id}_layout",
                task_type=ComputeTask.GRAPH_LAYOUT,
                input_data={
                    "nodes": data["structure"]["nodes"],
                    "edges": data["structure"].get("edges", [])
                },
                parameters={
                    "spring_constant": 1.0,
                    "time_step": 0.01,
                    "iterations": 100
                }
            )
            
            layout_job_id = self.gpu_accelerator.submit_job(layout_job)
            
            # Attendi risultato (semplificato - in produzione userebbe async)
            max_wait = 30  # secondi
            waited = 0
            while waited < max_wait:
                status = self.gpu_accelerator.get_job_status(layout_job_id)
                if status and status.get("done"):
                    if "result" in status:
                        gpu_results["optimized_layout"] = status["result"]
                    break
                time.sleep(0.1)
                waited += 0.1
        
        # Altri calcoli GPU...
        
        return gpu_results
    
    def _create_scene(self, job: RenderJob, data: Dict[str, Any]) -> Any:
        """Crea la scene appropriata."""
        if job.scene_type == SceneType.LAMBDA_BASIC:
            return LambdaSceneFactory.create_basic_visualization(data)
        elif job.scene_type == SceneType.LAMBDA_REDUCTION:
            reduction_steps = data.get("reduction_steps", [])
            return LambdaSceneFactory.create_reduction_animation(data, reduction_steps)
        elif job.scene_type == SceneType.LAMBDA_GRAPH:
            return LambdaSceneFactory.create_interactive_exploration(data)
        else:
            # Fallback alla scene manager originale
            scene = self.scene_manager.create_scene(
                job.scene_type, job.job_id, job.config
            )
            if scene:
                scene.initialize_scene(data)
            return scene
    
    def _render_scene_frames(self, job: RenderJob, scene: Any) -> List[Dict[str, Any]]:
        """Renderizza i frame della scene."""
        if hasattr(scene, 'render_animation'):
            # Scene Manim-style
            return scene.render_animation(job.config.duration)
        elif hasattr(scene, 'render_frame'):
            # Scene manager style
            frames = []
            total_frames = int(job.config.fps * job.config.duration)
            
            for frame_num in range(total_frames):
                time_fraction = frame_num / max(1, total_frames - 1)
                frame = scene.render_frame(frame_num, time_fraction)
                frames.append({
                    "frame_number": frame_num,
                    "time": time_fraction * job.config.duration,
                    "data": frame
                })
            
            return frames
        else:
            raise ValueError(f"Scene type {type(scene)} non supportato")
    
    def _finalize_render(self, job: RenderJob, frames: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Finalizza il rendering."""
        result = {
            "job_id": job.job_id,
            "scene_type": job.scene_type.value,
            "quality": job.quality.value,
            "config": {
                "width": job.config.width,
                "height": job.config.height,
                "fps": job.config.fps,
                "duration": job.config.duration
            },
            "frames": frames,
            "metadata": {
                "total_frames": len(frames),
                "render_time": time.time() - job.created_at,
                "engine_version": "2.0.0",
                "gpu_accelerated": job.config.use_gpu_acceleration
            }
        }
        
        # Salva nei job completati
        with self.lock:
            self.completed_jobs[job.job_id] = result
        
        return result
    
    def _handle_job_completion(self, job: RenderJob, success: bool, result: Any):
        """Gestisce il completamento di un job."""
        if job.completion_callback:
            try:
                job.completion_callback(job.job_id, success, result)
            except Exception as e:
                logger.error(f"Errore nel callback di completamento: {str(e)}")
        
        logger.info(f"Job {job.job_id} {'completato' if success else 'fallito'}")
    
    def _monitoring_worker(self):
        """Worker per il monitoring del sistema."""
        logger.info("MonitoringWorker avviato")
        
        while not self.shutdown_event.is_set():
            try:
                # Aggiorna metriche
                self._update_system_metrics()
                
                # Cleanup job vecchi
                self._cleanup_old_jobs()
                
                # Log status periodico
                if self.metrics["total_jobs_processed"] % 10 == 0:
                    self._log_system_status()
                
                time.sleep(5.0)  # Aggiorna ogni 5 secondi
                
            except Exception as e:
                logger.error(f"Errore nel monitoring: {str(e)}")
                time.sleep(10.0)
        
        logger.info("MonitoringWorker terminato")
    
    def _update_system_metrics(self):
        """Aggiorna le metriche del sistema."""
        with self.lock:
            # GPU utilization (simulato)
            gpu_info = self.gpu_accelerator.get_device_info()
            if gpu_info.get("cuda_available"):
                self.metrics["gpu_utilization"] = 0.7  # Simulato
            
            # Memory usage (simulato)
            self.metrics["memory_usage"] = len(self.active_jobs) * 100  # MB per job
    
    def _cleanup_old_jobs(self):
        """Pulisce i job completati vecchi."""
        current_time = time.time()
        cleanup_threshold = 3600  # 1 ora
        
        with self.lock:
            to_remove = []
            for job_id, result in self.completed_jobs.items():
                if current_time - result["metadata"]["render_time"] > cleanup_threshold:
                    to_remove.append(job_id)
            
            for job_id in to_remove:
                del self.completed_jobs[job_id]
            
            if to_remove:
                logger.info(f"Puliti {len(to_remove)} job completati")
    
    def _log_system_status(self):
        """Log dello status del sistema."""
        with self.lock:
            active_count = len(self.active_jobs)
            queue_count = len(self.render_queue)
            completed_count = len(self.completed_jobs)
            
            logger.info(f"Status Engine {self.engine_id}: "
                       f"Active={active_count}, Queue={queue_count}, "
                       f"Completed={completed_count}, "
                       f"Success Rate={self._get_success_rate():.1%}")
    
    def _get_success_rate(self) -> float:
        """Calcola il tasso di successo."""
        total = self.metrics["total_jobs_processed"]
        if total == 0:
            return 1.0
        return self.metrics["successful_renders"] / total
    
    # API pubblica per gestione e monitoring
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Ottiene lo status di un job."""
        with self.lock:
            # Job attivo
            if job_id in self.active_jobs:
                job = self.active_jobs[job_id]
                return {
                    "job_id": job_id,
                    "status": "active",
                    "scene_type": job.scene_type.value,
                    "quality": job.quality.value,
                    "created_at": job.created_at
                }
            
            # Job completato
            if job_id in self.completed_jobs:
                return {
                    "job_id": job_id,
                    "status": "completed",
                    "result": self.completed_jobs[job_id]
                }
            
            # Job in coda
            for job in self.render_queue:
                if job.job_id == job_id:
                    return {
                        "job_id": job_id,
                        "status": "queued",
                        "position": self.render_queue.index(job),
                        "scene_type": job.scene_type.value
                    }
        
        return None
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancella un job."""
        with self.lock:
            # Rimuovi dalla coda
            for i, job in enumerate(self.render_queue):
                if job.job_id == job_id:
                    del self.render_queue[i]
                    logger.info(f"Job {job_id} rimosso dalla coda")
                    return True
            
            # Job attivo non può essere cancellato facilmente
            if job_id in self.active_jobs:
                logger.warning(f"Job {job_id} è attivo e non può essere cancellato")
                return False
        
        return False
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Ottiene le metriche del sistema."""
        with self.lock:
            return {
                "engine_id": self.engine_id,
                "state": self.state.value,
                "metrics": self.metrics.copy(),
                "active_jobs": len(self.active_jobs),
                "queued_jobs": len(self.render_queue),
                "completed_jobs": len(self.completed_jobs),
                "worker_threads": len(self.worker_threads),
                "gpu_info": self.gpu_accelerator.get_device_info()
            }
    
    def shutdown(self):
        """Spegne il motore in modo pulito."""
        logger.info(f"Spegnimento Engine {self.engine_id}...")
        
        self.state = EngineState.SHUTDOWN
        self.shutdown_event.set()
        
        # Attendi terminazione worker threads
        for thread in self.worker_threads:
            thread.join(timeout=5.0)
        
        # Cleanup risorse
        self.gpu_accelerator.cleanup()
        
        logger.info(f"Engine {self.engine_id} spento")


# Istanza globale del motore unificato
unified_engine = UnifiedEngine()

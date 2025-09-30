"""
Sistema di Scene Modulari per Lambda Visualizer
Ispirato all'architettura SwapTube per gestione scene avanzate.
"""

import abc
import logging
import threading
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class SceneType(Enum):
    """Tipi di scene supportate dal sistema."""
    LAMBDA_BASIC = "lambda_basic"
    LAMBDA_REDUCTION = "lambda_reduction"
    LAMBDA_GRAPH = "lambda_graph"
    LAMBDA_3D = "lambda_3d"
    TROMP_DIAGRAM = "tromp_diagram"
    ANIMATED_FLOW = "animated_flow"


@dataclass
class RenderConfig:
    """Configurazione per il rendering delle scene."""
    width: int = 1920
    height: int = 1080
    fps: int = 60
    duration: float = 10.0
    quality: str = "high"  # low, medium, high, ultra
    background_color: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    use_gpu_acceleration: bool = True
    antialiasing: bool = True
    motion_blur: bool = False


@dataclass
class StateQuery:
    """
    Query di stato per il controllo temporale delle animazioni.
    Ispirato al sistema StateQuery di SwapTube.
    """
    microblock_fraction: str
    title_opacity: str
    latex_opacity: str
    
    def __init__(self, microblock_fraction: str = "0", 
                 title_opacity: str = "0", 
                 latex_opacity: str = "0"):
        self.microblock_fraction = microblock_fraction
        self.title_opacity = title_opacity
        self.latex_opacity = latex_opacity


class SceneState(Enum):
    """Stati possibili di una scene."""
    INITIALIZING = "initializing"
    READY = "ready"
    RENDERING = "rendering"
    COMPLETED = "completed"
    ERROR = "error"


class BaseScene(abc.ABC):
    """
    Classe base per tutte le scene del sistema.
    Ispirata all'architettura modulare di SwapTube.
    """
    
    def __init__(self, scene_id: str, config: RenderConfig):
        self.scene_id = scene_id
        self.config = config
        self.state = SceneState.INITIALIZING
        self.progress = 0.0
        self.error_message: Optional[str] = None
        self.render_data: Optional[Dict[str, Any]] = None
        self.lock = threading.Lock()
        
        # Timing e controllo temporale
        self.current_time = 0.0
        self.total_duration = config.duration
        self.frame_count = int(config.fps * config.duration)
        
        logger.info(f"Inizializzata scene {scene_id} di tipo {self.__class__.__name__}")
    
    @abc.abstractmethod
    def populate_state_query(self) -> StateQuery:
        """
        Popola la query di stato per il controllo temporale.
        Deve essere implementato da ogni scene specifica.
        """
        pass
    
    @abc.abstractmethod
    def initialize_scene(self, lambda_data: Dict[str, Any]) -> bool:
        """
        Inizializza la scene con i dati lambda forniti.
        Ritorna True se l'inizializzazione è riuscita.
        """
        pass
    
    @abc.abstractmethod
    def render_frame(self, frame_number: int, time_fraction: float) -> np.ndarray:
        """
        Renderizza un singolo frame della scene.
        
        Args:
            frame_number: Numero del frame (0-based)
            time_fraction: Frazione temporale (0.0-1.0)
            
        Returns:
            Array numpy con i dati del frame (height, width, channels)
        """
        pass
    
    def update_progress(self, progress: float):
        """Aggiorna il progresso del rendering."""
        with self.lock:
            self.progress = max(0.0, min(1.0, progress))
    
    def set_error(self, error_message: str):
        """Imposta lo stato di errore."""
        with self.lock:
            self.state = SceneState.ERROR
            self.error_message = error_message
            logger.error(f"Errore nella scene {self.scene_id}: {error_message}")
    
    def get_status(self) -> Dict[str, Any]:
        """Ritorna lo status corrente della scene."""
        with self.lock:
            return {
                "scene_id": self.scene_id,
                "state": self.state.value,
                "progress": self.progress,
                "error_message": self.error_message,
                "current_time": self.current_time,
                "total_duration": self.total_duration
            }


class LambdaBasicScene(BaseScene):
    """
    Scene per visualizzazione base di espressioni lambda.
    Implementa diagrammi statici nello stile di Tromp.
    """
    
    def __init__(self, scene_id: str, config: RenderConfig):
        super().__init__(scene_id, config)
        self.lambda_expression = None
        self.nodes = []
        self.edges = []
        self.layout_computed = False
    
    def populate_state_query(self) -> StateQuery:
        """Popola la state query per la scene base."""
        return StateQuery(
            microblock_fraction="1.0",
            title_opacity="1.0",
            latex_opacity="1.0"
        )
    
    def initialize_scene(self, lambda_data: Dict[str, Any]) -> bool:
        """Inizializza la scene con i dati lambda."""
        try:
            self.lambda_expression = lambda_data.get("expression")
            self.nodes = lambda_data.get("structure", {}).get("nodes", [])
            self.edges = lambda_data.get("structure", {}).get("edges", [])
            
            if not self.lambda_expression:
                self.set_error("Espressione lambda mancante")
                return False
            
            # Calcola il layout dei nodi
            self._compute_layout()
            self.state = SceneState.READY
            return True
            
        except Exception as e:
            self.set_error(f"Errore nell'inizializzazione: {str(e)}")
            return False
    
    def _compute_layout(self):
        """Calcola il layout dei nodi usando algoritmi ispirati a Tromp."""
        if not self.nodes:
            return
        
        # Layout gerarchico per astrazioni lambda
        lambda_nodes = [n for n in self.nodes if n["type"] == "abstraction"]
        variable_nodes = [n for n in self.nodes if n["type"] == "variable"]
        application_nodes = [n for n in self.nodes if n["type"] == "application"]
        
        # Posizionamento orizzontale per lambda
        for i, node in enumerate(lambda_nodes):
            node["x"] = i * 2.0
            node["y"] = 0.0
        
        # Posizionamento verticale per variabili
        for i, node in enumerate(variable_nodes):
            node["x"] = i * 1.5 + 0.5
            node["y"] = -1.5
        
        # Posizionamento per applicazioni
        for i, node in enumerate(application_nodes):
            node["x"] = i * 1.0 + 1.0
            node["y"] = -0.75
        
        self.layout_computed = True
        logger.info(f"Layout calcolato per {len(self.nodes)} nodi")
    
    def render_frame(self, frame_number: int, time_fraction: float) -> np.ndarray:
        """Renderizza un frame della visualizzazione base."""
        # Crea un frame vuoto
        frame = np.zeros((self.config.height, self.config.width, 3), dtype=np.uint8)
        
        if not self.layout_computed:
            return frame
        
        # Simula il rendering dei nodi e collegamenti
        # In una implementazione reale, qui ci sarebbe il rendering grafico
        
        # Aggiorna il progresso
        self.update_progress(time_fraction)
        
        return frame


class LambdaReductionScene(BaseScene):
    """
    Scene per animazioni di riduzione beta.
    Mostra passo-passo le trasformazioni delle espressioni lambda.
    """
    
    def __init__(self, scene_id: str, config: RenderConfig):
        super().__init__(scene_id, config)
        self.reduction_steps = []
        self.current_step = 0
        self.step_duration = 2.0  # secondi per step
    
    def populate_state_query(self) -> StateQuery:
        """Popola la state query per animazioni di riduzione."""
        step_fraction = str(self.current_step / max(1, len(self.reduction_steps)))
        return StateQuery(
            microblock_fraction=step_fraction,
            title_opacity="1.0",
            latex_opacity="0.8"
        )
    
    def initialize_scene(self, lambda_data: Dict[str, Any]) -> bool:
        """Inizializza la scene con i passi di riduzione."""
        try:
            self.reduction_steps = lambda_data.get("reduction_steps", [])
            
            if not self.reduction_steps:
                self.set_error("Passi di riduzione mancanti")
                return False
            
            # Calcola la durata per step
            if len(self.reduction_steps) > 0:
                self.step_duration = self.total_duration / len(self.reduction_steps)
            
            self.state = SceneState.READY
            return True
            
        except Exception as e:
            self.set_error(f"Errore nell'inizializzazione riduzione: {str(e)}")
            return False
    
    def render_frame(self, frame_number: int, time_fraction: float) -> np.ndarray:
        """Renderizza un frame dell'animazione di riduzione."""
        frame = np.zeros((self.config.height, self.config.width, 3), dtype=np.uint8)
        
        if not self.reduction_steps:
            return frame
        
        # Calcola lo step corrente basato sul tempo
        current_time = time_fraction * self.total_duration
        self.current_step = min(
            int(current_time / self.step_duration),
            len(self.reduction_steps) - 1
        )
        
        # Simula il rendering dello step corrente
        # In una implementazione reale, qui ci sarebbe il rendering dell'animazione
        
        self.update_progress(time_fraction)
        return frame


class SceneManager:
    """
    Manager principale per la gestione delle scene.
    Coordina la creazione, esecuzione e monitoring delle scene.
    """
    
    def __init__(self):
        self.scenes: Dict[str, BaseScene] = {}
        self.scene_factories = {
            SceneType.LAMBDA_BASIC: LambdaBasicScene,
            SceneType.LAMBDA_REDUCTION: LambdaReductionScene,
            # Altri tipi di scene verranno aggiunti qui
        }
        self.active_renders: Dict[str, threading.Thread] = {}
        self.lock = threading.Lock()
        
        logger.info("SceneManager inizializzato")
    
    def create_scene(self, scene_type: SceneType, scene_id: str, 
                    config: RenderConfig) -> Optional[BaseScene]:
        """Crea una nuova scene del tipo specificato."""
        try:
            if scene_type not in self.scene_factories:
                logger.error(f"Tipo di scene non supportato: {scene_type}")
                return None
            
            scene_class = self.scene_factories[scene_type]
            scene = scene_class(scene_id, config)
            
            with self.lock:
                self.scenes[scene_id] = scene
            
            logger.info(f"Scene {scene_id} creata con successo")
            return scene
            
        except Exception as e:
            logger.error(f"Errore nella creazione scene {scene_id}: {str(e)}")
            return None
    
    def render_scene_async(self, scene_id: str, lambda_data: Dict[str, Any],
                          callback: Optional[callable] = None) -> bool:
        """Avvia il rendering di una scene in modo asincrono."""
        scene = self.scenes.get(scene_id)
        if not scene:
            logger.error(f"Scene {scene_id} non trovata")
            return False
        
        def render_worker():
            try:
                # Inizializza la scene
                if not scene.initialize_scene(lambda_data):
                    return
                
                scene.state = SceneState.RENDERING
                
                # Renderizza tutti i frame
                frames = []
                for frame_num in range(scene.frame_count):
                    time_fraction = frame_num / max(1, scene.frame_count - 1)
                    frame = scene.render_frame(frame_num, time_fraction)
                    frames.append(frame)
                
                # Salva i dati di rendering
                scene.render_data = {
                    "frames": frames,
                    "config": scene.config,
                    "metadata": {
                        "scene_type": scene.__class__.__name__,
                        "frame_count": len(frames),
                        "duration": scene.total_duration
                    }
                }
                
                scene.state = SceneState.COMPLETED
                logger.info(f"Rendering scene {scene_id} completato")
                
                if callback:
                    callback(scene_id, True, scene.render_data)
                    
            except Exception as e:
                scene.set_error(f"Errore durante il rendering: {str(e)}")
                if callback:
                    callback(scene_id, False, str(e))
        
        # Avvia il worker thread
        thread = threading.Thread(target=render_worker, daemon=True)
        thread.start()
        
        with self.lock:
            self.active_renders[scene_id] = thread
        
        return True
    
    def get_scene_status(self, scene_id: str) -> Optional[Dict[str, Any]]:
        """Ritorna lo status di una scene."""
        scene = self.scenes.get(scene_id)
        return scene.get_status() if scene else None
    
    def list_scenes(self) -> List[Dict[str, Any]]:
        """Lista tutte le scene attive."""
        with self.lock:
            return [scene.get_status() for scene in self.scenes.values()]
    
    def cleanup_completed_scenes(self):
        """Pulisce le scene completate per liberare memoria."""
        to_remove = []
        
        with self.lock:
            for scene_id, scene in self.scenes.items():
                if scene.state in [SceneState.COMPLETED, SceneState.ERROR]:
                    to_remove.append(scene_id)
        
        for scene_id in to_remove:
            self.remove_scene(scene_id)
        
        logger.info(f"Rimosse {len(to_remove)} scene completate")
    
    def remove_scene(self, scene_id: str) -> bool:
        """Rimuove una scene dal manager."""
        with self.lock:
            if scene_id in self.scenes:
                del self.scenes[scene_id]
            
            if scene_id in self.active_renders:
                # Non forziamo la terminazione del thread per sicurezza
                del self.active_renders[scene_id]
        
        logger.info(f"Scene {scene_id} rimossa")
        return True


# Istanza globale del scene manager
scene_manager = SceneManager()

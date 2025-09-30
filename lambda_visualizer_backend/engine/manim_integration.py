"""
Sistema di Animazioni Matematiche per Lambda Visualizer
Ispirato al framework Manim per animazioni matematiche professionali.
"""

import logging
import numpy as np
import math
import threading
import time
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import json

logger = logging.getLogger(__name__)

# Simulazione di Manim - in una implementazione reale si importerebbe Manim
try:
    # from manim import *
    MANIM_AVAILABLE = False  # Temporaneamente False per simulazione
    logger.info("Manim disponibile - animazioni professionali abilitate")
except ImportError:
    MANIM_AVAILABLE = False
    logger.warning("Manim non disponibile - usando sistema di animazione personalizzato")


class AnimationType(Enum):
    """Tipi di animazione supportati."""
    CREATE = "create"
    TRANSFORM = "transform"
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    MOVE_TO = "move_to"
    ROTATE = "rotate"
    SCALE = "scale"
    MORPH = "morph"
    HIGHLIGHT = "highlight"
    INDICATE = "indicate"


class EasingType(Enum):
    """Tipi di easing per le animazioni."""
    LINEAR = "linear"
    SMOOTH = "smooth"
    RUSH_INTO = "rush_into"
    RUSH_FROM = "rush_from"
    SLOW_INTO = "slow_into"
    DOUBLE_SMOOTH = "double_smooth"
    WIGGLE = "wiggle"
    THERE_AND_BACK = "there_and_back"


@dataclass
class Color:
    """Rappresentazione di un colore RGBA."""
    r: float = 1.0
    g: float = 1.0
    b: float = 1.0
    a: float = 1.0
    
    @classmethod
    def from_hex(cls, hex_color: str) -> 'Color':
        """Crea un colore da stringa esadecimale."""
        hex_color = hex_color.lstrip('#')
        return cls(
            r=int(hex_color[0:2], 16) / 255.0,
            g=int(hex_color[2:4], 16) / 255.0,
            b=int(hex_color[4:6], 16) / 255.0,
            a=1.0
        )
    
    def to_rgba_tuple(self) -> Tuple[float, float, float, float]:
        """Converte in tupla RGBA."""
        return (self.r, self.g, self.b, self.a)


# Colori predefiniti (stile Manim)
class Colors:
    WHITE = Color(1.0, 1.0, 1.0, 1.0)
    BLACK = Color(0.0, 0.0, 0.0, 1.0)
    RED = Color(0.93, 0.26, 0.24, 1.0)
    GREEN = Color(0.18, 0.8, 0.44, 1.0)
    BLUE = Color(0.20, 0.60, 0.86, 1.0)
    YELLOW = Color(1.0, 0.84, 0.0, 1.0)
    PURPLE = Color(0.68, 0.51, 0.79, 1.0)
    ORANGE = Color(1.0, 0.65, 0.0, 1.0)
    PINK = Color(1.0, 0.75, 0.8, 1.0)
    GRAY = Color(0.5, 0.5, 0.5, 1.0)
    
    # Colori specifici per lambda calculus
    LAMBDA_RED = Color(0.9, 0.2, 0.2, 1.0)      # Astrazioni lambda
    VARIABLE_GREEN = Color(0.2, 0.8, 0.3, 1.0)   # Variabili
    APPLICATION_BLUE = Color(0.3, 0.5, 0.9, 1.0) # Applicazioni
    BOUND_GRAY = Color(0.6, 0.6, 0.6, 1.0)       # Variabili bound


@dataclass
class Point3D:
    """Punto nello spazio 3D."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __add__(self, other: 'Point3D') -> 'Point3D':
        return Point3D(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other: 'Point3D') -> 'Point3D':
        return Point3D(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar: float) -> 'Point3D':
        return Point3D(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def distance_to(self, other: 'Point3D') -> float:
        """Calcola la distanza euclidea."""
        dx, dy, dz = self.x - other.x, self.y - other.y, self.z - other.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def normalize(self) -> 'Point3D':
        """Normalizza il vettore."""
        length = math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)
        if length > 0:
            return Point3D(self.x/length, self.y/length, self.z/length)
        return Point3D()


class Mobject(ABC):
    """
    Classe base per tutti gli oggetti matematici mobili.
    Ispirata al sistema Mobject di Manim.
    """
    
    def __init__(self, **kwargs):
        self.position = Point3D()
        self.rotation = Point3D()
        self.scale_factor = Point3D(1.0, 1.0, 1.0)
        self.color = kwargs.get('color', Colors.WHITE)
        self.opacity = kwargs.get('opacity', 1.0)
        self.stroke_width = kwargs.get('stroke_width', 2.0)
        self.fill_opacity = kwargs.get('fill_opacity', 0.0)
        
        # Proprietà per animazioni
        self.is_visible = True
        self.animation_data = {}
        
        # Gerarchia di oggetti
        self.parent: Optional['Mobject'] = None
        self.children: List['Mobject'] = []
        
        # Dati geometrici
        self.points: List[Point3D] = []
        self.update_points()
    
    @abstractmethod
    def update_points(self):
        """Aggiorna i punti geometrici dell'oggetto."""
        pass
    
    def move_to(self, point: Point3D) -> 'Mobject':
        """Sposta l'oggetto a una posizione."""
        self.position = point
        return self
    
    def shift(self, vector: Point3D) -> 'Mobject':
        """Sposta l'oggetto di un vettore."""
        self.position = self.position + vector
        return self
    
    def rotate(self, angle: float, axis: Point3D = Point3D(0, 0, 1)) -> 'Mobject':
        """Ruota l'oggetto."""
        # Semplificazione - in una implementazione reale userebbe quaternioni
        if axis.z != 0:
            self.rotation.z += angle
        elif axis.y != 0:
            self.rotation.y += angle
        elif axis.x != 0:
            self.rotation.x += angle
        return self
    
    def scale(self, factor: float) -> 'Mobject':
        """Scala l'oggetto."""
        self.scale_factor = self.scale_factor * factor
        return self
    
    def set_color(self, color: Color) -> 'Mobject':
        """Imposta il colore."""
        self.color = color
        return self
    
    def set_opacity(self, opacity: float) -> 'Mobject':
        """Imposta l'opacità."""
        self.opacity = max(0.0, min(1.0, opacity))
        return self
    
    def add_child(self, child: 'Mobject'):
        """Aggiunge un oggetto figlio."""
        child.parent = self
        self.children.append(child)
    
    def get_center(self) -> Point3D:
        """Ottiene il centro dell'oggetto."""
        if not self.points:
            return self.position
        
        center_x = sum(p.x for p in self.points) / len(self.points)
        center_y = sum(p.y for p in self.points) / len(self.points)
        center_z = sum(p.z for p in self.points) / len(self.points)
        
        return Point3D(center_x, center_y, center_z)
    
    def copy(self) -> 'Mobject':
        """Crea una copia dell'oggetto."""
        # Implementazione semplificata
        new_obj = self.__class__()
        new_obj.position = Point3D(self.position.x, self.position.y, self.position.z)
        new_obj.rotation = Point3D(self.rotation.x, self.rotation.y, self.rotation.z)
        new_obj.scale_factor = Point3D(self.scale_factor.x, self.scale_factor.y, self.scale_factor.z)
        new_obj.color = self.color
        new_obj.opacity = self.opacity
        return new_obj


class Circle(Mobject):
    """Cerchio matematico."""
    
    def __init__(self, radius: float = 1.0, **kwargs):
        self.radius = radius
        super().__init__(**kwargs)
    
    def update_points(self):
        """Genera i punti del cerchio."""
        self.points = []
        num_points = 64
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            x = self.radius * math.cos(angle)
            y = self.radius * math.sin(angle)
            self.points.append(Point3D(x, y, 0))


class Rectangle(Mobject):
    """Rettangolo matematico."""
    
    def __init__(self, width: float = 2.0, height: float = 1.0, **kwargs):
        self.width = width
        self.height = height
        super().__init__(**kwargs)
    
    def update_points(self):
        """Genera i punti del rettangolo."""
        w, h = self.width / 2, self.height / 2
        self.points = [
            Point3D(-w, -h, 0),
            Point3D(w, -h, 0),
            Point3D(w, h, 0),
            Point3D(-w, h, 0),
            Point3D(-w, -h, 0)  # Chiude il rettangolo
        ]


class Text(Mobject):
    """Testo matematico."""
    
    def __init__(self, text: str, font_size: float = 48, **kwargs):
        self.text = text
        self.font_size = font_size
        super().__init__(**kwargs)
    
    def update_points(self):
        """Genera i punti del testo (semplificato)."""
        # In una implementazione reale, questo userebbe un engine di rendering testo
        self.points = [Point3D(0, 0, 0)]  # Punto di ancoraggio


class LambdaNode(Mobject):
    """Nodo specifico per espressioni lambda."""
    
    def __init__(self, node_type: str, label: str, **kwargs):
        self.node_type = node_type  # "abstraction", "variable", "application"
        self.label = label
        self.connections: List['LambdaNode'] = []
        
        # Colori specifici per tipo
        color_map = {
            "abstraction": Colors.LAMBDA_RED,
            "variable": Colors.VARIABLE_GREEN,
            "application": Colors.APPLICATION_BLUE
        }
        kwargs.setdefault('color', color_map.get(node_type, Colors.WHITE))
        
        super().__init__(**kwargs)
    
    def update_points(self):
        """Genera i punti del nodo lambda."""
        if self.node_type == "abstraction":
            # Forma lambda (triangolare)
            self.points = [
                Point3D(-0.5, -0.5, 0),
                Point3D(0.5, -0.5, 0),
                Point3D(0, 0.5, 0),
                Point3D(-0.5, -0.5, 0)
            ]
        elif self.node_type == "variable":
            # Cerchio per variabili
            num_points = 32
            radius = 0.3
            self.points = []
            for i in range(num_points):
                angle = 2 * math.pi * i / num_points
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                self.points.append(Point3D(x, y, 0))
        else:  # application
            # Quadrato per applicazioni
            self.points = [
                Point3D(-0.4, -0.4, 0),
                Point3D(0.4, -0.4, 0),
                Point3D(0.4, 0.4, 0),
                Point3D(-0.4, 0.4, 0),
                Point3D(-0.4, -0.4, 0)
            ]
    
    def connect_to(self, other: 'LambdaNode'):
        """Crea una connessione a un altro nodo."""
        if other not in self.connections:
            self.connections.append(other)


class LambdaConnection(Mobject):
    """Connessione tra nodi lambda."""
    
    def __init__(self, start_node: LambdaNode, end_node: LambdaNode, **kwargs):
        self.start_node = start_node
        self.end_node = end_node
        kwargs.setdefault('color', Colors.GRAY)
        super().__init__(**kwargs)
    
    def update_points(self):
        """Aggiorna i punti della connessione."""
        start_pos = self.start_node.position
        end_pos = self.end_node.position
        
        # Linea semplice
        self.points = [start_pos, end_pos]


@dataclass
class Animation:
    """Definizione di un'animazione."""
    mobject: Mobject
    animation_type: AnimationType
    duration: float = 1.0
    easing: EasingType = EasingType.SMOOTH
    start_time: float = 0.0
    parameters: Dict[str, Any] = field(default_factory=dict)


class AnimationEngine:
    """
    Engine per l'esecuzione delle animazioni.
    Ispirato al sistema di animazione di Manim.
    """
    
    def __init__(self, fps: int = 60):
        self.fps = fps
        self.frame_duration = 1.0 / fps
        self.animations: List[Animation] = []
        self.mobjects: List[Mobject] = []
        self.current_time = 0.0
        
        # Funzioni di easing
        self.easing_functions = {
            EasingType.LINEAR: self._linear,
            EasingType.SMOOTH: self._smooth,
            EasingType.RUSH_INTO: self._rush_into,
            EasingType.RUSH_FROM: self._rush_from,
            EasingType.SLOW_INTO: self._slow_into,
            EasingType.DOUBLE_SMOOTH: self._double_smooth,
            EasingType.WIGGLE: self._wiggle,
            EasingType.THERE_AND_BACK: self._there_and_back
        }
        
        logger.info(f"AnimationEngine inizializzato con {fps} fps")
    
    def add_mobject(self, mobject: Mobject):
        """Aggiunge un mobject alla scena."""
        if mobject not in self.mobjects:
            self.mobjects.append(mobject)
    
    def remove_mobject(self, mobject: Mobject):
        """Rimuove un mobject dalla scena."""
        if mobject in self.mobjects:
            self.mobjects.remove(mobject)
    
    def play(self, *animations: Animation):
        """Esegue una o più animazioni."""
        for animation in animations:
            self.animations.append(animation)
            # Assicurati che il mobject sia nella scena
            self.add_mobject(animation.mobject)
        
        # Ordina le animazioni per tempo di inizio
        self.animations.sort(key=lambda a: a.start_time)
    
    def create_animation(self, mobject: Mobject, animation_type: AnimationType,
                        duration: float = 1.0, **kwargs) -> Animation:
        """Crea un'animazione."""
        return Animation(
            mobject=mobject,
            animation_type=animation_type,
            duration=duration,
            easing=kwargs.get('easing', EasingType.SMOOTH),
            start_time=kwargs.get('start_time', self.current_time),
            parameters=kwargs.get('parameters', {})
        )
    
    def render_frame(self, time: float) -> Dict[str, Any]:
        """Renderizza un frame a un tempo specifico."""
        self.current_time = time
        
        # Aggiorna tutte le animazioni attive
        for animation in self.animations:
            if (animation.start_time <= time <= 
                animation.start_time + animation.duration):
                self._update_animation(animation, time)
        
        # Genera i dati del frame
        frame_data = {
            "time": time,
            "mobjects": []
        }
        
        for mobject in self.mobjects:
            if mobject.is_visible:
                mobject_data = {
                    "type": mobject.__class__.__name__,
                    "position": [mobject.position.x, mobject.position.y, mobject.position.z],
                    "rotation": [mobject.rotation.x, mobject.rotation.y, mobject.rotation.z],
                    "scale": [mobject.scale_factor.x, mobject.scale_factor.y, mobject.scale_factor.z],
                    "color": mobject.color.to_rgba_tuple(),
                    "opacity": mobject.opacity,
                    "points": [[p.x, p.y, p.z] for p in mobject.points]
                }
                
                # Dati specifici per nodi lambda
                if isinstance(mobject, LambdaNode):
                    mobject_data.update({
                        "node_type": mobject.node_type,
                        "label": mobject.label,
                        "connections": [id(conn) for conn in mobject.connections]
                    })
                
                frame_data["mobjects"].append(mobject_data)
        
        return frame_data
    
    def _update_animation(self, animation: Animation, current_time: float):
        """Aggiorna un'animazione specifica."""
        # Calcola il progresso dell'animazione (0.0 - 1.0)
        elapsed = current_time - animation.start_time
        progress = min(1.0, elapsed / animation.duration)
        
        # Applica easing
        eased_progress = self._apply_easing(progress, animation.easing)
        
        # Applica l'animazione specifica
        if animation.animation_type == AnimationType.FADE_IN:
            animation.mobject.opacity = eased_progress
        
        elif animation.animation_type == AnimationType.FADE_OUT:
            animation.mobject.opacity = 1.0 - eased_progress
        
        elif animation.animation_type == AnimationType.MOVE_TO:
            target = animation.parameters.get('target', Point3D())
            start = animation.parameters.get('start', animation.mobject.position)
            
            new_pos = Point3D(
                start.x + (target.x - start.x) * eased_progress,
                start.y + (target.y - start.y) * eased_progress,
                start.z + (target.z - start.z) * eased_progress
            )
            animation.mobject.position = new_pos
        
        elif animation.animation_type == AnimationType.SCALE:
            target_scale = animation.parameters.get('target_scale', 1.0)
            start_scale = animation.parameters.get('start_scale', 1.0)
            
            current_scale = start_scale + (target_scale - start_scale) * eased_progress
            animation.mobject.scale_factor = Point3D(current_scale, current_scale, current_scale)
        
        elif animation.animation_type == AnimationType.ROTATE:
            target_angle = animation.parameters.get('angle', 0.0)
            axis = animation.parameters.get('axis', Point3D(0, 0, 1))
            
            current_angle = target_angle * eased_progress
            if axis.z != 0:
                animation.mobject.rotation.z = current_angle
        
        elif animation.animation_type == AnimationType.TRANSFORM:
            # Trasformazione complessa tra due mobjects
            target_mobject = animation.parameters.get('target')
            if target_mobject:
                self._interpolate_mobjects(animation.mobject, target_mobject, eased_progress)
        
        # Aggiorna i punti geometrici
        animation.mobject.update_points()
    
    def _interpolate_mobjects(self, source: Mobject, target: Mobject, progress: float):
        """Interpola tra due mobjects."""
        # Interpola posizione
        source.position = Point3D(
            source.position.x + (target.position.x - source.position.x) * progress,
            source.position.y + (target.position.y - source.position.y) * progress,
            source.position.z + (target.position.z - source.position.z) * progress
        )
        
        # Interpola colore
        source.color = Color(
            source.color.r + (target.color.r - source.color.r) * progress,
            source.color.g + (target.color.g - source.color.g) * progress,
            source.color.b + (target.color.b - source.color.b) * progress,
            source.color.a + (target.color.a - source.color.a) * progress
        )
        
        # Interpola opacità
        source.opacity = source.opacity + (target.opacity - source.opacity) * progress
    
    def _apply_easing(self, t: float, easing_type: EasingType) -> float:
        """Applica una funzione di easing."""
        return self.easing_functions[easing_type](t)
    
    # Funzioni di easing (ispirate a Manim)
    def _linear(self, t: float) -> float:
        return t
    
    def _smooth(self, t: float) -> float:
        return t * t * (3 - 2 * t)
    
    def _rush_into(self, t: float) -> float:
        return 2 * t * t if t < 0.5 else 1
    
    def _rush_from(self, t: float) -> float:
        return 0 if t < 0.5 else 2 * (t - 0.5) * (t - 0.5)
    
    def _slow_into(self, t: float) -> float:
        return t * t
    
    def _double_smooth(self, t: float) -> float:
        if t < 0.5:
            return 2 * t * t
        else:
            return 1 - 2 * (1 - t) * (1 - t)
    
    def _wiggle(self, t: float) -> float:
        return t + 0.1 * math.sin(8 * math.pi * t) * (1 - t)
    
    def _there_and_back(self, t: float) -> float:
        return 2 * t * (1 - t)


class LambdaScene:
    """
    Scene specifica per visualizzazioni lambda calculus.
    Combina Mobjects e AnimationEngine per creare visualizzazioni complesse.
    """
    
    def __init__(self, width: int = 1920, height: int = 1080, fps: int = 60):
        self.width = width
        self.height = height
        self.animation_engine = AnimationEngine(fps)
        self.lambda_nodes: Dict[str, LambdaNode] = {}
        self.connections: List[LambdaConnection] = []
        
        logger.info(f"LambdaScene inizializzata: {width}x{height} @ {fps}fps")
    
    def create_lambda_expression(self, expression_data: Dict[str, Any]) -> List[Mobject]:
        """Crea la visualizzazione di un'espressione lambda."""
        nodes = expression_data.get("structure", {}).get("nodes", [])
        edges = expression_data.get("structure", {}).get("edges", [])
        
        created_objects = []
        
        # Crea i nodi
        for node in nodes:
            lambda_node = LambdaNode(
                node_type=node.get("type", "variable"),
                label=node.get("label", ""),
                color=self._get_node_color(node.get("type", "variable"))
            )
            
            # Posiziona il nodo
            lambda_node.position = Point3D(
                node.get("x", 0.0),
                node.get("y", 0.0),
                0.0
            )
            
            self.lambda_nodes[node.get("id", str(len(self.lambda_nodes)))] = lambda_node
            self.animation_engine.add_mobject(lambda_node)
            created_objects.append(lambda_node)
        
        # Crea le connessioni
        for edge in edges:
            source_id = edge.get("source")
            target_id = edge.get("target")
            
            if source_id in self.lambda_nodes and target_id in self.lambda_nodes:
                connection = LambdaConnection(
                    self.lambda_nodes[source_id],
                    self.lambda_nodes[target_id]
                )
                
                self.connections.append(connection)
                self.animation_engine.add_mobject(connection)
                created_objects.append(connection)
        
        return created_objects
    
    def animate_beta_reduction(self, reduction_steps: List[Dict[str, Any]], 
                             step_duration: float = 2.0) -> List[Animation]:
        """Crea animazioni per i passi di riduzione beta."""
        animations = []
        current_time = 0.0
        
        for i, step in enumerate(reduction_steps):
            step_animations = self._create_reduction_step_animation(
                step, current_time, step_duration
            )
            animations.extend(step_animations)
            current_time += step_duration
        
        return animations
    
    def _create_reduction_step_animation(self, step: Dict[str, Any], 
                                       start_time: float, duration: float) -> List[Animation]:
        """Crea animazioni per un singolo passo di riduzione."""
        animations = []
        
        # Evidenzia il redex (espressione da ridurre)
        redex_nodes = step.get("redex_nodes", [])
        for node_id in redex_nodes:
            if node_id in self.lambda_nodes:
                node = self.lambda_nodes[node_id]
                
                # Animazione di highlight
                highlight_anim = self.animation_engine.create_animation(
                    node, AnimationType.SCALE,
                    duration=duration * 0.3,
                    start_time=start_time,
                    parameters={
                        'target_scale': 1.2,
                        'start_scale': 1.0
                    }
                )
                animations.append(highlight_anim)
                
                # Cambia colore temporaneamente
                original_color = node.color
                node.color = Colors.YELLOW
                
                # Ripristina colore e scala
                restore_anim = self.animation_engine.create_animation(
                    node, AnimationType.SCALE,
                    duration=duration * 0.3,
                    start_time=start_time + duration * 0.7,
                    parameters={
                        'target_scale': 1.0,
                        'start_scale': 1.2
                    }
                )
                animations.append(restore_anim)
        
        # Animazione di trasformazione
        if "new_structure" in step:
            transform_anim = self._create_structure_transform_animation(
                step["new_structure"], start_time + duration * 0.5, duration * 0.5
            )
            animations.extend(transform_anim)
        
        return animations
    
    def _create_structure_transform_animation(self, new_structure: Dict[str, Any],
                                            start_time: float, duration: float) -> List[Animation]:
        """Crea animazioni per la trasformazione della struttura."""
        animations = []
        
        # In una implementazione reale, questo gestirebbe la trasformazione
        # completa della struttura del grafo
        
        return animations
    
    def _get_node_color(self, node_type: str) -> Color:
        """Ottiene il colore appropriato per un tipo di nodo."""
        color_map = {
            "abstraction": Colors.LAMBDA_RED,
            "variable": Colors.VARIABLE_GREEN,
            "application": Colors.APPLICATION_BLUE,
            "bound": Colors.BOUND_GRAY
        }
        return color_map.get(node_type, Colors.WHITE)
    
    def render_animation(self, duration: float, output_path: str = None) -> List[Dict[str, Any]]:
        """Renderizza l'intera animazione."""
        frames = []
        total_frames = int(duration * self.animation_engine.fps)
        
        for frame_num in range(total_frames):
            time = frame_num / self.animation_engine.fps
            frame_data = self.animation_engine.render_frame(time)
            frames.append(frame_data)
        
        logger.info(f"Renderizzati {len(frames)} frame per animazione di {duration}s")
        
        if output_path:
            self._save_animation_data(frames, output_path)
        
        return frames
    
    def _save_animation_data(self, frames: List[Dict[str, Any]], output_path: str):
        """Salva i dati dell'animazione su file."""
        animation_data = {
            "metadata": {
                "width": self.width,
                "height": self.height,
                "fps": self.animation_engine.fps,
                "total_frames": len(frames),
                "duration": len(frames) / self.animation_engine.fps
            },
            "frames": frames
        }
        
        try:
            with open(output_path, 'w') as f:
                json.dump(animation_data, f, indent=2)
            logger.info(f"Dati animazione salvati in {output_path}")
        except Exception as e:
            logger.error(f"Errore nel salvataggio animazione: {str(e)}")


# Factory per creare scene lambda predefinite
class LambdaSceneFactory:
    """Factory per creare scene lambda predefinite."""
    
    @staticmethod
    def create_basic_visualization(expression_data: Dict[str, Any]) -> LambdaScene:
        """Crea una visualizzazione base."""
        scene = LambdaScene()
        scene.create_lambda_expression(expression_data)
        return scene
    
    @staticmethod
    def create_reduction_animation(expression_data: Dict[str, Any],
                                 reduction_steps: List[Dict[str, Any]]) -> LambdaScene:
        """Crea un'animazione di riduzione."""
        scene = LambdaScene()
        scene.create_lambda_expression(expression_data)
        
        # Crea e esegue le animazioni di riduzione
        animations = scene.animate_beta_reduction(reduction_steps)
        for animation in animations:
            scene.animation_engine.play(animation)
        
        return scene
    
    @staticmethod
    def create_interactive_exploration(expression_data: Dict[str, Any]) -> LambdaScene:
        """Crea una visualizzazione interattiva."""
        scene = LambdaScene()
        objects = scene.create_lambda_expression(expression_data)
        
        # Aggiungi animazioni di introduzione
        for i, obj in enumerate(objects):
            fade_in = scene.animation_engine.create_animation(
                obj, AnimationType.FADE_IN,
                duration=1.0,
                start_time=i * 0.2
            )
            scene.animation_engine.play(fade_in)
        
        return scene

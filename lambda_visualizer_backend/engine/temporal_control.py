"""
Sistema di Controllo Temporale per Lambda Visualizer
Ispirato al sistema di macroblocks e microblocks di SwapTube.
"""

import logging
import math
import threading
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class TimeUnit(Enum):
    """Unità temporali del sistema."""
    MACROBLOCK = "macroblock"  # Unità atomiche di audio (es. 1024 samples)
    MICROBLOCK = "microblock"  # Unità atomiche di trasformazioni visive
    FRAME = "frame"            # Singoli frame video
    SECOND = "second"          # Tempo reale in secondi


@dataclass
class TemporalEvent:
    """Evento temporale nel sistema."""
    timestamp: float           # Timestamp in secondi
    event_type: str           # Tipo di evento
    data: Dict[str, Any]      # Dati dell'evento
    duration: float = 0.0     # Durata dell'evento
    priority: int = 0         # Priorità (0 = massima)


@dataclass
class AnimationKeyframe:
    """Keyframe per animazioni temporali."""
    time: float               # Tempo del keyframe (0.0-1.0)
    value: Any               # Valore al keyframe
    interpolation: str = "linear"  # Tipo di interpolazione
    easing: str = "ease"     # Funzione di easing


class InterpolationType(Enum):
    """Tipi di interpolazione supportati."""
    LINEAR = "linear"
    CUBIC = "cubic"
    BEZIER = "bezier"
    STEP = "step"


class EasingFunction(Enum):
    """Funzioni di easing supportate."""
    EASE = "ease"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    BOUNCE = "bounce"
    ELASTIC = "elastic"


class TemporalController:
    """
    Controller principale per la gestione temporale.
    Gestisce timeline, eventi e sincronizzazione.
    """
    
    def __init__(self, fps: int = 60, audio_sample_rate: int = 44100):
        self.fps = fps
        self.audio_sample_rate = audio_sample_rate
        self.frame_duration = 1.0 / fps
        
        # Calcolo dimensioni blocchi (ispirato a SwapTube)
        self.macroblock_size = 1024  # samples audio per macroblock
        self.macroblock_duration = self.macroblock_size / audio_sample_rate
        self.microblock_size = 16    # frame per microblock
        self.microblock_duration = self.microblock_size * self.frame_duration
        
        # Timeline e eventi
        self.events: List[TemporalEvent] = []
        self.current_time = 0.0
        self.total_duration = 0.0
        self.is_playing = False
        self.lock = threading.Lock()
        
        # Callbacks per eventi temporali
        self.event_callbacks: Dict[str, List[Callable]] = {}
        
        logger.info(f"TemporalController inizializzato: {fps}fps, "
                   f"macroblock={self.macroblock_duration:.3f}s, "
                   f"microblock={self.microblock_duration:.3f}s")
    
    def add_event(self, event: TemporalEvent):
        """Aggiunge un evento alla timeline."""
        with self.lock:
            self.events.append(event)
            self.events.sort(key=lambda e: (e.timestamp, e.priority))
            self.total_duration = max(self.total_duration, 
                                    event.timestamp + event.duration)
        
        logger.debug(f"Aggiunto evento {event.event_type} a t={event.timestamp:.3f}s")
    
    def register_callback(self, event_type: str, callback: Callable):
        """Registra un callback per un tipo di evento."""
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []
        self.event_callbacks[event_type].append(callback)
    
    def get_current_macroblock(self) -> int:
        """Ritorna il macroblock corrente."""
        return int(self.current_time / self.macroblock_duration)
    
    def get_current_microblock(self) -> int:
        """Ritorna il microblock corrente."""
        return int(self.current_time / self.microblock_duration)
    
    def get_current_frame(self) -> int:
        """Ritorna il frame corrente."""
        return int(self.current_time * self.fps)
    
    def get_macroblock_fraction(self) -> float:
        """Ritorna la frazione del macroblock corrente (0.0-1.0)."""
        macroblock_time = self.current_time % self.macroblock_duration
        return macroblock_time / self.macroblock_duration
    
    def get_microblock_fraction(self) -> float:
        """Ritorna la frazione del microblock corrente (0.0-1.0)."""
        microblock_time = self.current_time % self.microblock_duration
        return microblock_time / self.microblock_duration
    
    def seek_to_time(self, time: float):
        """Salta a un tempo specifico."""
        with self.lock:
            self.current_time = max(0.0, min(time, self.total_duration))
        
        # Trigger eventi al tempo corrente
        self._trigger_events_at_time(self.current_time)
    
    def seek_to_macroblock(self, macroblock: int):
        """Salta a un macroblock specifico."""
        target_time = macroblock * self.macroblock_duration
        self.seek_to_time(target_time)
    
    def seek_to_microblock(self, microblock: int):
        """Salta a un microblock specifico."""
        target_time = microblock * self.microblock_duration
        self.seek_to_time(target_time)
    
    def advance_frame(self):
        """Avanza di un frame."""
        with self.lock:
            old_time = self.current_time
            self.current_time = min(self.current_time + self.frame_duration,
                                  self.total_duration)
        
        # Trigger eventi nell'intervallo temporale
        self._trigger_events_in_range(old_time, self.current_time)
    
    def _trigger_events_at_time(self, time: float):
        """Trigger eventi a un tempo specifico."""
        for event in self.events:
            if abs(event.timestamp - time) < self.frame_duration / 2:
                self._execute_event(event)
    
    def _trigger_events_in_range(self, start_time: float, end_time: float):
        """Trigger eventi in un range temporale."""
        for event in self.events:
            if start_time <= event.timestamp <= end_time:
                self._execute_event(event)
    
    def _execute_event(self, event: TemporalEvent):
        """Esegue un evento temporale."""
        callbacks = self.event_callbacks.get(event.event_type, [])
        for callback in callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Errore nell'esecuzione callback per evento "
                           f"{event.event_type}: {str(e)}")


class AnimationTimeline:
    """
    Timeline per animazioni con keyframes e interpolazione.
    Supporta animazioni complesse con easing e interpolazione.
    """
    
    def __init__(self, duration: float):
        self.duration = duration
        self.keyframes: Dict[str, List[AnimationKeyframe]] = {}
        self.interpolators = {
            InterpolationType.LINEAR: self._linear_interpolation,
            InterpolationType.CUBIC: self._cubic_interpolation,
            InterpolationType.BEZIER: self._bezier_interpolation,
            InterpolationType.STEP: self._step_interpolation
        }
        self.easing_functions = {
            EasingFunction.EASE: self._ease,
            EasingFunction.EASE_IN: self._ease_in,
            EasingFunction.EASE_OUT: self._ease_out,
            EasingFunction.EASE_IN_OUT: self._ease_in_out,
            EasingFunction.BOUNCE: self._bounce,
            EasingFunction.ELASTIC: self._elastic
        }
    
    def add_keyframe(self, property_name: str, keyframe: AnimationKeyframe):
        """Aggiunge un keyframe per una proprietà."""
        if property_name not in self.keyframes:
            self.keyframes[property_name] = []
        
        self.keyframes[property_name].append(keyframe)
        self.keyframes[property_name].sort(key=lambda k: k.time)
    
    def get_value_at_time(self, property_name: str, time: float) -> Any:
        """Ottiene il valore di una proprietà a un tempo specifico."""
        if property_name not in self.keyframes:
            return None
        
        keyframes = self.keyframes[property_name]
        if not keyframes:
            return None
        
        # Normalizza il tempo (0.0-1.0)
        normalized_time = max(0.0, min(1.0, time / self.duration))
        
        # Trova i keyframes adiacenti
        if normalized_time <= keyframes[0].time:
            return keyframes[0].value
        
        if normalized_time >= keyframes[-1].time:
            return keyframes[-1].value
        
        # Trova i keyframes per interpolazione
        for i in range(len(keyframes) - 1):
            if keyframes[i].time <= normalized_time <= keyframes[i + 1].time:
                return self._interpolate_between_keyframes(
                    keyframes[i], keyframes[i + 1], normalized_time
                )
        
        return keyframes[-1].value
    
    def _interpolate_between_keyframes(self, kf1: AnimationKeyframe, 
                                     kf2: AnimationKeyframe, time: float) -> Any:
        """Interpola tra due keyframes."""
        # Calcola la frazione locale tra i keyframes
        if kf2.time == kf1.time:
            local_fraction = 0.0
        else:
            local_fraction = (time - kf1.time) / (kf2.time - kf1.time)
        
        # Applica easing
        eased_fraction = self._apply_easing(local_fraction, kf1.easing)
        
        # Applica interpolazione
        interpolation_type = InterpolationType(kf1.interpolation)
        interpolator = self.interpolators[interpolation_type]
        
        return interpolator(kf1.value, kf2.value, eased_fraction)
    
    def _apply_easing(self, t: float, easing: str) -> float:
        """Applica una funzione di easing."""
        easing_func = EasingFunction(easing)
        return self.easing_functions[easing_func](t)
    
    # Funzioni di interpolazione
    def _linear_interpolation(self, start: Any, end: Any, t: float) -> Any:
        """Interpolazione lineare."""
        if isinstance(start, (int, float)) and isinstance(end, (int, float)):
            return start + (end - start) * t
        elif isinstance(start, np.ndarray) and isinstance(end, np.ndarray):
            return start + (end - start) * t
        else:
            return start if t < 0.5 else end
    
    def _cubic_interpolation(self, start: Any, end: Any, t: float) -> Any:
        """Interpolazione cubica."""
        # Semplificata - in una implementazione reale userebbe spline cubiche
        cubic_t = t * t * (3.0 - 2.0 * t)
        return self._linear_interpolation(start, end, cubic_t)
    
    def _bezier_interpolation(self, start: Any, end: Any, t: float) -> Any:
        """Interpolazione Bezier cubica."""
        # Curve di Bezier con punti di controllo predefiniti
        p1, p2 = 0.25, 0.75  # Punti di controllo
        bezier_t = 3 * (1 - t) * (1 - t) * t * p1 + 3 * (1 - t) * t * t * p2 + t * t * t
        return self._linear_interpolation(start, end, bezier_t)
    
    def _step_interpolation(self, start: Any, end: Any, t: float) -> Any:
        """Interpolazione a gradini."""
        return start if t < 1.0 else end
    
    # Funzioni di easing
    def _ease(self, t: float) -> float:
        """Easing standard."""
        return t * t * (3.0 - 2.0 * t)
    
    def _ease_in(self, t: float) -> float:
        """Ease in (accelerazione)."""
        return t * t
    
    def _ease_out(self, t: float) -> float:
        """Ease out (decelerazione)."""
        return 1.0 - (1.0 - t) * (1.0 - t)
    
    def _ease_in_out(self, t: float) -> float:
        """Ease in-out (accelerazione + decelerazione)."""
        if t < 0.5:
            return 2.0 * t * t
        else:
            return 1.0 - 2.0 * (1.0 - t) * (1.0 - t)
    
    def _bounce(self, t: float) -> float:
        """Effetto bounce."""
        if t < 1.0 / 2.75:
            return 7.5625 * t * t
        elif t < 2.0 / 2.75:
            t -= 1.5 / 2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5 / 2.75:
            t -= 2.25 / 2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625 / 2.75
            return 7.5625 * t * t + 0.984375
    
    def _elastic(self, t: float) -> float:
        """Effetto elastico."""
        if t == 0.0 or t == 1.0:
            return t
        
        p = 0.3
        s = p / 4.0
        return -(math.pow(2.0, 10.0 * (t - 1.0)) * 
                math.sin((t - 1.0 - s) * (2.0 * math.pi) / p))


class StateTransitionManager:
    """
    Manager per le transizioni di stato nelle animazioni.
    Gestisce transizioni fluide tra stati diversi delle visualizzazioni.
    """
    
    def __init__(self):
        self.states: Dict[str, Dict[str, Any]] = {}
        self.transitions: Dict[str, AnimationTimeline] = {}
        self.current_state = None
        self.target_state = None
        self.transition_progress = 0.0
        self.is_transitioning = False
    
    def define_state(self, state_name: str, properties: Dict[str, Any]):
        """Definisce uno stato con le sue proprietà."""
        self.states[state_name] = properties.copy()
        logger.debug(f"Definito stato {state_name} con {len(properties)} proprietà")
    
    def define_transition(self, from_state: str, to_state: str, 
                         timeline: AnimationTimeline):
        """Definisce una transizione tra due stati."""
        transition_key = f"{from_state}->{to_state}"
        self.transitions[transition_key] = timeline
        logger.debug(f"Definita transizione {transition_key}")
    
    def start_transition(self, target_state: str, duration: float = 1.0):
        """Avvia una transizione verso uno stato target."""
        if target_state not in self.states:
            logger.error(f"Stato target {target_state} non definito")
            return False
        
        self.target_state = target_state
        self.transition_progress = 0.0
        self.is_transitioning = True
        
        logger.info(f"Avviata transizione da {self.current_state} a {target_state}")
        return True
    
    def update_transition(self, delta_time: float):
        """Aggiorna la transizione corrente."""
        if not self.is_transitioning:
            return
        
        # Aggiorna il progresso
        # In una implementazione reale, questo sarebbe gestito dal TemporalController
        self.transition_progress = min(1.0, self.transition_progress + delta_time)
        
        if self.transition_progress >= 1.0:
            self.complete_transition()
    
    def complete_transition(self):
        """Completa la transizione corrente."""
        self.current_state = self.target_state
        self.target_state = None
        self.transition_progress = 0.0
        self.is_transitioning = False
        
        logger.info(f"Transizione completata, stato corrente: {self.current_state}")
    
    def get_current_properties(self) -> Dict[str, Any]:
        """Ottiene le proprietà correnti considerando le transizioni."""
        if not self.is_transitioning or not self.current_state:
            return self.states.get(self.current_state, {})
        
        # Durante la transizione, interpola tra stati
        current_props = self.states.get(self.current_state, {})
        target_props = self.states.get(self.target_state, {})
        
        # Interpolazione semplificata - in una implementazione reale
        # userebbe le timeline di transizione definite
        interpolated = {}
        for key in current_props:
            if key in target_props:
                start_val = current_props[key]
                end_val = target_props[key]
                
                if isinstance(start_val, (int, float)) and isinstance(end_val, (int, float)):
                    interpolated[key] = start_val + (end_val - start_val) * self.transition_progress
                else:
                    interpolated[key] = start_val if self.transition_progress < 0.5 else end_val
            else:
                interpolated[key] = current_props[key]
        
        return interpolated

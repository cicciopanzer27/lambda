"""
Motore di visualizzazione avanzato per lambda diagrams.
Ispirato ai lavori di Tromp e alle tecniche di SwapTube.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
from matplotlib.lines import Line2D
import json
import os
import uuid
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging


class DiagramStyle(Enum):
    """Stili di visualizzazione disponibili."""
    TROMP_STANDARD = "tromp_standard"
    TROMP_ALTERNATIVE = "tromp_alternative"
    MODERN_GRAPH = "modern_graph"
    ANIMATED_FLOW = "animated_flow"


@dataclass
class AnimationFrame:
    """Rappresenta un frame dell'animazione."""
    frame_number: int
    nodes: List[Dict]
    edges: List[Dict]
    highlights: List[str] = None
    title: str = ""
    
    def __post_init__(self):
        if self.highlights is None:
            self.highlights = []


@dataclass
class VisualizationTheme:
    """Tema per la visualizzazione."""
    background_color: str = "#ffffff"
    lambda_color: str = "#e74c3c"
    variable_color: str = "#2ecc71"
    application_color: str = "#3498db"
    edge_color: str = "#2c3e50"
    highlight_color: str = "#f39c12"
    text_color: str = "#2c3e50"
    grid_color: str = "#ecf0f1"


class TrompDiagramRenderer:
    """Renderer per lambda diagrams nello stile di Tromp."""
    
    def __init__(self, theme: VisualizationTheme = None):
        self.theme = theme or VisualizationTheme()
        self.logger = logging.getLogger(__name__)
        
    def render_lambda_diagram(self, lambda_data: Dict, style: DiagramStyle = DiagramStyle.TROMP_STANDARD) -> np.ndarray:
        """Renderizza un lambda diagram nello stile di Tromp."""
        
        if style == DiagramStyle.TROMP_STANDARD:
            return self._render_tromp_standard(lambda_data)
        elif style == DiagramStyle.TROMP_ALTERNATIVE:
            return self._render_tromp_alternative(lambda_data)
        elif style == DiagramStyle.MODERN_GRAPH:
            return self._render_modern_graph(lambda_data)
        else:
            return self._render_animated_flow(lambda_data)
    
    def _render_tromp_standard(self, lambda_data: Dict) -> np.ndarray:
        """Renderizza nello stile standard di Tromp."""
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor(self.theme.background_color)
        
        nodes = lambda_data.get('nodes', [])
        edges = lambda_data.get('edges', [])
        
        # Calcola dimensioni del diagramma
        width, height = self._calculate_tromp_dimensions(nodes)
        
        # Disegna griglia di base
        self._draw_tromp_grid(ax, width, height)
        
        # Disegna astrazioni come linee orizzontali
        abstractions = [n for n in nodes if n.get('type') == 'abstraction']
        for i, abs_node in enumerate(abstractions):
            y_pos = height - i - 1
            self._draw_abstraction_line(ax, abs_node, y_pos, width)
        
        # Disegna variabili come linee verticali
        variables = [n for n in nodes if n.get('type') == 'variable']
        for var_node in variables:
            self._draw_variable_line(ax, var_node, height)
        
        # Disegna applicazioni come collegamenti orizzontali
        applications = [e for e in edges if e.get('type') == 'application']
        for app_edge in applications:
            self._draw_application_link(ax, app_edge)
        
        ax.set_xlim(-0.5, width + 0.5)
        ax.set_ylim(-0.5, height + 0.5)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Converti in array numpy
        fig.canvas.draw()
        buf = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        buf = buf.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        plt.close(fig)
        
        return buf
    
    def _render_tromp_alternative(self, lambda_data: Dict) -> np.ndarray:
        """Renderizza nello stile alternativo di Tromp."""
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor(self.theme.background_color)
        
        nodes = lambda_data.get('nodes', [])
        edges = lambda_data.get('edges', [])
        
        # Stile alternativo: collegamenti alle variabili più vicine e profonde
        self._draw_alternative_style_diagram(ax, nodes, edges)
        
        ax.set_aspect('equal')
        ax.axis('off')
        
        fig.canvas.draw()
        buf = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        buf = buf.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        plt.close(fig)
        
        return buf
    
    def _render_modern_graph(self, lambda_data: Dict) -> np.ndarray:
        """Renderizza come grafo moderno con nodi circolari."""
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor(self.theme.background_color)
        
        nodes = lambda_data.get('nodes', [])
        edges = lambda_data.get('edges', [])
        
        # Layout automatico dei nodi
        positions = self._calculate_modern_layout(nodes, edges)
        
        # Disegna archi
        for edge in edges:
            self._draw_modern_edge(ax, edge, positions)
        
        # Disegna nodi
        for node in nodes:
            self._draw_modern_node(ax, node, positions)
        
        ax.set_aspect('equal')
        ax.axis('off')
        
        fig.canvas.draw()
        buf = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        buf = buf.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        plt.close(fig)
        
        return buf
    
    def _render_animated_flow(self, lambda_data: Dict) -> np.ndarray:
        """Renderizza con effetti di flusso animati."""
        # Implementazione base - da estendere
        return self._render_modern_graph(lambda_data)
    
    def _calculate_tromp_dimensions(self, nodes: List[Dict]) -> Tuple[int, int]:
        """Calcola le dimensioni del diagramma di Tromp."""
        variables = [n for n in nodes if n.get('type') == 'variable']
        abstractions = [n for n in nodes if n.get('type') == 'abstraction']
        
        # Larghezza: 4 * numero di variabili - 1
        width = max(4 * len(variables) - 1, 4) if variables else 4
        
        # Altezza: 2 * massimo numero di astrazioni annidate + 1
        height = max(2 * len(abstractions) + 1, 3) if abstractions else 3
        
        return width, height
    
    def _draw_tromp_grid(self, ax, width: int, height: int):
        """Disegna la griglia di base per il diagramma di Tromp."""
        # Griglia sottile
        for x in range(width + 1):
            ax.axvline(x, color=self.theme.grid_color, linewidth=0.5, alpha=0.3)
        for y in range(height + 1):
            ax.axhline(y, color=self.theme.grid_color, linewidth=0.5, alpha=0.3)
    
    def _draw_abstraction_line(self, ax, node: Dict, y_pos: float, width: int):
        """Disegna una linea di astrazione orizzontale."""
        line = Line2D([0, width], [y_pos, y_pos], 
                     color=self.theme.lambda_color, linewidth=3)
        ax.add_line(line)
        
        # Etichetta lambda
        ax.text(-0.3, y_pos, f"λ{node.get('label', '')}", 
               color=self.theme.lambda_color, fontsize=12, fontweight='bold',
               ha='right', va='center')
    
    def _draw_variable_line(self, ax, node: Dict, height: int):
        """Disegna una linea di variabile verticale."""
        x_pos = node.get('x', 0)
        y_start = node.get('y', 0)
        
        line = Line2D([x_pos, x_pos], [y_start, height], 
                     color=self.theme.variable_color, linewidth=2)
        ax.add_line(line)
        
        # Etichetta variabile
        ax.text(x_pos, -0.3, node.get('label', 'x'), 
               color=self.theme.variable_color, fontsize=10, fontweight='bold',
               ha='center', va='top')
    
    def _draw_application_link(self, ax, edge: Dict):
        """Disegna un collegamento di applicazione orizzontale."""
        # Implementazione semplificata
        x1, y1 = 1, 1  # Da calcolare in base ai nodi
        x2, y2 = 3, 1
        
        line = Line2D([x1, x2], [y1, y2], 
                     color=self.theme.application_color, linewidth=2)
        ax.add_line(line)
    
    def _draw_alternative_style_diagram(self, ax, nodes: List[Dict], edges: List[Dict]):
        """Disegna il diagramma nello stile alternativo."""
        # Layout più organico con collegamenti alle variabili più vicine
        positions = {}
        
        # Posiziona nodi in modo più naturale
        for i, node in enumerate(nodes):
            if node.get('type') == 'abstraction':
                positions[node['id']] = (i * 2, 2)
            elif node.get('type') == 'variable':
                positions[node['id']] = (i * 1.5 + 0.5, 0)
            else:
                positions[node['id']] = (i * 1.5, 1)
        
        # Disegna con stile più fluido
        for edge in edges:
            source_pos = positions.get(edge['source'], (0, 0))
            target_pos = positions.get(edge['target'], (1, 1))
            
            # Curva invece di linea retta
            self._draw_curved_edge(ax, source_pos, target_pos, edge)
        
        for node in nodes:
            pos = positions.get(node['id'], (0, 0))
            self._draw_styled_node(ax, node, pos)
    
    def _draw_curved_edge(self, ax, start: Tuple[float, float], end: Tuple[float, float], edge: Dict):
        """Disegna un arco curvo."""
        x1, y1 = start
        x2, y2 = end
        
        # Punto di controllo per la curva
        mid_x = (x1 + x2) / 2
        mid_y = max(y1, y2) + 0.5
        
        # Curva di Bézier semplificata
        t = np.linspace(0, 1, 50)
        x_curve = (1-t)**2 * x1 + 2*(1-t)*t * mid_x + t**2 * x2
        y_curve = (1-t)**2 * y1 + 2*(1-t)*t * mid_y + t**2 * y2
        
        ax.plot(x_curve, y_curve, color=edge.get('color', self.theme.edge_color), 
               linewidth=2, alpha=0.8)
    
    def _draw_styled_node(self, ax, node: Dict, pos: Tuple[float, float]):
        """Disegna un nodo con stile."""
        x, y = pos
        node_type = node.get('type', 'variable')
        
        if node_type == 'abstraction':
            # Rettangolo per astrazioni
            rect = FancyBboxPatch((x-0.3, y-0.2), 0.6, 0.4,
                                 boxstyle="round,pad=0.05",
                                 facecolor=self.theme.lambda_color,
                                 edgecolor='black', linewidth=1.5)
            ax.add_patch(rect)
        elif node_type == 'variable':
            # Cerchio per variabili
            circle = Circle((x, y), 0.2, facecolor=self.theme.variable_color,
                          edgecolor='black', linewidth=1.5)
            ax.add_patch(circle)
        else:
            # Diamante per applicazioni
            diamond = FancyBboxPatch((x-0.2, y-0.2), 0.4, 0.4,
                                   boxstyle="round,pad=0.05",
                                   facecolor=self.theme.application_color,
                                   edgecolor='black', linewidth=1.5)
            ax.add_patch(diamond)
        
        # Etichetta
        ax.text(x, y, node.get('label', ''), ha='center', va='center',
               fontsize=10, fontweight='bold', color='white')
    
    def _calculate_modern_layout(self, nodes: List[Dict], edges: List[Dict]) -> Dict[str, Tuple[float, float]]:
        """Calcola layout moderno per i nodi."""
        positions = {}
        
        # Layout semplice a griglia
        abstractions = [n for n in nodes if n.get('type') == 'abstraction']
        variables = [n for n in nodes if n.get('type') == 'variable']
        applications = [n for n in nodes if n.get('type') == 'application']
        
        # Posiziona astrazioni in alto
        for i, node in enumerate(abstractions):
            positions[node['id']] = (i * 3, 4)
        
        # Posiziona variabili in basso
        for i, node in enumerate(variables):
            positions[node['id']] = (i * 2 + 0.5, 0)
        
        # Posiziona applicazioni al centro
        for i, node in enumerate(applications):
            positions[node['id']] = (i * 2.5 + 1, 2)
        
        return positions
    
    def _draw_modern_edge(self, ax, edge: Dict, positions: Dict[str, Tuple[float, float]]):
        """Disegna un arco moderno."""
        source_pos = positions.get(edge['source'])
        target_pos = positions.get(edge['target'])
        
        if source_pos and target_pos:
            x1, y1 = source_pos
            x2, y2 = target_pos
            
            ax.plot([x1, x2], [y1, y2], 
                   color=edge.get('color', self.theme.edge_color),
                   linewidth=2, alpha=0.7)
            
            # Freccia
            dx, dy = x2 - x1, y2 - y1
            length = np.sqrt(dx**2 + dy**2)
            if length > 0:
                dx, dy = dx/length, dy/length
                ax.annotate('', xy=(x2-0.2*dx, y2-0.2*dy), 
                           xytext=(x2-0.4*dx, y2-0.4*dy),
                           arrowprops=dict(arrowstyle='->', color=edge.get('color', self.theme.edge_color)))
    
    def _draw_modern_node(self, ax, node: Dict, positions: Dict[str, Tuple[float, float]]):
        """Disegna un nodo moderno."""
        pos = positions.get(node['id'])
        if not pos:
            return
        
        x, y = pos
        node_type = node.get('type', 'variable')
        size = node.get('size', 1.0) * 0.3
        
        if node_type == 'abstraction':
            color = self.theme.lambda_color
            shape = 'square'
        elif node_type == 'variable':
            color = self.theme.variable_color
            shape = 'circle'
        else:
            color = self.theme.application_color
            shape = 'diamond'
        
        if shape == 'circle':
            circle = Circle((x, y), size, facecolor=color, 
                          edgecolor='black', linewidth=2, alpha=0.8)
            ax.add_patch(circle)
        elif shape == 'square':
            rect = Rectangle((x-size, y-size), 2*size, 2*size,
                           facecolor=color, edgecolor='black', 
                           linewidth=2, alpha=0.8)
            ax.add_patch(rect)
        
        # Etichetta
        ax.text(x, y, node.get('label', ''), ha='center', va='center',
               fontsize=12, fontweight='bold', color='white')


class AdvancedVisualizationEngine:
    """Motore di visualizzazione avanzato."""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.renderer = TrompDiagramRenderer()
        self.logger = logging.getLogger(__name__)
        os.makedirs(output_dir, exist_ok=True)
    
    def create_advanced_animation(self, lambda_data: Dict, config: Dict) -> Optional[str]:
        """Crea un'animazione avanzata del lambda diagram."""
        try:
            video_id = str(uuid.uuid4())
            output_path = os.path.join(self.output_dir, f"{video_id}.mp4")
            
            # Genera sequenza di frame
            frames = self._generate_animation_frames(lambda_data, config)
            
            # Crea animazione
            success = self._create_animation_video(frames, output_path, config)
            
            return video_id if success else None
            
        except Exception as e:
            self.logger.error(f"Errore nella creazione animazione avanzata: {e}")
            return None
    
    def _generate_animation_frames(self, lambda_data: Dict, config: Dict) -> List[AnimationFrame]:
        """Genera la sequenza di frame per l'animazione."""
        frames = []
        nodes = lambda_data.get('nodes', [])
        edges = lambda_data.get('edges', [])
        
        # Frame 1: Struttura iniziale
        frames.append(AnimationFrame(
            frame_number=0,
            nodes=nodes.copy(),
            edges=edges.copy(),
            title="Struttura Lambda Iniziale"
        ))
        
        # Frame 2: Evidenzia astrazioni
        abstraction_nodes = [n['id'] for n in nodes if n.get('type') == 'abstraction']
        frames.append(AnimationFrame(
            frame_number=1,
            nodes=nodes.copy(),
            edges=edges.copy(),
            highlights=abstraction_nodes,
            title="Astrazioni Lambda"
        ))
        
        # Frame 3: Evidenzia variabili
        variable_nodes = [n['id'] for n in nodes if n.get('type') == 'variable']
        frames.append(AnimationFrame(
            frame_number=2,
            nodes=nodes.copy(),
            edges=edges.copy(),
            highlights=variable_nodes,
            title="Variabili"
        ))
        
        # Frame 4: Evidenzia binding
        binding_edges = [e for e in edges if e.get('type') == 'binding']
        frames.append(AnimationFrame(
            frame_number=3,
            nodes=nodes.copy(),
            edges=edges.copy(),
            highlights=[e['source'] for e in binding_edges] + [e['target'] for e in binding_edges],
            title="Binding delle Variabili"
        ))
        
        # Frame 5: Struttura completa
        frames.append(AnimationFrame(
            frame_number=4,
            nodes=nodes.copy(),
            edges=edges.copy(),
            title="Struttura Completa"
        ))
        
        return frames
    
    def _create_animation_video(self, frames: List[AnimationFrame], output_path: str, config: Dict) -> bool:
        """Crea il video dell'animazione."""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            fig.patch.set_facecolor('#ffffff')
            
            def animate(frame_idx):
                ax.clear()
                
                if frame_idx < len(frames):
                    frame = frames[frame_idx]
                    self._render_frame(ax, frame)
                
                return ax.artists + ax.patches + ax.lines + ax.texts
            
            # Crea animazione
            fps = config.get('fps', 2)  # Più lento per vedere i dettagli
            duration = config.get('duration', 10.0)
            num_frames = max(len(frames), int(fps * duration))
            
            anim = animation.FuncAnimation(
                fig, animate, frames=num_frames,
                interval=1000/fps, blit=False, repeat=True
            )
            
            # Salva video
            anim.save(output_path, writer='ffmpeg', fps=fps, bitrate=1800)
            plt.close(fig)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Errore nella creazione video animazione: {e}")
            return False
    
    def _render_frame(self, ax, frame: AnimationFrame):
        """Renderizza un singolo frame."""
        nodes = frame.nodes
        edges = frame.edges
        highlights = frame.highlights or []
        
        # Calcola posizioni
        positions = self._calculate_frame_positions(nodes, edges)
        
        # Disegna archi
        for edge in edges:
            source_pos = positions.get(edge['source'])
            target_pos = positions.get(edge['target'])
            
            if source_pos and target_pos:
                color = '#f39c12' if (edge['source'] in highlights or edge['target'] in highlights) else edge.get('color', '#2c3e50')
                ax.plot([source_pos[0], target_pos[0]], [source_pos[1], target_pos[1]], 
                       color=color, linewidth=3 if color == '#f39c12' else 2, alpha=0.8)
        
        # Disegna nodi
        for node in nodes:
            pos = positions.get(node['id'])
            if pos:
                is_highlighted = node['id'] in highlights
                self._draw_frame_node(ax, node, pos, is_highlighted)
        
        # Titolo
        ax.set_title(frame.title, fontsize=16, fontweight='bold', pad=20)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Limiti
        if positions:
            xs = [pos[0] for pos in positions.values()]
            ys = [pos[1] for pos in positions.values()]
            margin = 1.0
            ax.set_xlim(min(xs) - margin, max(xs) + margin)
            ax.set_ylim(min(ys) - margin, max(ys) + margin)
    
    def _calculate_frame_positions(self, nodes: List[Dict], edges: List[Dict]) -> Dict[str, Tuple[float, float]]:
        """Calcola posizioni per il frame."""
        positions = {}
        
        # Layout gerarchico
        abstractions = [n for n in nodes if n.get('type') == 'abstraction']
        variables = [n for n in nodes if n.get('type') == 'variable']
        applications = [n for n in nodes if n.get('type') == 'application']
        
        # Astrazioni in alto
        for i, node in enumerate(abstractions):
            positions[node['id']] = (i * 4, 3)
        
        # Variabili in basso
        for i, node in enumerate(variables):
            positions[node['id']] = (i * 3 + 1, 0)
        
        # Applicazioni al centro
        for i, node in enumerate(applications):
            positions[node['id']] = (i * 3.5 + 0.5, 1.5)
        
        return positions
    
    def _draw_frame_node(self, ax, node: Dict, pos: Tuple[float, float], highlighted: bool):
        """Disegna un nodo nel frame."""
        x, y = pos
        node_type = node.get('type', 'variable')
        
        # Colori
        if highlighted:
            color = '#f39c12'
            edge_color = '#e67e22'
            linewidth = 3
        else:
            if node_type == 'abstraction':
                color = '#e74c3c'
            elif node_type == 'variable':
                color = '#2ecc71'
            else:
                color = '#3498db'
            edge_color = 'black'
            linewidth = 2
        
        # Forma
        if node_type == 'abstraction':
            rect = FancyBboxPatch((x-0.4, y-0.3), 0.8, 0.6,
                                 boxstyle="round,pad=0.1",
                                 facecolor=color, edgecolor=edge_color, 
                                 linewidth=linewidth, alpha=0.9)
            ax.add_patch(rect)
        elif node_type == 'variable':
            circle = Circle((x, y), 0.3, facecolor=color,
                          edgecolor=edge_color, linewidth=linewidth, alpha=0.9)
            ax.add_patch(circle)
        else:
            diamond = FancyBboxPatch((x-0.3, y-0.3), 0.6, 0.6,
                                   boxstyle="round,pad=0.1",
                                   facecolor=color, edgecolor=edge_color,
                                   linewidth=linewidth, alpha=0.9)
            ax.add_patch(diamond)
        
        # Etichetta
        text_color = 'white' if not highlighted else 'black'
        fontsize = 14 if highlighted else 12
        ax.text(x, y, node.get('label', ''), ha='center', va='center',
               fontsize=fontsize, fontweight='bold', color=text_color)

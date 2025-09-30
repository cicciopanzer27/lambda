"""
Servizio per la generazione di visualizzazioni dinamiche dei lambda diagrams.
"""

import os
import json
import uuid
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import subprocess
import tempfile


@dataclass
class VisualizationConfig:
    """Configurazione per la visualizzazione."""
    width: int = 800
    height: int = 600
    fps: int = 30
    duration: float = 5.0
    background_color: str = "#ffffff"
    quality: str = "medium"  # low, medium, high


class VisualizationService:
    """Servizio per la generazione di visualizzazioni."""
    
    def __init__(self, output_dir: str = "/home/ubuntu/lambda_visualizer_backend/static/videos"):
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        os.makedirs(output_dir, exist_ok=True)
        
        # Import dei moduli avanzati
        try:
            from .advanced_visualization import AdvancedVisualizationEngine, DiagramStyle
            from .lambda_reduction import VisualizationDataGenerator
            
            self.advanced_engine = AdvancedVisualizationEngine(output_dir)
            self.reduction_generator = VisualizationDataGenerator()
            self.has_advanced_features = True
        except ImportError as e:
            self.logger.warning(f"Funzionalità avanzate non disponibili: {e}")
            self.has_advanced_features = False
    
    def generate_lambda_diagram_video(self, 
                                    lambda_data: Dict, 
                                    config: VisualizationConfig = None) -> Optional[str]:
        """Genera un video del lambda diagram."""
        if config is None:
            config = VisualizationConfig()
        
        try:
            # Genera un ID unico per il video
            video_id = str(uuid.uuid4())
            output_path = os.path.join(self.output_dir, f"{video_id}.mp4")
            
            # Crea il video usando il generatore Python personalizzato
            success = self._create_video_with_python(lambda_data, output_path, config)
            
            if success:
                return video_id
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Errore nella generazione video: {e}")
            return None
    
    def _create_video_with_python(self, 
                                lambda_data: Dict, 
                                output_path: str, 
                                config: VisualizationConfig) -> bool:
        """Crea il video usando Python e FFmpeg."""
        try:
            # Crea script Python temporaneo per la generazione
            script_content = self._generate_visualization_script(lambda_data, output_path, config)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(script_content)
                script_path = f.name
            
            try:
                # Esegui lo script
                result = subprocess.run([
                    'python3', script_path
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    self.logger.info(f"Video generato con successo: {output_path}")
                    return True
                else:
                    self.logger.error(f"Errore nella generazione: {result.stderr}")
                    return False
                    
            finally:
                # Pulisci file temporaneo
                os.unlink(script_path)
                
        except Exception as e:
            self.logger.error(f"Errore nella creazione video Python: {e}")
            return False
    
    def _generate_visualization_script(self, 
                                     lambda_data: Dict, 
                                     output_path: str, 
                                     config: VisualizationConfig) -> str:
        """Genera lo script Python per la visualizzazione."""
        nodes = lambda_data.get('nodes', [])
        edges = lambda_data.get('edges', [])
        
        script = f'''
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import networkx as nx
from matplotlib.patches import Circle
import json

# Configurazione
WIDTH = {config.width}
HEIGHT = {config.height}
FPS = {config.fps}
DURATION = {config.duration}

# Dati del grafo
nodes_data = {json.dumps(nodes)}
edges_data = {json.dumps(edges)}

def create_graph():
    G = nx.Graph()
    
    # Aggiungi nodi
    for node in nodes_data:
        G.add_node(node['id'], 
                  label=node['label'],
                  node_type=node['type'],
                  color=node['color'],
                  size=node['size'],
                  pos=(node['x'], node['y']))
    
    # Aggiungi archi
    for edge in edges_data:
        G.add_edge(edge['source'], edge['target'],
                  color=edge['color'],
                  weight=edge['weight'])
    
    return G

def animate_graph(frame):
    ax.clear()
    
    # Crea il grafo
    G = create_graph()
    
    # Posizioni dei nodi
    pos = nx.get_node_attributes(G, 'pos')
    if not pos:
        pos = nx.spring_layout(G)
    
    # Colori e dimensioni dei nodi
    node_colors = [G.nodes[node]['color'] for node in G.nodes()]
    node_sizes = [G.nodes[node]['size'] * 500 for node in G.nodes()]
    
    # Colori degli archi
    edge_colors = [G.edges[edge].get('color', '#2c3e50') for edge in G.edges()]
    
    # Disegna il grafo
    nx.draw(G, pos, 
           node_color=node_colors,
           node_size=node_sizes,
           edge_color=edge_colors,
           with_labels=True,
           labels={{node: G.nodes[node]['label'] for node in G.nodes()}},
           font_size=10,
           font_weight='bold',
           ax=ax)
    
    # Titolo con frame
    ax.set_title(f'Lambda Diagram - Frame {{frame + 1}}', fontsize=14, fontweight='bold')
    ax.set_aspect('equal')

# Crea figura e animazione
fig, ax = plt.subplots(figsize=({config.width/100}, {config.height/100}))
fig.patch.set_facecolor('{config.background_color}')

# Numero di frame
num_frames = int(FPS * DURATION)

# Crea animazione
anim = animation.FuncAnimation(fig, animate_graph, frames=num_frames, 
                             interval=1000/FPS, repeat=False)

# Salva come video
try:
    anim.save('{output_path}', writer='ffmpeg', fps=FPS, bitrate=1800)
    print("Video salvato con successo")
except Exception as e:
    print(f"Errore nel salvataggio: {{e}}")
    # Fallback: salva come GIF
    try:
        gif_path = '{output_path}'.replace('.mp4', '.gif')
        anim.save(gif_path, writer='pillow', fps=FPS//2)
        print(f"Salvato come GIF: {{gif_path}}")
    except Exception as e2:
        print(f"Errore anche nel GIF: {{e2}}")

plt.close()
'''
        return script
    
    def generate_static_image(self, lambda_data: Dict, image_id: str = None) -> Optional[str]:
        """Genera un'immagine statica del lambda diagram."""
        if image_id is None:
            image_id = str(uuid.uuid4())
        
        try:
            output_path = os.path.join(self.output_dir, f"{image_id}.png")
            
            # Crea script per immagine statica
            script_content = self._generate_static_image_script(lambda_data, output_path)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(script_content)
                script_path = f.name
            
            try:
                result = subprocess.run([
                    'python3', script_path
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    return image_id
                else:
                    self.logger.error(f"Errore generazione immagine: {result.stderr}")
                    return None
                    
            finally:
                os.unlink(script_path)
                
        except Exception as e:
            self.logger.error(f"Errore nella generazione immagine: {e}")
            return None
    
    def _generate_static_image_script(self, lambda_data: Dict, output_path: str) -> str:
        """Genera script per immagine statica."""
        nodes = lambda_data.get('nodes', [])
        edges = lambda_data.get('edges', [])
        
        script = f'''
import matplotlib.pyplot as plt
import networkx as nx
import json

# Dati del grafo
nodes_data = {json.dumps(nodes)}
edges_data = {json.dumps(edges)}

# Crea il grafo
G = nx.Graph()

# Aggiungi nodi
for node in nodes_data:
    G.add_node(node['id'], 
              label=node['label'],
              node_type=node['type'],
              color=node['color'],
              size=node['size'],
              pos=(node['x'], node['y']))

# Aggiungi archi
for edge in edges_data:
    G.add_edge(edge['source'], edge['target'],
              color=edge['color'],
              weight=edge['weight'])

# Crea figura
fig, ax = plt.subplots(figsize=(10, 8))
fig.patch.set_facecolor('#ffffff')

# Posizioni dei nodi
pos = nx.get_node_attributes(G, 'pos')
if not pos:
    pos = nx.spring_layout(G, seed=42)

# Colori e dimensioni
node_colors = [G.nodes[node]['color'] for node in G.nodes()]
node_sizes = [G.nodes[node]['size'] * 800 for node in G.nodes()]
edge_colors = [G.edges[edge].get('color', '#2c3e50') for edge in G.edges()]

# Disegna il grafo
nx.draw(G, pos, 
       node_color=node_colors,
       node_size=node_sizes,
       edge_color=edge_colors,
       with_labels=True,
       labels={{node: G.nodes[node]['label'] for node in G.nodes()}},
       font_size=12,
       font_weight='bold',
       ax=ax)

ax.set_title('Lambda Diagram', fontsize=16, fontweight='bold')
ax.set_aspect('equal')

# Salva immagine
plt.savefig('{output_path}', dpi=300, bbox_inches='tight', 
           facecolor='white', edgecolor='none')
plt.close()

print("Immagine salvata con successo")
'''
        return script
    
    def get_video_info(self, video_id: str) -> Optional[Dict]:
        """Ottiene informazioni su un video generato."""
        video_path = os.path.join(self.output_dir, f"{video_id}.mp4")
        
        if not os.path.exists(video_path):
            return None
        
        try:
            stat = os.stat(video_path)
            return {
                "id": video_id,
                "path": video_path,
                "size": stat.st_size,
                "created": stat.st_ctime,
                "exists": True
            }
        except Exception as e:
            self.logger.error(f"Errore nel recupero info video: {e}")
            return None
    
    def cleanup_old_videos(self, max_age_hours: int = 24):
        """Pulisce i video più vecchi di max_age_hours."""
        import time
        
        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for filename in os.listdir(self.output_dir):
                if filename.endswith(('.mp4', '.gif', '.png')):
                    filepath = os.path.join(self.output_dir, filename)
                    file_age = current_time - os.path.getctime(filepath)
                    
                    if file_age > max_age_seconds:
                        os.remove(filepath)
                        self.logger.info(f"Rimosso file vecchio: {filename}")
                        
        except Exception as e:
            self.logger.error(f"Errore nella pulizia file: {e}")
    
    def list_generated_content(self) -> List[Dict]:
        """Lista tutto il contenuto generato."""
        content = []
        
        try:
            for filename in os.listdir(self.output_dir):
                if filename.endswith(('.mp4', '.gif', '.png')):
                    filepath = os.path.join(self.output_dir, filename)
                    stat = os.stat(filepath)
                    
                    content.append({
                        "filename": filename,
                        "id": filename.split('.')[0],
                        "type": filename.split('.')[-1],
                        "size": stat.st_size,
                        "created": stat.st_ctime
                    })
                    
        except Exception as e:
            self.logger.error(f"Errore nel listing contenuto: {e}")
        
        return sorted(content, key=lambda x: x['created'], reverse=True)
    
    def generate_reduction_animation(self, expression: str, config: VisualizationConfig = None) -> Optional[str]:
        """Genera un'animazione delle riduzioni beta."""
        if not self.has_advanced_features:
            self.logger.warning("Funzionalità avanzate non disponibili")
            return None
        
        try:
            if config is None:
                config = VisualizationConfig()
            
            # Genera dati per l'animazione delle riduzioni
            reduction_data = self.reduction_generator.generate_reduction_animation_data(expression)
            
            # Crea animazione avanzata
            video_id = self.advanced_engine.create_advanced_animation(reduction_data, config.__dict__)
            
            return video_id
            
        except Exception as e:
            self.logger.error(f"Errore nella generazione animazione riduzioni: {e}")
            return None
    
    def generate_tromp_style_diagram(self, lambda_data: Dict, style: str = "standard") -> Optional[str]:
        """Genera un diagramma nello stile di Tromp."""
        if not self.has_advanced_features:
            self.logger.warning("Funzionalità avanzate non disponibili")
            return None
        
        try:
            from .advanced_visualization import DiagramStyle
            
            # Mappa stili
            style_map = {
                "standard": DiagramStyle.TROMP_STANDARD,
                "alternative": DiagramStyle.TROMP_ALTERNATIVE,
                "modern": DiagramStyle.MODERN_GRAPH,
                "animated": DiagramStyle.ANIMATED_FLOW
            }
            
            diagram_style = style_map.get(style, DiagramStyle.TROMP_STANDARD)
            
            # Renderizza diagramma
            image_array = self.advanced_engine.renderer.render_lambda_diagram(lambda_data, diagram_style)
            
            # Salva immagine
            image_id = str(uuid.uuid4())
            output_path = os.path.join(self.output_dir, f"{image_id}.png")
            
            import matplotlib.pyplot as plt
            plt.imsave(output_path, image_array)
            
            return image_id
            
        except Exception as e:
            self.logger.error(f"Errore nella generazione diagramma Tromp: {e}")
            return None
    
    def get_reduction_steps(self, expression: str) -> Optional[Dict]:
        """Ottiene i passi di riduzione per un'espressione."""
        if not self.has_advanced_features:
            return None
        
        try:
            return self.reduction_generator.generate_reduction_animation_data(expression)
        except Exception as e:
            self.logger.error(f"Errore nel calcolo riduzioni: {e}")
            return None

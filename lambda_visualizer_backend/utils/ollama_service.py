"""
Servizio per l'integrazione con Ollama per l'elaborazione delle espressioni lambda.
"""

import ollama
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class OllamaResponse:
    """Risposta strutturata da Ollama."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    raw_response: Optional[str] = None


class OllamaService:
    """Servizio per l'interazione con Ollama."""
    
    def __init__(self, model_name: str = "llama3.2", host: str = "http://localhost:11434"):
        self.model_name = model_name
        self.host = host
        self.client = ollama.Client(host=host)
        self.logger = logging.getLogger(__name__)
        
    def is_available(self) -> bool:
        """Verifica se Ollama è disponibile."""
        try:
            models = self.client.list()
            return True
        except Exception as e:
            self.logger.error(f"Ollama non disponibile: {e}")
            return False
    
    def analyze_lambda_expression(self, expression: str) -> OllamaResponse:
        """Analizza un'espressione lambda usando Ollama."""
        prompt = self._create_analysis_prompt(expression)
        
        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'system',
                        'content': self._get_system_prompt()
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                stream=False
            )
            
            content = response['message']['content']
            parsed_data = self._parse_response(content)
            
            return OllamaResponse(
                success=True,
                data=parsed_data,
                raw_response=content
            )
            
        except Exception as e:
            self.logger.error(f"Errore nell'analisi lambda: {e}")
            return OllamaResponse(
                success=False,
                error=str(e)
            )
    
    def generate_visualization_config(self, expression: str, analysis: Dict) -> OllamaResponse:
        """Genera configurazione per la visualizzazione."""
        prompt = self._create_visualization_prompt(expression, analysis)
        
        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'system',
                        'content': self._get_visualization_system_prompt()
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                stream=False
            )
            
            content = response['message']['content']
            config = self._parse_visualization_config(content)
            
            return OllamaResponse(
                success=True,
                data=config,
                raw_response=content
            )
            
        except Exception as e:
            self.logger.error(f"Errore nella generazione config visualizzazione: {e}")
            return OllamaResponse(
                success=False,
                error=str(e)
            )
    
    def _get_system_prompt(self) -> str:
        """Prompt di sistema per l'analisi lambda."""
        return """Sei un esperto di lambda calculus. Il tuo compito è analizzare espressioni lambda e fornire informazioni strutturate.

Per ogni espressione lambda, devi identificare:
1. Il tipo di espressione (identità, costante, combinatore, etc.)
2. Le variabili presenti
3. La struttura delle astrazioni
4. Le applicazioni
5. La complessità computazionale

Rispondi sempre in formato JSON con questa struttura:
{
    "type": "tipo_espressione",
    "variables": ["lista", "variabili"],
    "abstractions": [{"var": "x", "body": "corpo"}],
    "applications": [{"function": "f", "argument": "arg"}],
    "complexity": "descrizione_complessità",
    "description": "descrizione_naturale"
}"""
    
    def _get_visualization_system_prompt(self) -> str:
        """Prompt di sistema per la configurazione visualizzazione."""
        return """Sei un esperto di visualizzazione di grafi e lambda calculus. 

Il tuo compito è generare configurazioni per la visualizzazione di espressioni lambda come grafi dinamici.

Considera:
1. Posizionamento ottimale dei nodi
2. Colori appropriati per diversi tipi di nodi
3. Dimensioni basate sull'importanza
4. Animazioni per mostrare riduzioni
5. Layout che minimizza sovrapposizioni

Rispondi in formato JSON con:
{
    "layout": "tipo_layout",
    "node_colors": {"type": "color"},
    "node_sizes": {"type": size},
    "animation_steps": [{"step": 1, "description": "desc"}],
    "visual_properties": {"property": "value"}
}"""
    
    def _create_analysis_prompt(self, expression: str) -> str:
        """Crea il prompt per l'analisi dell'espressione."""
        return f"""Analizza questa espressione lambda: {expression}

Fornisci un'analisi completa includendo:
- Tipo di espressione
- Variabili e loro binding
- Struttura delle astrazioni
- Eventuali applicazioni
- Complessità computazionale
- Descrizione in linguaggio naturale

Esempio di espressioni:
- λx.x è la funzione identità
- λx.λy.x è la funzione costante K
- λf.λx.f(f x) è il numerale di Church 2

Rispondi in formato JSON."""
    
    def _create_visualization_prompt(self, expression: str, analysis: Dict) -> str:
        """Crea il prompt per la configurazione visualizzazione."""
        return f"""Basandoti su questa espressione lambda: {expression}
E questa analisi: {json.dumps(analysis, indent=2)}

Genera una configurazione per visualizzare l'espressione come grafo dinamico.

Considera:
- Nodi per astrazioni (λ) in rosso
- Nodi per variabili in verde
- Nodi per applicazioni in blu
- Archi per binding e applicazioni
- Layout che evidenzi la struttura
- Animazioni per mostrare riduzioni beta

Rispondi in formato JSON."""
    
    def _parse_response(self, content: str) -> Dict:
        """Parsing della risposta di Ollama."""
        try:
            # Cerca JSON nel contenuto
            start = content.find('{')
            end = content.rfind('}') + 1
            
            if start != -1 and end != 0:
                json_str = content[start:end]
                return json.loads(json_str)
            else:
                # Fallback: crea struttura base
                return {
                    "type": "unknown",
                    "variables": [],
                    "abstractions": [],
                    "applications": [],
                    "complexity": "unknown",
                    "description": content
                }
                
        except json.JSONDecodeError:
            self.logger.warning("Impossibile parsare JSON dalla risposta")
            return {
                "type": "unknown",
                "variables": [],
                "abstractions": [],
                "applications": [],
                "complexity": "unknown",
                "description": content
            }
    
    def _parse_visualization_config(self, content: str) -> Dict:
        """Parsing della configurazione visualizzazione."""
        try:
            start = content.find('{')
            end = content.rfind('}') + 1
            
            if start != -1 and end != 0:
                json_str = content[start:end]
                return json.loads(json_str)
            else:
                # Configurazione di default
                return self._get_default_visualization_config()
                
        except json.JSONDecodeError:
            self.logger.warning("Impossibile parsare config visualizzazione")
            return self._get_default_visualization_config()
    
    def _get_default_visualization_config(self) -> Dict:
        """Configurazione visualizzazione di default."""
        return {
            "layout": "hierarchical",
            "node_colors": {
                "abstraction": "#e74c3c",
                "variable": "#2ecc71",
                "application": "#3498db"
            },
            "node_sizes": {
                "abstraction": 1.2,
                "variable": 1.0,
                "application": 1.1
            },
            "animation_steps": [
                {"step": 1, "description": "Mostra struttura iniziale"},
                {"step": 2, "description": "Evidenzia binding"},
                {"step": 3, "description": "Mostra flusso dati"}
            ],
            "visual_properties": {
                "edge_color": "#2c3e50",
                "background_color": "#ecf0f1",
                "font_size": 12
            }
        }
    
    def get_available_models(self) -> List[str]:
        """Ottiene la lista dei modelli disponibili."""
        try:
            models = self.client.list()
            return [model['name'] for model in models['models']]
        except Exception as e:
            self.logger.error(f"Errore nel recupero modelli: {e}")
            return []
    
    def pull_model(self, model_name: str) -> bool:
        """Scarica un modello se non presente."""
        try:
            self.client.pull(model_name)
            return True
        except Exception as e:
            self.logger.error(f"Errore nel download modello {model_name}: {e}")
            return False

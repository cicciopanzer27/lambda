"""
Modulo per la riduzione beta e visualizzazione delle trasformazioni lambda.
"""

import re
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging


class ReductionType(Enum):
    """Tipi di riduzione lambda."""
    BETA = "beta"
    ALPHA = "alpha"
    ETA = "eta"
    DELTA = "delta"


@dataclass
class ReductionStep:
    """Rappresenta un passo di riduzione."""
    step_number: int
    expression_before: str
    expression_after: str
    reduction_type: ReductionType
    position: str
    description: str
    redex: str = ""
    contractum: str = ""


class LambdaParser:
    """Parser semplificato per espressioni lambda."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse(self, expression: str) -> Dict[str, Any]:
        """Parsing di un'espressione lambda."""
        # Normalizza l'espressione
        expr = self._normalize_expression(expression)
        
        # Identifica componenti
        components = self._identify_components(expr)
        
        return {
            'original': expression,
            'normalized': expr,
            'components': components,
            'variables': self._extract_variables(expr),
            'abstractions': self._extract_abstractions(expr),
            'applications': self._extract_applications(expr)
        }
    
    def _normalize_expression(self, expr: str) -> str:
        """Normalizza l'espressione lambda."""
        # Sostituisci simboli lambda alternativi
        expr = expr.replace('\\', 'λ')
        expr = expr.replace('^', 'λ')
        
        # Rimuovi spazi extra
        expr = re.sub(r'\s+', ' ', expr.strip())
        
        return expr
    
    def _identify_components(self, expr: str) -> List[Dict]:
        """Identifica i componenti dell'espressione."""
        components = []
        
        # Pattern per astrazioni
        lambda_pattern = r'λ([a-zA-Z][a-zA-Z0-9]*)\.'
        matches = re.finditer(lambda_pattern, expr)
        
        for match in matches:
            components.append({
                'type': 'abstraction',
                'variable': match.group(1),
                'position': match.span(),
                'full_match': match.group(0)
            })
        
        # Pattern per variabili libere
        var_pattern = r'\b([a-zA-Z][a-zA-Z0-9]*)\b'
        matches = re.finditer(var_pattern, expr)
        
        for match in matches:
            if not any(comp['variable'] == match.group(1) 
                      for comp in components if comp['type'] == 'abstraction'):
                components.append({
                    'type': 'variable',
                    'name': match.group(1),
                    'position': match.span(),
                    'full_match': match.group(0)
                })
        
        return components
    
    def _extract_variables(self, expr: str) -> List[str]:
        """Estrae tutte le variabili."""
        pattern = r'\b([a-zA-Z][a-zA-Z0-9]*)\b'
        return list(set(re.findall(pattern, expr)))
    
    def _extract_abstractions(self, expr: str) -> List[Dict]:
        """Estrae le astrazioni."""
        pattern = r'λ([a-zA-Z][a-zA-Z0-9]*)\.'
        matches = re.finditer(pattern, expr)
        
        abstractions = []
        for match in matches:
            abstractions.append({
                'variable': match.group(1),
                'position': match.span(),
                'body_start': match.end()
            })
        
        return abstractions
    
    def _extract_applications(self, expr: str) -> List[Dict]:
        """Estrae le applicazioni."""
        # Implementazione semplificata
        applications = []
        
        # Pattern per applicazioni esplicite con parentesi
        app_pattern = r'\(([^)]+)\)\s*\(([^)]+)\)'
        matches = re.finditer(app_pattern, expr)
        
        for match in matches:
            applications.append({
                'function': match.group(1).strip(),
                'argument': match.group(2).strip(),
                'position': match.span()
            })
        
        return applications


class BetaReducer:
    """Esegue riduzioni beta su espressioni lambda."""
    
    def __init__(self):
        self.parser = LambdaParser()
        self.logger = logging.getLogger(__name__)
    
    def reduce_expression(self, expression: str, max_steps: int = 10) -> List[ReductionStep]:
        """Esegue riduzione beta completa."""
        steps = []
        current_expr = expression
        step_count = 0
        
        while step_count < max_steps:
            # Trova prossimo redex
            redex_info = self._find_beta_redex(current_expr)
            
            if not redex_info:
                # Nessun redex trovato - forma normale raggiunta
                break
            
            # Esegui riduzione
            new_expr = self._perform_beta_reduction(current_expr, redex_info)
            
            if new_expr == current_expr:
                # Nessun cambiamento - termina
                break
            
            # Crea step di riduzione
            step = ReductionStep(
                step_number=step_count + 1,
                expression_before=current_expr,
                expression_after=new_expr,
                reduction_type=ReductionType.BETA,
                position=redex_info.get('position', ''),
                description=self._describe_reduction(redex_info),
                redex=redex_info.get('redex', ''),
                contractum=redex_info.get('contractum', '')
            )
            
            steps.append(step)
            current_expr = new_expr
            step_count += 1
        
        return steps
    
    def _find_beta_redex(self, expr: str) -> Optional[Dict]:
        """Trova il prossimo redex beta."""
        # Pattern per (λx.M) N
        pattern = r'\((λ([a-zA-Z][a-zA-Z0-9]*))\.([^)]+)\)\s*([a-zA-Z][a-zA-Z0-9]*|\([^)]+\))'
        
        match = re.search(pattern, expr)
        if match:
            return {
                'redex': match.group(0),
                'lambda_var': match.group(2),
                'body': match.group(3),
                'argument': match.group(4),
                'position': match.span(),
                'full_match': match
            }
        
        # Pattern più semplice: λx.M N (senza parentesi esterne)
        pattern2 = r'λ([a-zA-Z][a-zA-Z0-9]*)\.([^\s]+)\s+([a-zA-Z][a-zA-Z0-9]*)'
        match2 = re.search(pattern2, expr)
        if match2:
            return {
                'redex': match2.group(0),
                'lambda_var': match2.group(1),
                'body': match2.group(2),
                'argument': match2.group(3),
                'position': match2.span(),
                'full_match': match2
            }
        
        return None
    
    def _perform_beta_reduction(self, expr: str, redex_info: Dict) -> str:
        """Esegue una singola riduzione beta."""
        try:
            lambda_var = redex_info['lambda_var']
            body = redex_info['body']
            argument = redex_info['argument']
            redex = redex_info['redex']
            
            # Sostituisci tutte le occorrenze della variabile nel corpo
            # con l'argomento (implementazione semplificata)
            contractum = self._substitute_variable(body, lambda_var, argument)
            
            # Sostituisci il redex con il contractum nell'espressione
            new_expr = expr.replace(redex, contractum, 1)
            
            return new_expr
            
        except Exception as e:
            self.logger.error(f"Errore nella riduzione beta: {e}")
            return expr
    
    def _substitute_variable(self, body: str, var: str, replacement: str) -> str:
        """Sostituisce una variabile nel corpo (implementazione semplificata)."""
        # Pattern per trovare occorrenze della variabile come parola intera
        pattern = r'\b' + re.escape(var) + r'\b'
        
        # Sostituisci tutte le occorrenze
        result = re.sub(pattern, replacement, body)
        
        return result
    
    def _describe_reduction(self, redex_info: Dict) -> str:
        """Crea descrizione della riduzione."""
        lambda_var = redex_info.get('lambda_var', 'x')
        argument = redex_info.get('argument', 'arg')
        
        return f"Applica λ{lambda_var} all'argomento {argument}"
    
    def is_normal_form(self, expression: str) -> bool:
        """Verifica se l'espressione è in forma normale."""
        return self._find_beta_redex(expression) is None
    
    def get_reduction_tree(self, expression: str) -> Dict:
        """Ottiene l'albero completo delle riduzioni."""
        steps = self.reduce_expression(expression)
        
        tree = {
            'root': expression,
            'steps': steps,
            'final_form': steps[-1].expression_after if steps else expression,
            'is_normal_form': self.is_normal_form(steps[-1].expression_after if steps else expression),
            'reduction_count': len(steps)
        }
        
        return tree


class VisualizationDataGenerator:
    """Genera dati per la visualizzazione delle riduzioni."""
    
    def __init__(self):
        self.parser = LambdaParser()
        self.reducer = BetaReducer()
        self.logger = logging.getLogger(__name__)
    
    def generate_reduction_animation_data(self, expression: str) -> Dict:
        """Genera dati per animare le riduzioni."""
        # Parsing iniziale
        parsed = self.parser.parse(expression)
        
        # Riduzioni
        reduction_steps = self.reducer.reduce_expression(expression)
        
        # Genera frame per ogni step
        frames = []
        
        # Frame iniziale
        initial_frame = self._create_expression_frame(expression, 0, "Espressione Iniziale")
        frames.append(initial_frame)
        
        # Frame per ogni riduzione
        for i, step in enumerate(reduction_steps):
            # Frame che evidenzia il redex
            redex_frame = self._create_redex_highlight_frame(
                step.expression_before, step.redex, i*2 + 1, 
                f"Step {step.step_number}: Identifica Redex"
            )
            frames.append(redex_frame)
            
            # Frame con il risultato
            result_frame = self._create_expression_frame(
                step.expression_after, i*2 + 2, 
                f"Step {step.step_number}: Dopo Riduzione"
            )
            frames.append(result_frame)
        
        return {
            'original_expression': expression,
            'parsed_data': parsed,
            'reduction_steps': [step.__dict__ for step in reduction_steps],
            'animation_frames': frames,
            'final_form': reduction_steps[-1].expression_after if reduction_steps else expression,
            'is_normal_form': self.reducer.is_normal_form(
                reduction_steps[-1].expression_after if reduction_steps else expression
            )
        }
    
    def _create_expression_frame(self, expression: str, frame_number: int, title: str) -> Dict:
        """Crea un frame per un'espressione."""
        parsed = self.parser.parse(expression)
        
        # Converti in formato nodi/archi
        nodes, edges = self._expression_to_graph(parsed)
        
        return {
            'frame_number': frame_number,
            'title': title,
            'expression': expression,
            'nodes': nodes,
            'edges': edges,
            'highlights': []
        }
    
    def _create_redex_highlight_frame(self, expression: str, redex: str, frame_number: int, title: str) -> Dict:
        """Crea un frame che evidenzia un redex."""
        frame = self._create_expression_frame(expression, frame_number, title)
        
        # Identifica nodi da evidenziare basandosi sul redex
        # Implementazione semplificata
        frame['highlights'] = ['redex_highlight']
        frame['redex'] = redex
        
        return frame
    
    def _expression_to_graph(self, parsed_data: Dict) -> Tuple[List[Dict], List[Dict]]:
        """Converte dati parsed in nodi e archi."""
        nodes = []
        edges = []
        
        # Crea nodi per astrazioni
        for i, abs_data in enumerate(parsed_data.get('abstractions', [])):
            node = {
                'id': f'abs_{i}',
                'type': 'abstraction',
                'label': f"λ{abs_data['variable']}",
                'x': i * 2.0,
                'y': 2.0,
                'color': '#e74c3c',
                'size': 1.2
            }
            nodes.append(node)
        
        # Crea nodi per variabili
        for i, var in enumerate(parsed_data.get('variables', [])):
            node = {
                'id': f'var_{var}_{i}',
                'type': 'variable',
                'label': var,
                'x': i * 1.5,
                'y': 0.0,
                'color': '#2ecc71',
                'size': 1.0
            }
            nodes.append(node)
        
        # Crea archi per binding
        for i, abs_data in enumerate(parsed_data.get('abstractions', [])):
            var_name = abs_data['variable']
            # Trova variabili corrispondenti
            for j, var in enumerate(parsed_data.get('variables', [])):
                if var == var_name:
                    edge = {
                        'source': f'abs_{i}',
                        'target': f'var_{var}_{j}',
                        'type': 'binding',
                        'color': '#2c3e50',
                        'weight': 1.0
                    }
                    edges.append(edge)
        
        return nodes, edges
    
    def generate_comparison_data(self, expressions: List[str]) -> Dict:
        """Genera dati per confrontare multiple espressioni."""
        comparisons = []
        
        for expr in expressions:
            reduction_data = self.generate_reduction_animation_data(expr)
            comparisons.append(reduction_data)
        
        return {
            'expressions': expressions,
            'comparisons': comparisons,
            'summary': self._create_comparison_summary(comparisons)
        }
    
    def _create_comparison_summary(self, comparisons: List[Dict]) -> Dict:
        """Crea un riassunto del confronto."""
        return {
            'total_expressions': len(comparisons),
            'reduction_counts': [len(comp['reduction_steps']) for comp in comparisons],
            'normal_forms': [comp['final_form'] for comp in comparisons],
            'all_normal': all(comp['is_normal_form'] for comp in comparisons)
        }

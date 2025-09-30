"""
Modulo per la rappresentazione e manipolazione delle espressioni lambda.
"""

from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum


class NodeType(Enum):
    """Tipi di nodi nel grafo lambda."""
    VARIABLE = "variable"
    ABSTRACTION = "abstraction"
    APPLICATION = "application"


@dataclass
class LambdaNode:
    """Rappresenta un nodo nel grafo lambda."""
    id: str
    node_type: NodeType
    label: str
    x: float = 0.0
    y: float = 0.0
    color: str = "#3498db"
    size: float = 1.0
    connections: List[str] = None
    
    def __post_init__(self):
        if self.connections is None:
            self.connections = []


@dataclass
class LambdaEdge:
    """Rappresenta un arco nel grafo lambda."""
    source: str
    target: str
    edge_type: str = "default"
    color: str = "#2c3e50"
    weight: float = 1.0


class LambdaExpression:
    """Classe per rappresentare e manipolare espressioni lambda."""
    
    def __init__(self, expression: str):
        self.raw_expression = expression
        self.nodes: Dict[str, LambdaNode] = {}
        self.edges: List[LambdaEdge] = []
        self.variables: Dict[str, int] = {}
        self._parse_expression()
    
    def _parse_expression(self):
        """Parsing semplificato dell'espressione lambda."""
        # Implementazione base - da estendere con parser più sofisticato
        self._create_basic_structure()
    
    def _create_basic_structure(self):
        """Crea una struttura base per test."""
        # Esempio: λx.x (identità)
        if "λx.x" in self.raw_expression or "\\x.x" in self.raw_expression:
            self._create_identity_structure()
        elif "λx.λy.x" in self.raw_expression or "\\x.\\y.x" in self.raw_expression:
            self._create_constant_structure()
        else:
            self._create_generic_structure()
    
    def _create_identity_structure(self):
        """Crea la struttura per la funzione identità."""
        # Nodo lambda
        lambda_node = LambdaNode(
            id="lambda_1",
            node_type=NodeType.ABSTRACTION,
            label="λx",
            x=0.0,
            y=0.0,
            color="#e74c3c",
            size=1.2
        )
        
        # Nodo variabile
        var_node = LambdaNode(
            id="var_x",
            node_type=NodeType.VARIABLE,
            label="x",
            x=1.0,
            y=-1.0,
            color="#2ecc71",
            size=1.0
        )
        
        self.nodes = {"lambda_1": lambda_node, "var_x": var_node}
        self.edges = [LambdaEdge("lambda_1", "var_x", "binding")]
    
    def _create_constant_structure(self):
        """Crea la struttura per la funzione costante K."""
        nodes = {
            "lambda_1": LambdaNode("lambda_1", NodeType.ABSTRACTION, "λx", 0.0, 0.0, "#e74c3c", 1.2),
            "lambda_2": LambdaNode("lambda_2", NodeType.ABSTRACTION, "λy", 1.0, 0.0, "#e74c3c", 1.2),
            "var_x": LambdaNode("var_x", NodeType.VARIABLE, "x", 2.0, -1.0, "#2ecc71", 1.0)
        }
        
        edges = [
            LambdaEdge("lambda_1", "lambda_2", "nested"),
            LambdaEdge("lambda_2", "var_x", "binding")
        ]
        
        self.nodes = nodes
        self.edges = edges
    
    def _create_generic_structure(self):
        """Crea una struttura generica per espressioni non riconosciute."""
        # Struttura semplice con un nodo principale
        main_node = LambdaNode(
            id="main",
            node_type=NodeType.ABSTRACTION,
            label=self.raw_expression[:10] + "..." if len(self.raw_expression) > 10 else self.raw_expression,
            x=0.0,
            y=0.0,
            color="#9b59b6",
            size=1.5
        )
        
        self.nodes = {"main": main_node}
        self.edges = []
    
    def to_dict(self) -> Dict:
        """Converte l'espressione in un dizionario per JSON."""
        return {
            "expression": self.raw_expression,
            "nodes": [
                {
                    "id": node.id,
                    "type": node.node_type.value,
                    "label": node.label,
                    "x": node.x,
                    "y": node.y,
                    "color": node.color,
                    "size": node.size,
                    "connections": node.connections
                }
                for node in self.nodes.values()
            ],
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "type": edge.edge_type,
                    "color": edge.color,
                    "weight": edge.weight
                }
                for edge in self.edges
            ]
        }
    
    def get_complexity_metrics(self) -> Dict:
        """Calcola metriche di complessità dell'espressione."""
        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "abstraction_count": sum(1 for node in self.nodes.values() 
                                   if node.node_type == NodeType.ABSTRACTION),
            "variable_count": sum(1 for node in self.nodes.values() 
                                if node.node_type == NodeType.VARIABLE),
            "application_count": sum(1 for node in self.nodes.values() 
                                   if node.node_type == NodeType.APPLICATION),
            "max_depth": self._calculate_max_depth()
        }
    
    def _calculate_max_depth(self) -> int:
        """Calcola la profondità massima dell'espressione."""
        # Implementazione semplificata
        return len([node for node in self.nodes.values() 
                   if node.node_type == NodeType.ABSTRACTION])

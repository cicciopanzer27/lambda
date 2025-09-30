#!/usr/bin/env python3
"""
API per Business Analytics con Lambda Calculus
Endpoint specializzati per analisi di dataset aziendali.
"""

import os
import sys
import logging
import pandas as pd
import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from typing import Dict, Any, List

# Aggiungi il percorso del progetto
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from utils.business_analytics import BusinessLambdaAnalyzer

# Configurazione logging
logger = logging.getLogger(__name__)

# Crea blueprint per le API business
business_bp = Blueprint('business', __name__, url_prefix='/api/business')

# Inizializza analizzatore business
business_analyzer = BusinessLambdaAnalyzer()

@business_bp.route('/models', methods=['GET'])
def get_business_models():
    """Ottiene la lista dei modelli di business disponibili."""
    try:
        models = business_analyzer.business_models
        
        # Formatta i modelli per la risposta
        formatted_models = []
        for name, expression in models.items():
            formatted_models.append({
                "name": name,
                "expression": expression,
                "description": _get_model_description(name),
                "category": _get_model_category(name)
            })
        
        return jsonify({
            "success": True,
            "models": formatted_models,
            "total_models": len(models)
        })
        
    except Exception as e:
        logger.error(f"Errore nel recupero modelli: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@business_bp.route('/models', methods=['POST'])
def create_custom_model():
    """Crea un modello di business personalizzato."""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data or 'expression' not in data:
            return jsonify({
                "success": False,
                "error": "Nome e espressione lambda richiesti"
            }), 400
        
        model_name = data['name']
        lambda_expression = data['expression']
        
        # Crea il modello personalizzato
        result = business_analyzer.create_custom_business_model(model_name, lambda_expression)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Errore nella creazione modello: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@business_bp.route('/analyze/sales', methods=['POST'])
def analyze_sales_data():
    """Analizza dati di vendita."""
    try:
        data = request.get_json()
        
        if not data or 'sales_data' not in data:
            return jsonify({
                "success": False,
                "error": "Dati di vendita richiesti"
            }), 400
        
        # Converte i dati in DataFrame
        sales_df = pd.DataFrame(data['sales_data'])
        
        # Esegue l'analisi
        results = business_analyzer.analyze_sales_data(sales_df)
        
        return jsonify({
            "success": True,
            "analysis_type": "sales",
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Errore nell'analisi vendite: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@business_bp.route('/analyze/inventory', methods=['POST'])
def analyze_inventory_data():
    """Analizza dati di inventario."""
    try:
        data = request.get_json()
        
        if not data or 'inventory_data' not in data:
            return jsonify({
                "success": False,
                "error": "Dati di inventario richiesti"
            }), 400
        
        # Converte i dati in DataFrame
        inventory_df = pd.DataFrame(data['inventory_data'])
        
        # Esegue l'analisi
        results = business_analyzer.analyze_inventory_data(inventory_df)
        
        return jsonify({
            "success": True,
            "analysis_type": "inventory",
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Errore nell'analisi inventario: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@business_bp.route('/apply-model', methods=['POST'])
def apply_business_model():
    """Applica un modello di business ai dati."""
    try:
        data = request.get_json()
        
        if not data or 'model_name' not in data or 'data' not in data:
            return jsonify({
                "success": False,
                "error": "Nome modello e dati richiesti"
            }), 400
        
        model_name = data['model_name']
        input_data = data['data']
        
        # Applica il modello
        result = business_analyzer.apply_business_model(model_name, input_data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Errore nell'applicazione modello: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@business_bp.route('/report', methods=['POST'])
def generate_business_report():
    """Genera un report aziendale completo."""
    try:
        data = request.get_json()
        
        if not data or 'analyses' not in data:
            return jsonify({
                "success": False,
                "error": "Risultati di analisi richiesti"
            }), 400
        
        analyses = data['analyses']
        
        # Genera il report
        report = business_analyzer.generate_business_report(analyses)
        
        return jsonify({
            "success": True,
            "report": report
        })
        
    except Exception as e:
        logger.error(f"Errore nella generazione report: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@business_bp.route('/examples/sales', methods=['GET'])
def get_sales_examples():
    """Ottiene esempi di dati di vendita."""
    try:
        # Crea dati di esempio
        sample_data = {
            "sales_data": [
                {
                    "date": "2024-01-01",
                    "product_id": 1,
                    "price": 25.50,
                    "quantity": 10,
                    "discount": 0.1,
                    "category": "A"
                },
                {
                    "date": "2024-01-02",
                    "product_id": 2,
                    "price": 45.00,
                    "quantity": 5,
                    "discount": 0.0,
                    "category": "B"
                },
                {
                    "date": "2024-01-03",
                    "product_id": 1,
                    "price": 25.50,
                    "quantity": 15,
                    "discount": 0.15,
                    "category": "A"
                }
            ]
        }
        
        return jsonify({
            "success": True,
            "example_data": sample_data,
            "description": "Dati di vendita di esempio per test"
        })
        
    except Exception as e:
        logger.error(f"Errore nella generazione esempi: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@business_bp.route('/examples/inventory', methods=['GET'])
def get_inventory_examples():
    """Ottiene esempi di dati di inventario."""
    try:
        # Crea dati di esempio
        sample_data = {
            "inventory_data": [
                {
                    "product_id": 1,
                    "current_stock": 100,
                    "sold": 15,
                    "received": 20,
                    "quantity": 105,
                    "unit_price": 25.50,
                    "cost_of_goods": 500.00,
                    "avg_inventory": 200.00
                },
                {
                    "product_id": 2,
                    "current_stock": 50,
                    "sold": 8,
                    "received": 10,
                    "quantity": 52,
                    "unit_price": 45.00,
                    "cost_of_goods": 800.00,
                    "avg_inventory": 150.00
                }
            ]
        }
        
        return jsonify({
            "success": True,
            "example_data": sample_data,
            "description": "Dati di inventario di esempio per test"
        })
        
    except Exception as e:
        logger.error(f"Errore nella generazione esempi: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def _get_model_description(model_name: str) -> str:
    """Ottiene la descrizione di un modello."""
    descriptions = {
        "linear_sales": "Modello lineare per calcolo vendite: prezzo × quantità",
        "discount_sales": "Modello vendite con sconto: (prezzo × (1 - sconto)) × quantità",
        "seasonal_sales": "Modello vendite stagionali: prezzo_base × fattore_stagione × quantità",
        "bulk_sales": "Modello vendite all'ingrosso con sconti per quantità",
        "stock_update": "Aggiornamento stock: stock_corrente - venduto + ricevuto",
        "reorder_point": "Punto di riordino: vendite_medie_giornaliere × lead_time + scorta_sicurezza",
        "stock_value": "Valore inventario: quantità × prezzo_unitario",
        "turnover_rate": "Tasso di rotazione: costo_merci / inventario_medio",
        "profit_margin": "Margine di profitto: (ricavi - costi) / ricavi",
        "roi": "Return on Investment: profitto / investimento",
        "growth_rate": "Tasso di crescita: (attuale - precedente) / precedente"
    }
    return descriptions.get(model_name, "Modello di business personalizzato")

def _get_model_category(model_name: str) -> str:
    """Ottiene la categoria di un modello."""
    categories = {
        "linear_sales": "Vendite",
        "discount_sales": "Vendite",
        "seasonal_sales": "Vendite",
        "bulk_sales": "Vendite",
        "stock_update": "Inventario",
        "reorder_point": "Inventario",
        "stock_value": "Inventario",
        "turnover_rate": "Inventario",
        "profit_margin": "Performance",
        "roi": "Performance",
        "growth_rate": "Performance",
        "moving_average": "Analisi Temporale",
        "trend_analysis": "Analisi Temporale",
        "seasonality": "Analisi Temporale",
        "customer_segmentation": "Clustering",
        "product_categorization": "Clustering",
        "market_analysis": "Clustering"
    }
    return categories.get(model_name, "Personalizzato")

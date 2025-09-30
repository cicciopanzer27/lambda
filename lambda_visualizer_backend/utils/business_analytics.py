#!/usr/bin/env python3
"""
Business Analytics con Lambda Calculus
Applica il Lambda Visualizer per analisi di dataset aziendali.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import json

from .correct_lambda_parser import CorrectLambdaParser, CorrectBetaReducer, ReductionStrategy

class BusinessLambdaAnalyzer:
    """Analizzatore di dati aziendali usando Lambda Calculus."""
    
    def __init__(self):
        self.parser = CorrectLambdaParser()
        self.reducer = CorrectBetaReducer(ReductionStrategy.NORMAL_ORDER)
        self.business_models = self._create_business_models()
    
    def _create_business_models(self) -> Dict[str, str]:
        """Crea modelli di business come espressioni lambda."""
        return {
            # Modelli di vendita
            "linear_sales": "\\price.\\quantity.price * quantity",
            "discount_sales": "\\price.\\quantity.\\discount.(price * (1 - discount)) * quantity",
            "seasonal_sales": "\\base_price.\\season_factor.\\quantity.base_price * season_factor * quantity",
            "bulk_sales": "\\price.\\quantity.\\bulk_threshold.\\bulk_discount.if quantity > bulk_threshold then price * (1 - bulk_discount) * quantity else price * quantity",
            
            # Modelli di inventario
            "stock_update": "\\current_stock.\\sold.\\received.current_stock - sold + received",
            "reorder_point": "\\avg_daily_sales.\\lead_time.\\safety_stock.avg_daily_sales * lead_time + safety_stock",
            "stock_value": "\\quantity.\\unit_price.quantity * unit_price",
            "turnover_rate": "\\cost_of_goods.\\avg_inventory.cost_of_goods / avg_inventory",
            
            # Modelli di performance
            "profit_margin": "\\revenue.\\costs.(revenue - costs) / revenue",
            "roi": "\\profit.\\investment.profit / investment",
            "growth_rate": "\\current.\\previous.(current - previous) / previous",
            
            # Modelli di analisi temporale
            "moving_average": "\\data.\\window_size.calculate_moving_average(data, window_size)",
            "trend_analysis": "\\data.\\period.analyze_trend(data, period)",
            "seasonality": "\\data.\\seasonal_period.detect_seasonality(data, seasonal_period)",
            
            # Modelli di clustering e segmentazione
            "customer_segmentation": "\\customer_data.\\criteria.segment_customers(customer_data, criteria)",
            "product_categorization": "\\product_data.\\features.categorize_products(product_data, features)",
            "market_analysis": "\\market_data.\\metrics.analyze_market(market_data, metrics)"
        }
    
    def analyze_sales_data(self, sales_data: pd.DataFrame) -> Dict[str, Any]:
        """Analizza dati di vendita usando modelli lambda."""
        
        results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "data_shape": sales_data.shape,
            "models_applied": [],
            "insights": [],
            "lambda_expressions": {}
        }
        
        # Analisi lineare delle vendite
        if 'price' in sales_data.columns and 'quantity' in sales_data.columns:
            linear_model = self.business_models["linear_sales"]
            results["lambda_expressions"]["linear_sales"] = linear_model
            
            # Calcola vendite totali
            sales_data['total_sales'] = sales_data['price'] * sales_data['quantity']
            total_revenue = sales_data['total_sales'].sum()
            
            results["insights"].append({
                "metric": "total_revenue",
                "value": total_revenue,
                "description": "Ricavi totali calcolati con modello lineare"
            })
        
        # Analisi con sconti
        if 'discount' in sales_data.columns:
            discount_model = self.business_models["discount_sales"]
            results["lambda_expressions"]["discount_sales"] = discount_model
            
            # Calcola vendite con sconto
            sales_data['discounted_sales'] = sales_data['price'] * (1 - sales_data['discount']) * sales_data['quantity']
            discounted_revenue = sales_data['discounted_sales'].sum()
            
            results["insights"].append({
                "metric": "discounted_revenue",
                "value": discounted_revenue,
                "description": "Ricavi con sconti applicati"
            })
        
        # Analisi di crescita
        if len(sales_data) > 1 and 'total_sales' in sales_data.columns:
            growth_model = self.business_models["growth_rate"]
            results["lambda_expressions"]["growth_rate"] = growth_model
            
            # Calcola tasso di crescita
            current_period = sales_data['total_sales'].iloc[-1]
            previous_period = sales_data['total_sales'].iloc[-2]
            growth_rate = (current_period - previous_period) / previous_period if previous_period != 0 else 0
            
            results["insights"].append({
                "metric": "growth_rate",
                "value": growth_rate,
                "description": f"Tasso di crescita: {growth_rate:.2%}"
            })
        
        return results
    
    def analyze_inventory_data(self, inventory_data: pd.DataFrame) -> Dict[str, Any]:
        """Analizza dati di inventario usando modelli lambda."""
        
        results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "data_shape": inventory_data.shape,
            "models_applied": [],
            "insights": [],
            "lambda_expressions": {}
        }
        
        # Analisi stock update
        if all(col in inventory_data.columns for col in ['current_stock', 'sold', 'received']):
            stock_model = self.business_models["stock_update"]
            results["lambda_expressions"]["stock_update"] = stock_model
            
            # Calcola stock aggiornato
            inventory_data['updated_stock'] = inventory_data['current_stock'] - inventory_data['sold'] + inventory_data['received']
            
            results["insights"].append({
                "metric": "total_updated_stock",
                "value": inventory_data['updated_stock'].sum(),
                "description": "Stock totale dopo aggiornamenti"
            })
        
        # Analisi valore inventario
        if all(col in inventory_data.columns for col in ['quantity', 'unit_price']):
            value_model = self.business_models["stock_value"]
            results["lambda_expressions"]["stock_value"] = value_model
            
            # Calcola valore inventario
            inventory_data['item_value'] = inventory_data['quantity'] * inventory_data['unit_price']
            total_inventory_value = inventory_data['item_value'].sum()
            
            results["insights"].append({
                "metric": "total_inventory_value",
                "value": total_inventory_value,
                "description": "Valore totale dell'inventario"
            })
        
        # Analisi turnover
        if all(col in inventory_data.columns for col in ['cost_of_goods', 'avg_inventory']):
            turnover_model = self.business_models["turnover_rate"]
            results["lambda_expressions"]["turnover_rate"] = turnover_model
            
            # Calcola turnover rate
            inventory_data['turnover_rate'] = inventory_data['cost_of_goods'] / inventory_data['avg_inventory']
            avg_turnover = inventory_data['turnover_rate'].mean()
            
            results["insights"].append({
                "metric": "average_turnover_rate",
                "value": avg_turnover,
                "description": f"Tasso di rotazione medio: {avg_turnover:.2f}"
            })
        
        return results
    
    def create_custom_business_model(self, model_name: str, lambda_expression: str) -> Dict[str, Any]:
        """Crea un modello di business personalizzato."""
        
        try:
            # Valida l'espressione lambda
            parsed = self.parser.parse(lambda_expression)
            
            # Testa la riduzione
            test_result = self.reducer.reduce(parsed, max_steps=10)
            
            # Aggiungi al dizionario dei modelli
            self.business_models[model_name] = lambda_expression
            
            return {
                "success": True,
                "model_name": model_name,
                "lambda_expression": lambda_expression,
                "parsed_term": str(parsed),
                "validation_result": test_result,
                "message": f"Modello '{model_name}' creato con successo"
            }
            
        except Exception as e:
            return {
                "success": False,
                "model_name": model_name,
                "lambda_expression": lambda_expression,
                "error": str(e),
                "message": f"Errore nella creazione del modello '{model_name}'"
            }
    
    def apply_business_model(self, model_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Applica un modello di business ai dati."""
        
        if model_name not in self.business_models:
            return {
                "success": False,
                "error": f"Modello '{model_name}' non trovato",
                "available_models": list(self.business_models.keys())
            }
        
        try:
            # Ottieni l'espressione lambda del modello
            lambda_expr = self.business_models[model_name]
            
            # Sostituisci i parametri con i valori dei dati
            substituted_expr = self._substitute_parameters(lambda_expr, data)
            
            # Parsa e riduci
            parsed = self.parser.parse(substituted_expr)
            result = self.reducer.reduce(parsed, max_steps=50)
            
            return {
                "success": True,
                "model_name": model_name,
                "original_expression": lambda_expr,
                "substituted_expression": substituted_expr,
                "result": result['final_term'],
                "steps": result['steps'],
                "is_normal_form": result['is_normal_form'],
                "reduction_steps": result['reduction_steps']
            }
            
        except Exception as e:
            return {
                "success": False,
                "model_name": model_name,
                "error": str(e),
                "message": f"Errore nell'applicazione del modello '{model_name}'"
            }
    
    def _substitute_parameters(self, lambda_expr: str, data: Dict[str, Any]) -> str:
        """Sostituisce i parametri nell'espressione lambda con i valori dei dati."""
        
        # Sostituzioni semplici per i parametri comuni
        substitutions = {
            'price': str(data.get('price', 'price')),
            'quantity': str(data.get('quantity', 'quantity')),
            'discount': str(data.get('discount', 'discount')),
            'current_stock': str(data.get('current_stock', 'current_stock')),
            'sold': str(data.get('sold', 'sold')),
            'received': str(data.get('received', 'received')),
            'revenue': str(data.get('revenue', 'revenue')),
            'costs': str(data.get('costs', 'costs')),
            'profit': str(data.get('profit', 'profit')),
            'investment': str(data.get('investment', 'investment'))
        }
        
        substituted = lambda_expr
        for param, value in substitutions.items():
            substituted = substituted.replace(f'\\{param}', f'\\{value}')
        
        return substituted
    
    def generate_business_report(self, analysis_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Genera un report aziendale completo."""
        
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "total_analyses": len(analysis_results),
            "summary": {
                "total_insights": 0,
                "models_used": set(),
                "key_metrics": {}
            },
            "detailed_results": analysis_results
        }
        
        # Aggrega i risultati
        for result in analysis_results:
            if 'insights' in result:
                report["summary"]["total_insights"] += len(result['insights'])
            
            if 'lambda_expressions' in result:
                report["summary"]["models_used"].update(result['lambda_expressions'].keys())
            
            # Estrai metriche chiave
            for insight in result.get('insights', []):
                metric_name = insight.get('metric')
                metric_value = insight.get('value')
                if metric_name and metric_value is not None:
                    report["summary"]["key_metrics"][metric_name] = metric_value
        
        # Converti set in lista per JSON serialization
        report["summary"]["models_used"] = list(report["summary"]["models_used"])
        
        return report

# Esempi di utilizzo
def create_sample_sales_data() -> pd.DataFrame:
    """Crea dati di vendita di esempio."""
    return pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=30, freq='D'),
        'product_id': np.random.randint(1, 10, 30),
        'price': np.random.uniform(10, 100, 30),
        'quantity': np.random.randint(1, 50, 30),
        'discount': np.random.uniform(0, 0.3, 30),
        'category': np.random.choice(['A', 'B', 'C'], 30)
    })

def create_sample_inventory_data() -> pd.DataFrame:
    """Crea dati di inventario di esempio."""
    return pd.DataFrame({
        'product_id': range(1, 11),
        'current_stock': np.random.randint(0, 100, 10),
        'sold': np.random.randint(0, 20, 10),
        'received': np.random.randint(0, 30, 10),
        'quantity': np.random.randint(10, 200, 10),
        'unit_price': np.random.uniform(5, 50, 10),
        'cost_of_goods': np.random.uniform(100, 1000, 10),
        'avg_inventory': np.random.uniform(50, 500, 10)
    })

# Test e dimostrazione
if __name__ == "__main__":
    # Crea analizzatore
    analyzer = BusinessLambdaAnalyzer()
    
    # Crea dati di esempio
    sales_data = create_sample_sales_data()
    inventory_data = create_sample_inventory_data()
    
    print("=== ANALISI VENDITE ===")
    sales_results = analyzer.analyze_sales_data(sales_data)
    print(json.dumps(sales_results, indent=2, default=str))
    
    print("\n=== ANALISI INVENTARIO ===")
    inventory_results = analyzer.analyze_inventory_data(inventory_data)
    print(json.dumps(inventory_results, indent=2, default=str))
    
    print("\n=== MODELLI DISPONIBILI ===")
    for name, expr in analyzer.business_models.items():
        print(f"{name}: {expr}")

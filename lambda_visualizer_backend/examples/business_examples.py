#!/usr/bin/env python3
"""
Esempi Pratici di Business Analytics con Lambda Calculus
Dimostra come applicare il Lambda Visualizer a dataset aziendali reali.
"""

import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Configurazione
BASE_URL = "http://localhost:5000"

def test_business_analytics():
    """Testa le funzionalità di business analytics."""
    
    print("=" * 60)
    print("BUSINESS ANALYTICS CON LAMBDA CALCULUS")
    print("=" * 60)
    
    # Test 1: Ottieni modelli disponibili
    print("\n1. MODELLI DISPONIBILI")
    print("-" * 30)
    try:
        response = requests.get(f"{BASE_URL}/api/business/models")
        if response.status_code == 200:
            models = response.json()
            print(f"SUCCESS: Trovati {models['total_models']} modelli:")
            for model in models['models'][:5]:  # Mostra primi 5
                print(f"   - {model['name']}: {model['description']}")
        else:
            print(f"Errore: {response.status_code}")
    except Exception as e:
        print(f"Errore connessione: {e}")
    
    # Test 2: Analisi dati di vendita
    print("\n2. ANALISI DATI DI VENDITA")
    print("-" * 30)
    
    sales_data = create_sample_sales_data()
    print(f"📊 Dati vendita creati: {len(sales_data)} record")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/business/analyze/sales",
            json={"sales_data": sales_data.to_dict('records')},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Analisi vendite completata:")
            for insight in result['results']['insights']:
                print(f"   - {insight['metric']}: {insight['value']:.2f}")
        else:
            print(f"❌ Errore: {response.status_code}")
    except Exception as e:
        print(f"❌ Errore: {e}")
    
    # Test 3: Analisi dati di inventario
    print("\n3. ANALISI DATI DI INVENTARIO")
    print("-" * 30)
    
    inventory_data = create_sample_inventory_data()
    print(f"📦 Dati inventario creati: {len(inventory_data)} record")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/business/analyze/inventory",
            json={"inventory_data": inventory_data.to_dict('records')},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Analisi inventario completata:")
            for insight in result['results']['insights']:
                print(f"   - {insight['metric']}: {insight['value']:.2f}")
        else:
            print(f"❌ Errore: {response.status_code}")
    except Exception as e:
        print(f"❌ Errore: {e}")
    
    # Test 4: Applicazione modello personalizzato
    print("\n4. MODELLO PERSONALIZZATO")
    print("-" * 30)
    
    custom_model = "\\price.\\quantity.\\tax.\\shipping.(price * quantity + tax + shipping)"
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/business/models",
            json={
                "name": "total_cost_calculator",
                "expression": custom_model
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ Modello personalizzato creato:")
                print(f"   - Nome: {result['model_name']}")
                print(f"   - Espressione: {result['lambda_expression']}")
                print(f"   - Parsed: {result['parsed_term']}")
            else:
                print(f"❌ Errore: {result['error']}")
        else:
            print(f"❌ Errore HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Errore: {e}")
    
    # Test 5: Applicazione modello ai dati
    print("\n5. APPLICAZIONE MODELLO AI DATI")
    print("-" * 30)
    
    test_data = {
        "price": 25.50,
        "quantity": 10,
        "tax": 2.55,
        "shipping": 5.00
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/business/apply-model",
            json={
                "model_name": "total_cost_calculator",
                "data": test_data
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ Modello applicato con successo:")
                print(f"   - Risultato: {result['result']}")
                print(f"   - Passi: {result['steps']}")
                print(f"   - Forma normale: {result['is_normal_form']}")
            else:
                print(f"❌ Errore: {result['error']}")
        else:
            print(f"❌ Errore HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Errore: {e}")

def create_sample_sales_data():
    """Crea dati di vendita di esempio."""
    np.random.seed(42)  # Per risultati riproducibili
    
    dates = pd.date_range('2024-01-01', periods=30, freq='D')
    
    data = []
    for i, date in enumerate(dates):
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'product_id': np.random.randint(1, 6),
            'price': round(np.random.uniform(10, 100), 2),
            'quantity': np.random.randint(1, 20),
            'discount': round(np.random.uniform(0, 0.3), 2),
            'category': np.random.choice(['A', 'B', 'C']),
            'region': np.random.choice(['Nord', 'Centro', 'Sud']),
            'salesperson_id': np.random.randint(1, 4)
        })
    
    return pd.DataFrame(data)

def create_sample_inventory_data():
    """Crea dati di inventario di esempio."""
    np.random.seed(42)
    
    data = []
    for product_id in range(1, 11):
        data.append({
            'product_id': product_id,
            'product_name': f'Prodotto_{product_id}',
            'current_stock': np.random.randint(0, 100),
            'sold': np.random.randint(0, 20),
            'received': np.random.randint(0, 30),
            'quantity': np.random.randint(10, 200),
            'unit_price': round(np.random.uniform(5, 50), 2),
            'cost_of_goods': round(np.random.uniform(100, 1000), 2),
            'avg_inventory': round(np.random.uniform(50, 500), 2),
            'category': np.random.choice(['Elettronica', 'Abbigliamento', 'Casa', 'Sport']),
            'supplier_id': np.random.randint(1, 4)
        })
    
    return pd.DataFrame(data)

def demonstrate_real_world_scenarios():
    """Dimostra scenari del mondo reale."""
    
    print("\n" + "=" * 60)
    print("SCENARI DEL MONDO REALE")
    print("=" * 60)
    
    # Scenario 1: E-commerce
    print("\n🛒 SCENARIO 1: E-COMMERCE")
    print("-" * 30)
    print("Modelli applicabili:")
    print("- linear_sales: Calcolo vendite base")
    print("- discount_sales: Gestione sconti e promozioni")
    print("- bulk_sales: Sconti per quantità")
    print("- stock_update: Gestione inventario real-time")
    print("- reorder_point: Automazione riordini")
    
    # Scenario 2: Retail
    print("\n🏪 SCENARIO 2: RETAIL")
    print("-" * 30)
    print("Modelli applicabili:")
    print("- seasonal_sales: Analisi vendite stagionali")
    print("- trend_analysis: Identificazione trend")
    print("- customer_segmentation: Segmentazione clienti")
    print("- profit_margin: Analisi margini")
    
    # Scenario 3: Manufacturing
    print("\n🏭 SCENARIO 3: MANUFACTURING")
    print("-" * 30)
    print("Modelli applicabili:")
    print("- stock_value: Valutazione inventario")
    print("- turnover_rate: Efficienza rotazione")
    print("- growth_rate: Analisi crescita")
    print("- roi: Return on Investment")
    
    # Scenario 4: Finance
    print("\n💰 SCENARIO 4: FINANCE")
    print("-" * 30)
    print("Modelli applicabili:")
    print("- profit_margin: Analisi profittabilità")
    print("- roi: Valutazione investimenti")
    print("- growth_rate: Analisi crescita aziendale")
    print("- moving_average: Analisi trend finanziari")

def create_business_dashboard_example():
    """Crea un esempio di dashboard aziendale."""
    
    print("\n" + "=" * 60)
    print("DASHBOARD AZIENDALE ESEMPIO")
    print("=" * 60)
    
    # Simula chiamate API per dashboard
    dashboard_data = {
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "total_revenue": 125000.50,
            "total_orders": 1250,
            "avg_order_value": 100.00,
            "inventory_value": 45000.00,
            "top_selling_product": "Prodotto_A",
            "growth_rate": 0.15,
            "profit_margin": 0.25
        },
        "lambda_models_used": [
            "linear_sales",
            "discount_sales", 
            "stock_value",
            "profit_margin",
            "growth_rate"
        ],
        "insights": [
            "Vendite in crescita del 15% rispetto al mese precedente",
            "Margine di profitto stabile al 25%",
            "Inventario ottimizzato con turnover rate di 2.5",
            "Sconti applicati hanno aumentato le vendite del 20%"
        ]
    }
    
    print("📊 Dashboard Metrics:")
    for metric, value in dashboard_data["metrics"].items():
        if isinstance(value, float):
            print(f"   - {metric}: {value:,.2f}")
        else:
            print(f"   - {metric}: {value}")
    
    print(f"\n🔧 Modelli Lambda utilizzati: {len(dashboard_data['lambda_models_used'])}")
    for model in dashboard_data['lambda_models_used']:
        print(f"   - {model}")
    
    print(f"\n💡 Insights generati: {len(dashboard_data['insights'])}")
    for insight in dashboard_data['insights']:
        print(f"   - {insight}")

if __name__ == "__main__":
    # Esegui test
    test_business_analytics()
    
    # Mostra scenari del mondo reale
    demonstrate_real_world_scenarios()
    
    # Crea esempio dashboard
    create_business_dashboard_example()
    
    print("\n" + "=" * 60)
    print("✅ BUSINESS ANALYTICS DEMO COMPLETATA")
    print("=" * 60)
    print("\nPer utilizzare il sistema:")
    print("1. Avvia il backend: python start_backend.py")
    print("2. Usa gli endpoint /api/business/*")
    print("3. Integra con i tuoi dataset aziendali")
    print("4. Crea modelli personalizzati per le tue esigenze")

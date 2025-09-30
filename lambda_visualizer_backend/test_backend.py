#!/usr/bin/env python3
"""
Script di test per il Lambda Visualizer Backend.
"""

import requests
import json
import time
import sys


def test_backend(base_url="http://localhost:5000"):
    """Testa tutte le funzionalità del backend."""
    
    print("🧪 Test Lambda Visualizer Backend")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Test Health Check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check OK: {data}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Errore connessione: {e}")
        return False
    
    # Test 2: Esempi
    print("\n2. Test Esempi...")
    try:
        response = requests.get(f"{base_url}/api/examples")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Esempi recuperati: {len(data['examples'])} esempi")
            examples = data['examples']
        else:
            print(f"❌ Errore esempi: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Errore esempi: {e}")
        return False
    
    # Test 3: Analisi espressione lambda
    print("\n3. Test Analisi Lambda...")
    test_expression = "λx.x"  # Funzione identità
    
    try:
        response = requests.post(f"{base_url}/api/analyze", 
                               json={"expression": test_expression})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analisi completata per: {test_expression}")
            print(f"   Nodi: {data['metrics']['node_count']}")
            print(f"   Archi: {data['metrics']['edge_count']}")
            analysis_data = data
        else:
            print(f"❌ Errore analisi: {response.status_code}")
            print(f"   Risposta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Errore analisi: {e}")
        return False
    
    # Test 4: Visualizzazione statica
    print("\n4. Test Visualizzazione Statica...")
    try:
        response = requests.post(f"{base_url}/api/visualize/static",
                               json={"expression": test_expression})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Immagine generata: {data['image_id']}")
            image_id = data['image_id']
            
            # Test recupero immagine
            img_response = requests.get(f"{base_url}/api/image/{image_id}")
            if img_response.status_code == 200:
                print(f"✅ Immagine servita correttamente ({len(img_response.content)} bytes)")
            else:
                print(f"❌ Errore nel servire immagine: {img_response.status_code}")
        else:
            print(f"❌ Errore visualizzazione statica: {response.status_code}")
            print(f"   Risposta: {response.text}")
    except Exception as e:
        print(f"❌ Errore visualizzazione statica: {e}")
    
    # Test 5: Visualizzazione video
    print("\n5. Test Visualizzazione Video...")
    try:
        response = requests.post(f"{base_url}/api/visualize",
                               json={
                                   "expression": test_expression,
                                   "config": {
                                       "width": 640,
                                       "height": 480,
                                       "duration": 3.0,
                                       "fps": 15
                                   }
                               })
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Video generato: {data['video_id']}")
            video_id = data['video_id']
            
            # Attendi un po' per la generazione
            print("   Attendendo generazione video...")
            time.sleep(5)
            
            # Test recupero video
            video_response = requests.get(f"{base_url}/api/video/{video_id}")
            if video_response.status_code == 200:
                print(f"✅ Video servito correttamente ({len(video_response.content)} bytes)")
            else:
                print(f"⚠️  Video non ancora pronto o errore: {video_response.status_code}")
        else:
            print(f"❌ Errore visualizzazione video: {response.status_code}")
            print(f"   Risposta: {response.text}")
    except Exception as e:
        print(f"❌ Errore visualizzazione video: {e}")
    
    # Test 6: Lista contenuto
    print("\n6. Test Lista Contenuto...")
    try:
        response = requests.get(f"{base_url}/api/content")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Contenuto listato: {len(data['content'])} file")
        else:
            print(f"❌ Errore lista contenuto: {response.status_code}")
    except Exception as e:
        print(f"❌ Errore lista contenuto: {e}")
    
    # Test 7: Test con diversi esempi
    print("\n7. Test Esempi Diversi...")
    test_expressions = [
        "λx.λy.x",  # Costante K
        "λf.λx.f(f x)",  # Numerale 2
        "λx.λy.λz.(x z)(y z)"  # Combinatore S
    ]
    
    for expr in test_expressions:
        try:
            response = requests.post(f"{base_url}/api/analyze", 
                                   json={"expression": expr})
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {expr}: {data['metrics']['node_count']} nodi")
            else:
                print(f"❌ {expr}: errore {response.status_code}")
        except Exception as e:
            print(f"❌ {expr}: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Test completati!")
    return True


def test_ollama_integration(base_url="http://localhost:5000"):
    """Testa l'integrazione con Ollama."""
    
    print("\n🤖 Test Integrazione Ollama")
    print("=" * 30)
    
    try:
        # Test modelli disponibili
        response = requests.get(f"{base_url}/api/models")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ Modelli Ollama: {data['models']}")
            else:
                print("⚠️  Ollama non disponibile")
        else:
            print(f"❌ Errore modelli: {response.status_code}")
    except Exception as e:
        print(f"❌ Errore test Ollama: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:5000"
    
    print(f"Testing backend at: {base_url}")
    
    success = test_backend(base_url)
    test_ollama_integration(base_url)
    
    if success:
        print("\n✅ Tutti i test principali sono passati!")
        sys.exit(0)
    else:
        print("\n❌ Alcuni test sono falliti!")
        sys.exit(1)

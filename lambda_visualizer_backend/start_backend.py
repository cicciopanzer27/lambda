#!/usr/bin/env python3
"""
Script di avvio semplificato per il backend Lambda Visualizer.
"""

import os
import sys
import logging

# Aggiungi il percorso del progetto
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

try:
    # Import dell'applicazione
    from app.main import app
    
    logger.info("🚀 Avvio Lambda Visualizer Backend...")
    logger.info("📍 URL: http://localhost:5000")
    
    # Avvia l'applicazione
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,  # Disabilita debug per evitare problemi
        threaded=True
    )
    
except ImportError as e:
    logger.error(f"❌ Errore di import: {e}")
    sys.exit(1)
except Exception as e:
    logger.error(f"❌ Errore nell'avvio: {e}")
    sys.exit(1)

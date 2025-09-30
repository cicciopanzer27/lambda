#!/usr/bin/env python3
"""
Startup script for Enhanced Lambda Visualizer
Avvia il sistema completo con tutte le funzionalità integrate.
"""

import os
import sys
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Avvia il sistema enhanced."""
    
    print("Starting Enhanced Lambda Visualizer System")
    print("=" * 60)
    
    try:
        # Import and run the enhanced system
        from app.enhanced_main import EnhancedLambdaVisualizer
        
        # Create the application
        app = EnhancedLambdaVisualizer()
        
        # Run the application
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False  # Set to True for development
        )
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        print("ERROR: Failed to import required modules. Please check dependencies.")
        print("   Install with: pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"System error: {e}")
        print(f"ERROR: System failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

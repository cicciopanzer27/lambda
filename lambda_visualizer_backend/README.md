# Lambda Visualizer Backend

Backend Flask per l'analisi e visualizzazione del Lambda Calculus.

## Stato Tecnico

### ✅ Funzionante
- Parser lambda calculus con tokenizzazione corretta
- Beta reduction engine con strategie multiple
- API REST per analisi espressioni
- Database SQLite per persistenza job
- Sistema di job queue (con errori di serializzazione)

### ⚠️ Parzialmente Funzionante
- Integrazioni Manim/CuPy/FFmpeg (fallback CPU/JSON)
- WebSocket server (non testato in produzione)
- Sistema di visualizzazione (genera output ma non sempre corretto)

### ❌ Non Funzionante
- Serializzazione JSON di oggetti Variable
- Gestione errori completa
- Test di integrazione

## Struttura del Codice

```
lambda_visualizer_backend/
├── app/
│   └── enhanced_main.py          # Flask app principale
├── utils/
│   ├── complete_beta_reduction.py # Parser e beta reduction
│   ├── persistence_system.py     # Database SQLite
│   ├── real_integrations.py      # Manim/CuPy/FFmpeg
│   └── websocket_communication.py # WebSocket server
├── production_system.py          # Sistema produzione
├── start_enhanced.py            # Script avvio
└── requirements.txt             # Dipendenze Python
```

## Installazione

```bash
pip install -r requirements.txt
```

**Dipendenze richieste:**
- `flask==3.0.0`
- `websockets==12.0`
- `flask-socketio==5.3.6`
- `manim==0.18.0` (opzionale)
- `cupy-cuda12x==12.3.0` (opzionale)
- `ffmpeg-python==0.2.0` (opzionale)

## Avvio

```bash
python start_enhanced.py
```

**Note:**
- Manim richiede LaTeX installato
- CuPy richiede CUDA toolkit
- FFmpeg deve essere installato separatamente

## API Endpoints

### Analisi Espressione
```bash
POST /api/analyze
Content-Type: application/json

{
  "expression": "\\x.x",
  "max_steps": 100
}
```

### Job Visualizzazione
```bash
POST /api/visualize
Content-Type: application/json

{
  "expression": "\\x.x",
  "config": {
    "duration": 5.0,
    "quality": "medium_quality"
  }
}
```

### Stato Job
```bash
GET /api/jobs/{job_id}
```

### Health Check
```bash
GET /health
```

## Problemi Conosciuti

### Critici
1. **Serializzazione JSON**: Oggetti Variable non serializzabili
2. **Error Handling**: Gestione errori incompleta
3. **Job Queue**: Errori di serializzazione nei job

### Minori
1. **Integrazioni**: Manim/CuPy/FFmpeg non sempre disponibili
2. **WebSocket**: Server attivo ma non testato
3. **Performance**: CPU-only senza GPU acceleration

## Log e Debug

I log sono configurati per livello INFO. Per debug dettagliato:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Test

```bash
# Test parser
python -c "
from utils.complete_beta_reduction import LambdaParser, BetaReducer
parser = LambdaParser()
reducer = BetaReducer()
term = parser.parse('(\\x.x) a')
result = reducer.reduce(term, max_steps=10)
print(result['final_term'])
"
```

## Limitazioni

- **Parser**: Gestisce solo espressioni semplici-medie
- **Performance**: Fallback CPU quando GPU non disponibile
- **Scalabilità**: Job queue con errori di serializzazione
- **Robustezza**: Fallback system non completo

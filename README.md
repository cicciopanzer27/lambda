# Lambda Visualizer

Sistema per l'analisi e visualizzazione del Lambda Calculus con integrazioni opzionali.

## Stato del Progetto

### ✅ Funzionante
- Parser lambda calculus con tokenizzazione corretta
- Beta reduction engine con strategie multiple (normal order, applicative order)
- API REST per analisi espressioni
- Database SQLite per persistenza job
- Sistema di job queue (con errori di serializzazione)

### ⚠️ Parzialmente Funzionante
- Integrazioni Manim/CuPy/FFmpeg (fallback CPU/JSON)
- WebSocket server (non testato in produzione)
- Sistema di visualizzazione (genera output ma non sempre corretto)

### ❌ Non Funzionante
- Frontend React (conflitti dipendenze, build non funzionante)
- Test di integrazione end-to-end
- Sistema di animazione completo

## Architettura Tecnica

### Backend (`lambda_visualizer_backend/`)
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
└── start_enhanced.py            # Script avvio
```

### Frontend (`lambda-visualizer-advanced/`)
```
lambda-visualizer-advanced/
├── src/
│   ├── components/
│   │   └── LambdaVisualizer.jsx  # Componente principale
│   ├── utils/
│   │   └── websocketClient.js    # Client WebSocket
│   └── App.jsx                   # App React
└── package.json                  # Dipendenze (conflitti)
```

## Installazione

### Backend (Funzionante)

```bash
cd lambda_visualizer_backend
pip install -r requirements.txt
python start_enhanced.py
```

**Dipendenze richieste:**
- `flask==3.0.0`
- `websockets==12.0`
- `flask-socketio==5.3.6`
- `manim==0.18.0` (opzionale)
- `cupy-cuda12x==12.3.0` (opzionale)
- `ffmpeg-python==0.2.0` (opzionale)

**Note:**
- Manim richiede LaTeX installato
- CuPy richiede CUDA toolkit
- FFmpeg deve essere installato separatamente

### Frontend (Non Funzionante)

```bash
cd lambda-visualizer-advanced
npm install  # Fallisce per conflitti dipendenze
```

**Problemi noti:**
- Conflitti tra npm/pnpm/yarn
- Dipendenze incompatibili
- Build system non funzionante

## API Documentazione

### Analisi Espressione
```bash
POST /api/analyze
Content-Type: application/json

{
  "expression": "\\x.x",
  "max_steps": 100
}
```

**Risposta:**
```json
{
  "final_term": "a",
  "steps_taken": 1,
  "is_normal_form": true,
  "analysis": {
    "combinator": "I (Identity)",
    "free_variables": [],
    "bound_variables": ["x"],
    "complexity": 4
  }
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

**Risposta:**
```json
{
  "job_id": "uuid-string",
  "status": "submitted",
  "message": "Job submitted successfully"
}
```

### Stato Job
```bash
GET /api/jobs/{job_id}
```

**Risposta:**
```json
{
  "job_id": "uuid-string",
  "status": "completed",
  "progress": 1.0,
  "result": {
    "output_path": "path/to/output",
    "frames": 120,
    "duration": 5.0
  }
}
```

## Esempi di Test

### Test Parser Corretto
```bash
# Input: (\\x.x) a
# Output: a (corretto)

# Input: (\\x.\\y.x) a b  
# Output: \\y.a (corretto)

# Input: (\\x.x x)
# Output: \\x.x x (corretto)
```

### Test Falliti
```bash
# Input: Espressioni troppo complesse
# Errore: Parse error o timeout

# Input: Job con errori serializzazione
# Errore: Object of type Variable is not JSON serializable
```

## Problemi Conosciuti

### Critici
1. **Frontend**: Conflitti dipendenze, build non funzionante
2. **Serializzazione**: Oggetti Variable non serializzabili in JSON
3. **Error Handling**: Gestione errori incompleta

### Minori
1. **Integrazioni**: Manim/CuPy/FFmpeg non sempre disponibili
2. **WebSocket**: Server attivo ma non testato completamente
3. **Performance**: CPU-only senza GPU acceleration
4. **Testing**: Mancano test di integrazione

## Limitazioni Tecniche

- **Parser**: Gestisce solo espressioni semplici-medie
- **Performance**: Fallback CPU quando GPU non disponibile
- **Scalabilità**: Job queue con errori di serializzazione
- **Robustezza**: Fallback system non completo
- **Frontend**: Non funzionante, richiede refactoring completo

## Contributi

### Priorità Alta
1. Fix frontend build system
2. Risolvi errori serializzazione JSON
3. Aggiungi test di integrazione
4. Migliora error handling

### Priorità Media
1. Documenta API WebSocket
2. Ottimizza performance CPU
3. Migliora gestione dipendenze opzionali

## Licenza

MIT License

## Changelog

### v3.0.0 (30 Settembre 2025)
- ✅ Parser lambda calculus corretto
- ✅ Beta reduction engine funzionante
- ✅ Database SQLite per persistenza
- ❌ Frontend non funzionante
- ❌ Integrazioni parzialmente funzionanti

### v2.0.0 (28 Settembre 2025)
- ❌ Parser con errori di tokenizzazione
- ❌ Beta reduction incorretta
- ❌ Sistema non funzionante

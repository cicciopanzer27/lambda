# Lambda Visualizer Enhanced

Un sistema per l'analisi e visualizzazione del lambda calculus con integrazioni opzionali e comunicazione real-time.

## ⚠️ Stato del Progetto

### ✅ Funzionante
- Parser lambda calculus corretto e funzionante
- Beta reduction engine con strategie multiple
- API REST backend per analisi espressioni
- Database SQLite per persistenza job

### ⚠️ Parzialmente Funzionante
- Integrazioni Manim/CuPy/FFmpeg (fallback CPU/JSON)
- WebSocket server (non testato completamente)
- Sistema job queue (errori serializzazione)

### ❌ Non Funzionante
- Frontend React (conflitti dipendenze, build non funzionante)
- Test di integrazione end-to-end
- Sistema di animazione completo

## 🚀 Caratteristiche Principali

### ✅ Funzionante

1. **Parser Lambda Calculus Corretto**
   - Tokenizzazione corretta delle espressioni
   - Parsing in AST (Abstract Syntax Tree)
   - Gestione corretta delle applicazioni (x x vs xx)

2. **Beta Reduction Engine**
   - Strategie multiple (normal order, applicative order)
   - Alpha conversion per evitare variable capture
   - Sostituzione corretta e completa

3. **API REST Backend**
   - Endpoints per analisi espressioni
   - Database SQLite per persistenza job
   - Sistema di logging configurato

### ⚠️ Parzialmente Funzionante

4. **Integrazioni Opzionali**
   - Manim: Fallback CPU quando non disponibile
   - CuPy: Fallback CPU quando GPU non disponibile
   - FFmpeg: Fallback JSON quando non disponibile

5. **Sistema Job Queue**
   - Database SQLite funzionante
   - Errori di serializzazione JSON (oggetti Variable)

6. **WebSocket Server**
   - Server attivo ma non testato completamente
   - Gestione connessioni implementata

### ❌ Non Funzionante

7. **Frontend React**
   - Conflitti dipendenze (npm/pnpm/yarn)
   - Build system Vite non funzionante
   - Test di integrazione non implementati

## 🏗️ Architettura del Sistema

```
lambda_visualizer_backend/
├── app/
│   ├── main.py                    # Sistema originale
│   └── enhanced_main.py           # Sistema enhanced con tutte le integrazioni
├── utils/
│   ├── persistence_system.py      # Database e gestione job
│   ├── complete_beta_reduction.py # Parser e riduttore beta
│   ├── real_integrations.py       # Manim, CuPy, FFmpeg
│   └── websocket_communication.py # Comunicazione real-time
├── production_system.py           # Sistema production-ready
└── start_enhanced.py             # Script di avvio

lambda-visualizer-advanced/
├── src/
│   ├── components/
│   │   └── LambdaVisualizer.jsx   # Componente React principale
│   └── utils/
│       └── websocketClient.js     # Client WebSocket
└── package.json
```

## 🛠️ Installazione

### Backend

1. **Installa le dipendenze Python:**
```bash
cd lambda_visualizer_backend
pip install -r requirements.txt
```

2. **Dipendenze opzionali per funzionalità complete:**
```bash
# Per Manim (animazioni matematiche)
pip install manim

# Per CuPy (accelerazione GPU) - richiede CUDA
pip install cupy-cuda12x

# Per FFmpeg (generazione video)
# Su Ubuntu/Debian:
sudo apt install ffmpeg
# Su Windows: scarica da https://ffmpeg.org/
```

3. **Avvia il sistema enhanced:**
```bash
python start_enhanced.py
```

### Frontend

1. **Installa le dipendenze Node.js:**
```bash
cd lambda-visualizer-advanced
npm install
```

2. **Avvia il server di sviluppo:**
```bash
npm run dev
```

## 🎯 Utilizzo

### API REST

Il sistema enhanced espone le seguenti API:

#### Analisi Lambda
```bash
POST /api/analyze
{
  "expression": "λx.x",
  "max_steps": 100,
  "strategy": "normal_order"
}
```

#### Sottomissione Job
```bash
POST /api/visualize
{
  "expression": "λx.x",
  "config": {
    "duration": 5.0,
    "quality": "medium_quality",
    "fps": 30
  }
}
```

#### Stato Job
```bash
GET /api/jobs/{job_id}
```

#### Statistiche Sistema
```bash
GET /api/statistics
```

### WebSocket

Connessione: `ws://localhost:8765`

#### Messaggi Supportati

**Client → Server:**
- `job_submit`: Sottomette un job
- `subscribe`: Si sottoscrive agli aggiornamenti
- `ping`: Ping per mantenere la connessione

**Server → Client:**
- `job_update`: Aggiornamento stato job
- `job_completed`: Job completato con risultati
- `job_failed`: Job fallito con errore
- `system_update`: Aggiornamento stato sistema

### Frontend React

Il componente `LambdaVisualizer` fornisce:

- **Input espressioni lambda** con esempi predefiniti
- **Analisi real-time** con beta reduction
- **Visualizzazione progress** dei job
- **Storia job** con risultati
- **Connessione WebSocket** automatica

## 🔧 Configurazione

### Sistema Enhanced

```python
# Configurazione in enhanced_main.py
class SystemConfiguration:
    database_path: str = "./enhanced_lambda_visualizer.db"
    websocket_host: str = "localhost"
    websocket_port: int = 8765
    api_host: str = "0.0.0.0"
    api_port: int = 5000
    max_concurrent_jobs: int = 4
    output_directory: str = "./output"
    video_quality: str = "high"
    max_reduction_steps: int = 1000
    default_strategy: str = "normal_order"
```

### Frontend

```javascript
// Configurazione WebSocket in websocketClient.js
const wsClient = new LambdaVisualizerWebSocketClient('ws://localhost:8765');
```

## 📊 Monitoraggio e Debug

### Logs

Il sistema genera logs dettagliati per:
- Connessioni WebSocket
- Processamento job
- Errori e fallback
- Performance metrics

### Database

Il database SQLite contiene:
- **jobs**: Job e loro stati
- **results**: Risultati e file generati
- **system_state**: Configurazioni sistema
- **performance_metrics**: Metriche di performance

### Health Check

```bash
GET /health
```

Risposta:
```json
{
  "status": "healthy",
  "version": "2.0.0-enhanced",
  "services": {
    "ollama": true,
    "persistence": true,
    "manim": true,
    "gpu": "GPU",
    "websocket": true
  }
}
```

## 🚀 Sistemi di Avvio

### Sviluppo
```bash
# Backend enhanced
python start_enhanced.py

# Frontend
npm run dev
```

### Produzione
```bash
# Sistema completo production-ready
python production_system.py
```

## 🔍 Esempi di Utilizzo

### Espressioni Lambda Supportate

```javascript
// Identità
"λx.x"

// Costante K
"λx.λy.x"

// Falso
"λx.λy.y"

// Combinatore S
"λx.λy.λz.(x z)(y z)"

// Numerale di Church 2
"λf.λx.f(f x)"

// Omega (non termina)
"(λx.x x)(λx.x x)"
```

### Strategie di Riduzione

- **normal_order**: Leftmost outermost (default)
- **applicative_order**: Leftmost innermost
- **call_by_name**: Call by name
- **call_by_value**: Call by value

## 🐛 Troubleshooting

### Problemi Critici

1. **Frontend non funziona**
   - **Problema**: Conflitti dipendenze npm/pnpm/yarn
   - **Sintomi**: `npm install` fallisce, build non funziona
   - **Soluzione**: Non risolto, richiede refactoring completo

2. **Errori serializzazione JSON**
   - **Problema**: `Object of type Variable is not JSON serializable`
   - **Sintomi**: Job falliscono durante l'elaborazione
   - **Soluzione**: Implementare serializzazione custom per oggetti Variable

3. **WebSocket non testato**
   - **Problema**: Server attivo ma non verificato in produzione
   - **Sintomi**: Connessioni potrebbero non funzionare
   - **Soluzione**: Testare completamente il sistema WebSocket

### Problemi Minori

4. **Manim non disponibile**
   - Il sistema usa automaticamente il fallback CPU
   - Installa Manim: `pip install manim`

5. **CuPy non disponibile**
   - Il sistema usa CPU automaticamente
   - Installa CuPy: `pip install cupy-cuda12x`

6. **FFmpeg non disponibile**
   - I video vengono salvati come JSON
   - Installa FFmpeg dal sito ufficiale

### Debug

```bash
# Verifica dipendenze
python -c "import manim; print('Manim OK')"
python -c "import cupy; print('CuPy OK')"

# Test WebSocket
python -m utils.websocket_communication

# Test sistema completo
python -m utils.persistence_system
python -m utils.complete_beta_reduction
python -m utils.real_integrations
```

## 📈 Performance

### Metriche Tracciate

- Tempo di analisi lambda (funzionante)
- Tempo di rendering video (fallback JSON)
- Utilizzo CPU (GPU non sempre disponibile)
- Success rate dei job (con errori serializzazione)
- Latenza WebSocket (non testata)

### Limitazioni Attuali

- **CPU-only**: Accelerazione GPU non sempre disponibile
- **Single-thread**: Elaborazione sequenziale
- **Errori Serializzazione**: Job falliscono per oggetti non serializzabili
- **Frontend**: Non funzionante, nessuna metrica UI

### Ottimizzazioni Implementate

- **Fallback System**: Degradazione graceful quando servizi non disponibili
- **Database Caching**: Risultati salvati nel database SQLite
- **Parser Corretto**: Tokenizzazione e parsing ottimizzati
- **Error Handling**: Gestione errori base implementata

## 🔮 Roadmap

### Priorità Critiche (Da Risolvere)

- [ ] **Fix Frontend**: Risolvi conflitti dipendenze e build system
- [ ] **Serializzazione JSON**: Implementa serializzazione custom per oggetti Variable
- [ ] **Error Handling**: Migliora gestione errori completa
- [ ] **Test di Integrazione**: Aggiungi test end-to-end

### Priorità Alte (Miglioramenti)

- [ ] **WebSocket Testing**: Test completo del sistema WebSocket
- [ ] **Performance**: Ottimizza elaborazione CPU
- [ ] **Documentazione**: Aggiorna documentazione tecnica
- [ ] **Deployment**: Configura sistema di deployment

### Priorità Medie (Funzionalità)

- [ ] Supporto per più strategie di riduzione
- [ ] Visualizzazioni 3D con Three.js
- [ ] Export in formati multipli (GIF, WebM)
- [ ] Integrazione con più AI models
- [ ] Dashboard di monitoraggio avanzata
- [ ] API GraphQL
- [ ] Docker containerization

## 📝 Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedi il file LICENSE per i dettagli.

## 🤝 Contributi

I contributi sono benvenuti! Per favore:

1. Fork del repository
2. Crea un branch per la feature (`git checkout -b feature/AmazingFeature`)
3. Commit delle modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## 📞 Supporto

Per supporto e domande:
- Apri una issue su GitHub
- Controlla la documentazione
- Verifica i logs per errori dettagliati

---

**Lambda Visualizer Enhanced** - Un sistema completo per l'analisi e visualizzazione del lambda calculus con tecnologie moderne e comunicazione real-time.

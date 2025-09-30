# Lambda Visualizer - Documentazione Tecnica

## Panoramica del Sistema

Sistema per l'analisi e visualizzazione del Lambda Calculus con integrazioni opzionali.

## Architettura

### Backend (Flask)
- **API REST**: Endpoints per analisi e visualizzazione
- **Parser Lambda**: Tokenizzazione e parsing corretto
- **Beta Reduction**: Strategie multiple
- **Database**: SQLite per persistenza job
- **Job Queue**: Elaborazione asincrona (con errori)
- **WebSocket**: Comunicazione real-time (non testato)

### Frontend (React)
- **UI**: Interfaccia utente moderna
- **WebSocket Client**: Comunicazione real-time
- **Build System**: Vite (non funzionante)
- **Styling**: Tailwind CSS

## Implementazione Tecnica

### Parser Lambda Calculus
**File**: `lambda_visualizer_backend/utils/complete_beta_reduction.py`

**Funzionalità**:
- Tokenizzazione corretta delle espressioni
- Parsing in AST
- Beta reduction con strategie multiple
- Alpha conversion per evitare capture

**Problemi Risolti**:
- ✅ Tokenizzazione: Separazione corretta variabili
- ✅ Parsing: Gestione applicazioni corrette
- ✅ Beta Reduction: Sostituzione corretta

### Database SQLite
**File**: `lambda_visualizer_backend/utils/persistence_system.py`

**Problemi**:
- ❌ Serializzazione JSON: Oggetti Variable non serializzabili
- ❌ Error Handling: Gestione errori incompleta

### API REST
**File**: `lambda_visualizer_backend/app/enhanced_main.py`

**Problemi**:
- ❌ Error Handling: Gestione errori incompleta
- ❌ Serializzazione: Oggetti non serializzabili

## Problemi Conosciuti

### Critici
1. **Frontend Build**: Non funzionante
2. **Serializzazione JSON**: Oggetti Variable non serializzabili
3. **Error Handling**: Gestione errori incompleta

### Minori
1. **Integrazioni**: Manim/CuPy/FFmpeg non sempre disponibili
2. **Performance**: CPU-only senza GPU acceleration
3. **Testing**: Mancano test di integrazione

## Limitazioni Tecniche

### Parser
- **Complessità**: Gestisce solo espressioni semplici-medie
- **Performance**: CPU-only senza ottimizzazioni

### Database
- **Serializzazione**: Oggetti Python non serializzabili
- **Scalabilità**: SQLite non scalabile

### Frontend
- **Build System**: Vite non funzionante
- **Dipendenze**: Conflitti package manager

## Performance

### Backend
- **CPU**: Elaborazione single-thread
- **Memory**: Gestione memoria base
- **Database**: SQLite file-based

### Frontend
- **Build**: Non funzionante
- **Runtime**: Non testato

## Conclusioni

Il sistema presenta:
- **Parser**: Funzionante e corretto
- **Backend**: Parzialmente funzionante
- **Frontend**: Non funzionante
- **Integrazioni**: Opzionali e non testate

**Raccomandazioni**:
1. Fix frontend build system
2. Risolvi errori serializzazione
3. Migliora error handling
4. Aggiungi test di integrazione

---

# Lambda Visualizer Advanced - Documentazione Tecnica

**Versione:** 2.0.0
**Autore:** cicciopanzer27
**Data:** 28 Settembre 2025

---

## 1. Introduzione

Questa documentazione fornisce una panoramica tecnica approfondita del sistema **Lambda Visualizer Advanced**. L'obiettivo è descrivere l'architettura, i componenti chiave, i flussi di dati e le decisioni di progettazione che hanno guidato lo sviluppo.

## 2. Architettura Generale

Il sistema adotta un'architettura **client-server**, con un backend potente e stateful e un frontend leggero e reattivo.

-   **Backend (Flask):** Gestisce la logica di business, l'analisi delle espressioni, il rendering delle visualizzazioni e l'interazione con i sottosistemi (GPU, Ollama).
-   **Frontend (React):** Fornisce l'interfaccia utente, gestisce l'input dell'utente, invia richieste al backend e visualizza i risultati.

## 3. Backend in Dettaglio

Il backend è costruito attorno a un **motore unificato (`UnifiedEngine`)** che orchestra diversi sottosistemi specializzati.

### 3.1. Unified Engine (`engine/unified_engine.py`)

Questo è il cuore del backend. Le sue responsabilità includono:

-   **Gestione della Coda di Job:** Accetta job di rendering, li mette in coda in base alla priorità e li assegna ai worker.
-   **Orchestrazione dei Sottosistemi:** Coordina `SceneManager`, `GPUAccelerator`, `TemporalController` e `ManimIntegration` per eseguire un job.
-   **Gestione dello Stato:** Mantiene lo stato del motore (es. `READY`, `PROCESSING`, `ERROR`).
-   **Monitoring e Metriche:** Raccoglie e espone metriche sulle performance e l'utilizzo del sistema.

### 3.2. Scene Manager (`engine/scene_manager.py`)

Ispirato a **SwapTube**, questo componente gestisce la creazione e il rendering di "scene" modulari.

-   **Scene Modulari:** Ogni tipo di visualizzazione (es. diagramma base, animazione di riduzione) è una `BaseScene`.
-   **Configurazione di Rendering:** `RenderConfig` definisce parametri come risoluzione, FPS e qualità.
-   **Estensibilità:** È facile aggiungere nuovi tipi di scene ereditando da `BaseScene`.

### 3.3. GPU Accelerator (`engine/gpu_acceleration.py`)

Questo componente astrae i calcoli ad alta intensità, delegandoli alla GPU se disponibile.

-   **Astrazione del Dispositivo:** Rileva automaticamente la presenza di CUDA (tramite CuPy) e fa fallback sulla CPU in caso contrario.
-   **Kernel CUDA:** Contiene codice CUDA (simulato come stringhe) per task specifici come il **force-directed layout** per i grafi.
-   **Job di Calcolo:** `ComputeJob` rappresenta un'unità di lavoro per la GPU (es. `GRAPH_LAYOUT`, `PARTICLE_SIMULATION`).
-   **Esecuzione Asincrona:** I job vengono eseguiti in thread separati per non bloccare il motore principale.

### 3.4. Temporal Controller (`engine/temporal_control.py`)

Ispirato a **SwapTube**, gestisce la dimensione temporale delle animazioni.

-   **Unità Temporali:** Definisce `Macroblock` e `Microblock` per sincronizzare audio e video (concetto da SwapTube).
-   **Timeline di Animazione:** `AnimationTimeline` gestisce keyframe, interpolazione (lineare, cubica, Bezier) e funzioni di easing.
-   **Transizioni di Stato:** `StateTransitionManager` permette transizioni fluide tra stati diversi di una visualizzazione.

### 3.5. Manim Integration (`engine/manim_integration.py`)

Questo componente porta la potenza e l'eleganza di **Manim** nel nostro sistema.

-   **Mobject (Mathematical Object):** Classe base per tutti gli oggetti animabili (`Circle`, `Text`, `LambdaNode`).
-   **AnimationEngine:** Esegue le animazioni definite su Mobjects (es. `Create`, `Transform`, `FadeIn`).
-   **Scene Lambda:** `LambdaScene` è una classe specializzata che usa Mobjects per costruire e animare espressioni lambda.
-   **Colori e Stili:** Include una palette di colori e stili ispirata a Manim per un look professionale.

### 3.6. Modello Dati (`models/lambda_expression.py`)

-   **`LambdaExpression`:** Classe che rappresenta un'espressione lambda. Contiene la logica per:
    -   **Parsing:** Convertire la stringa in una struttura dati interna (grafo di nodi e archi).
    -   **Analisi:** Calcolare metriche come complessità e profondità.
    -   **Trasformazione:** Generare rappresentazioni come dizionari o grafi.

## 4. Frontend in Dettaglio

Il frontend è un'applicazione **Single Page Application (SPA)** costruita con React.

### 4.1. Componenti Principali (`src/App.jsx`)

-   **`App`:** Il componente radice che gestisce lo stato globale dell'applicazione.
-   **Pannello di Input:** `Textarea` per l'espressione e pulsanti per avviare analisi e visualizzazione.
-   **Pannello di Configurazione:** `Select` e `Switch` per configurare qualità, tipo di scena e altre opzioni.
-   **Pannello di Analisi:** `Tabs` per mostrare i risultati dell'analisi (struttura, metriche, riduzione, AI).
-   **Barra Laterale:** Mostra lo stato del sistema, i job in corso e una lista di esempi.

### 4.2. Gestione dello Stato

-   Lo stato è gestito principalmente con il hook `useState` di React per semplicità.
-   Lo stato include l'espressione corrente, i risultati dell'analisi, lo stato dei job e le metriche di sistema.

### 4.3. Comunicazione con il Backend

-   Tutte le comunicazioni avvengono tramite richieste **HTTP (fetch)** all'API RESTful del backend.
-   **Polling:** Il frontend esegue il polling dell'endpoint `/api/jobs/<job_id>/status` per ottenere aggiornamenti sullo stato dei job di rendering.

### 4.4. Stile e UI

-   **Tailwind CSS:** Utilizzato per uno styling rapido e utility-first.
-   **shadcn/ui:** Libreria di componenti React ben progettati e accessibili, costruita su Tailwind CSS.
-   **Framer Motion:** Utilizzata per animazioni fluide e transizioni nell'interfaccia utente.

## 5. Flusso di Dati: Dalla Lambda all'Animazione

1.  **Input Utente:** L'utente inserisce un'espressione lambda (es. `λf.λx.f(x)`) nel frontend.

2.  **Richiesta di Analisi:** Il frontend invia una richiesta POST a `/api/analyze`.

3.  **Analisi Backend:**
    -   `LambdaExpression` parsifica la stringa.
    -   Vengono calcolate metriche e generata la struttura del grafo.
    -   (Opzionale) Ollama fornisce un'analisi semantica.
    -   Il backend risponde con un JSON contenente tutti i dati dell'analisi.

4.  **Richiesta di Visualizzazione:** L'utente clicca su "Animate Reduction". Il frontend invia una richiesta POST a `/api/visualize/reduction` con i dati dell'analisi.

5.  **Job di Rendering nel Backend:**
    -   `UnifiedEngine` crea un `RenderJob`.
    -   Il job viene messo in coda.
    -   Un worker preleva il job.
    -   **GPU:** Se necessario, `GPUAccelerator` calcola il layout del grafo.
    -   **Scene Creation:** `LambdaSceneFactory` crea una scena di animazione di riduzione.
    -   **Manim & Temporal Control:** `AnimationEngine` e `TemporalController` lavorano insieme per generare i frame dell'animazione, interpolando tra i passi di riduzione.
    -   Il risultato (una sequenza di frame in formato JSON) viene salvato.

6.  **Polling e Risultato:**
    -   Il frontend esegue il polling dello stato del job.
    -   Quando il job è `completed`, il frontend richiede il risultato da `/api/jobs/<job_id>/result`.

7.  **Visualizzazione Frontend:**
    -   Il frontend riceve i dati dei frame.
    -   Utilizzando una libreria di rendering (es. HTML5 Canvas o WebGL), il frontend disegna ogni frame, creando l'animazione finale visibile all'utente.

## 6. Decisioni di Progettazione e Compromessi

-   **Simulazione vs. Integrazione Reale:** Per `Manim` e `CuPy`, è stata creata un'architettura di integrazione robusta, ma l'implementazione finale è una **simulazione**. Questo permette di dimostrare l'architettura senza richiedere l'installazione completa di queste complesse dipendenze. L'integrazione reale richiederebbe solo di sostituire le classi simulate con le importazioni reali.

-   **JSON per i Frame:** L'output del rendering è una struttura dati JSON che descrive gli oggetti in ogni frame. Questo è un formato intermedio flessibile. Per un'applicazione di produzione, questo JSON verrebbe convertito in un formato video (es. MP4) o in una sequenza di immagini (PNG).

-   **Polling vs. WebSockets:** È stato scelto il polling per semplicità. In un'applicazione reale con molti utenti, i **WebSockets** sarebbero una soluzione più efficiente per notificare al client lo stato dei job.

-   **Stato nel Frontend:** Per questo progetto, lo stato locale di React è sufficiente. Per applicazioni più complesse, si potrebbe considerare una libreria di gestione dello stato globale come Redux o Zustand.



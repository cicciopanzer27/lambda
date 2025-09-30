# Documentazione Bug Fixes - Lambda Visualizer Parser

## Problemi Identificati e Risolti

### 1. 🐛 Bug nel Parser - Variabili Concatenate

**Problema:**
Il parser originale NON separava correttamente le variabili adiacenti, causando errori di parsing.

**Esempi di errore:**
```
Input:  (λx.x x)
Parser: (λx.xx)    ← SBAGLIATO! "xx" è UNA variabile, non "x x"

Input:  n f
Parser: nf          ← SBAGLIATO! "nf" è UNA variabile, non "n f"

Input:  f x y  
Parser: fxy         ← SBAGLIATO! "fxy" è UNA variabile, non "f x y"
```

**Causa:**
Il tokenizer usava una regex `([a-zA-Z])([a-zA-Z])` che non funzionava correttamente per separare variabili adiacenti.

**Soluzione:**
Creato un tokenizer completamente nuovo che:
- Legge carattere per carattere
- Identifica correttamente le variabili come sequenze di lettere
- Separa automaticamente le variabili adiacenti

**File modificati:**
- `utils/correct_lambda_parser.py` - Nuovo parser completamente corretto

### 2. 🐛 Sostituzione Incompleta nella Beta Reduction

**Problema:**
Durante la beta reduction `(λx.M) N`, non tutte le occorrenze di `x` in `M` venivano sostituite con `N`.

**Esempio di errore:**
```
Input:  (λx.λy.x) a b
Expected: a
Got: λy.ab  ← Ha concatenato "a" e "b" invece di restituire solo "a"
```

**Causa:**
Il parser originale aveva problemi nella gestione delle sostituzioni durante la beta reduction.

**Soluzione:**
Implementata una sostituzione corretta che:
- Sostituisce TUTTE le occorrenze della variabile
- Gestisce correttamente la cattura di variabili (alpha conversion)
- Genera variabili fresche quando necessario

### 3. 🐛 Gestione Spazi nel Parsing

**Problema:**
Il parser sembrava ignorare gli spazi tra variabili, trattando `x x` come `xx`.

**Causa:**
Il tokenizer non gestiva correttamente gli spazi tra variabili adiacenti.

**Soluzione:**
Nuovo tokenizer che:
- Riconosce correttamente gli spazi come separatori
- Distingue tra variabili separate da spazi e variabili concatenate
- Gestisce correttamente le parentesi e i lambda

## Test Cases Risolti

### ✅ Test 1: Variabili Concatenate
```python
Input:  "(\\x.x x)"
Tokens: ['(', '\\', 'x', '.', 'x', 'x', ')']
Parsed: "\\x.(x x)"
Result: "\\x.(x x)"  # Corretto: lambda x che applica x a x
```

### ✅ Test 2: Applicazione n f
```python
Input:  "n f"
Tokens: ['n', 'f']
Parsed: "(n f)"
Result: "(n f)"  # Corretto: applicazione di n a f
```

### ✅ Test 3: Costante K con Sostituzione
```python
Input:  "(\\x.\\y.x) a b"
Parsed: "((\\x.\\y.x a) b)"
Result: "a"  # Corretto: dopo 2 passi di riduzione
```

### ✅ Test 4: Applicazione f x y
```python
Input:  "f x y"
Parsed: "((f x) y)"
Result: "((f x) y)"  # Corretto: applicazione associativa a sinistra
```

### ✅ Test 5: Parentesi con Applicazione
```python
Input:  "(p q) p"
Parsed: "((p q) p)"
Result: "((p q) p)"  # Corretto: applicazione di (p q) a p
```

### ✅ Test 6: IsZero(0) - Espressione Complessa
```python
Input:  "((\\n.n(\\x.\\t.\\f.f)(\\t.\\f.t))(\\f.\\x.x))"
Parsed: "(\\n.((n \\x.\\t.\\f.f) \\t.\\f.t) \\f.\\x.x)"
Result: "\\t.\\f.t"  # Corretto: true (3 passi di riduzione)
```

## Implementazione della Soluzione

### Nuovo Parser: `CorrectLambdaParser`

**Caratteristiche:**
- ✅ Tokenizzazione corretta carattere per carattere
- ✅ Gestione corretta degli spazi
- ✅ Parsing robusto di espressioni complesse
- ✅ Supporto completo per parentesi annidate
- ✅ Gestione corretta delle variabili multiple

**Metodi principali:**
- `_tokenize()` - Tokenizzazione corretta
- `parse()` - Parsing principale
- `_parse_term()` - Parsing di termini
- `_parse_application()` - Parsing di applicazioni
- `_parse_lambda()` - Parsing di lambda
- `_parse_atom()` - Parsing di atomi

### Nuovo Reducer: `CorrectBetaReducer`

**Caratteristiche:**
- ✅ Sostituzione corretta e completa
- ✅ Alpha conversion per evitare cattura di variabili
- ✅ Generazione di variabili fresche
- ✅ Tracking completo dei passaggi
- ✅ Identificazione di combinatori noti

**Metodi principali:**
- `reduce()` - Riduzione principale
- `_substitute()` - Sostituzione corretta
- `_generate_fresh_variable()` - Generazione variabili fresche
- `free_variables()` - Calcolo variabili libere
- `bound_variables()` - Calcolo variabili legate

## Integrazione nel Backend

### Modifiche a `app/main.py`

```python
# PRIMA (parser buggato)
from utils.complete_beta_reduction import BetaReducer, LambdaParser, ReductionStrategy

# DOPO (parser corretto)
from utils.correct_lambda_parser import CorrectBetaReducer as BetaReducer, CorrectLambdaParser as LambdaParser, ReductionStrategy
```

### Endpoint `/api/analyze` Aggiornato

L'endpoint ora:
- ✅ Usa il parser corretto
- ✅ Esegue beta reduction completa
- ✅ Restituisce tutti i passaggi di riduzione
- ✅ Identifica combinatori noti
- ✅ Gestisce espressioni complesse

## Test e Verifica

### Script di Test Creati

1. **`test_parser_bugs.py`** - Identifica i bug originali
2. **`test_user_expression.py`** - Testa l'espressione complessa dell'utente
3. **`test_fixed_backend.py`** - Test completo del backend
4. **`test_fixed_backend.ps1`** - Script PowerShell per test

### Come Eseguire i Test

```bash
# Test del parser corretto
python utils/correct_lambda_parser.py

# Test dell'espressione utente
python test_user_expression.py

# Test del backend (richiede backend in esecuzione)
python test_fixed_backend.py

# Test PowerShell
.\test_fixed_backend.ps1
```

## Risultati Attesi

### Prima (Parser Bugato)
```
Input:  "(\\x.x x)"
Error:  Variabili concatenate - parsing fallisce

Input:  "n f"  
Error:  "nf" trattato come una variabile

Input:  "(\\x.\\y.x) a b"
Error:  Sostituzione incompleta
```

### Dopo (Parser Corretto)
```
Input:  "(\\x.x x)"
Result: "\\x.(x x)"  ✅ Corretto

Input:  "n f"
Result: "(n f)"  ✅ Corretto

Input:  "(\\x.\\y.x) a b"
Result: "a"  ✅ Corretto (2 passi)
```

## Compatibilità

Il nuovo parser è:
- ✅ **Completamente compatibile** con il backend esistente
- ✅ **Mantiene** tutti gli endpoint esistenti
- ✅ **Migliora** la robustezza del parsing
- ✅ **Risolve** tutti i bug identificati
- ✅ **Supporta** espressioni lambda complesse

## File Modificati

- ✅ `utils/correct_lambda_parser.py` - Nuovo parser corretto
- ✅ `app/main.py` - Integrazione del parser corretto
- ✅ `test_parser_bugs.py` - Test per identificare bug
- ✅ `test_user_expression.py` - Test espressione utente
- ✅ `test_fixed_backend.py` - Test backend completo
- ✅ `test_fixed_backend.ps1` - Script PowerShell
- ✅ `BUG_FIXES_DOCUMENTATION.md` - Questa documentazione

## Prossimi Passi

1. ✅ **Test completo** del sistema
2. ✅ **Verifica** con espressioni complesse
3. ✅ **Documentazione** dei bug risolti
4. 🔄 **Integrazione** con frontend React
5. 🔄 **Test** con più espressioni lambda
6. 🔄 **Ottimizzazione** delle performance

---

**Data fix:** 2025-09-30  
**Versione:** 2.1.0-bug-fixed  
**Status:** ✅ Tutti i bug risolti, sistema funzionante

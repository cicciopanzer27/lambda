# Test script per Business Analytics con Lambda Calculus
# Dimostra l'applicazione a dataset aziendali

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Business Analytics con Lambda Calculus" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Ottieni modelli disponibili
Write-Host "1. MODELLI DISPONIBILI" -ForegroundColor Yellow
Write-Host "----------------------" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/business/models" -Method GET
    $result = $response.Content | ConvertFrom-Json
    if ($result.success) {
        Write-Host "✅ Trovati $($result.total_models) modelli:" -ForegroundColor Green
        foreach ($model in $result.models[0..4]) {
            Write-Host "   - $($model.name): $($model.description)" -ForegroundColor White
        }
    } else {
        Write-Host "❌ Errore: $($result.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Errore connessione: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 2: Analisi dati di vendita
Write-Host "2. ANALISI DATI DI VENDITA" -ForegroundColor Yellow
Write-Host "--------------------------" -ForegroundColor Yellow

$salesData = @(
    @{
        date = "2024-01-01"
        product_id = 1
        price = 25.50
        quantity = 10
        discount = 0.1
        category = "A"
    },
    @{
        date = "2024-01-02"
        product_id = 2
        price = 45.00
        quantity = 5
        discount = 0.0
        category = "B"
    },
    @{
        date = "2024-01-03"
        product_id = 1
        price = 25.50
        quantity = 15
        discount = 0.15
        category = "A"
    }
)

$salesBody = @{
    sales_data = $salesData
} | ConvertTo-Json -Depth 3

try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/business/analyze/sales" -Method POST -Body $salesBody -ContentType "application/json"
    $result = $response.Content | ConvertFrom-Json
    if ($result.success) {
        Write-Host "✅ Analisi vendite completata:" -ForegroundColor Green
        foreach ($insight in $result.results.insights) {
            Write-Host "   - $($insight.metric): $($insight.value)" -ForegroundColor White
        }
    } else {
        Write-Host "❌ Errore: $($result.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Errore: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 3: Analisi dati di inventario
Write-Host "3. ANALISI DATI DI INVENTARIO" -ForegroundColor Yellow
Write-Host "-----------------------------" -ForegroundColor Yellow

$inventoryData = @(
    @{
        product_id = 1
        current_stock = 100
        sold = 15
        received = 20
        quantity = 105
        unit_price = 25.50
        cost_of_goods = 500.00
        avg_inventory = 200.00
    },
    @{
        product_id = 2
        current_stock = 50
        sold = 8
        received = 10
        quantity = 52
        unit_price = 45.00
        cost_of_goods = 800.00
        avg_inventory = 150.00
    }
)

$inventoryBody = @{
    inventory_data = $inventoryData
} | ConvertTo-Json -Depth 3

try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/business/analyze/inventory" -Method POST -Body $inventoryBody -ContentType "application/json"
    $result = $response.Content | ConvertFrom-Json
    if ($result.success) {
        Write-Host "✅ Analisi inventario completata:" -ForegroundColor Green
        foreach ($insight in $result.results.insights) {
            Write-Host "   - $($insight.metric): $($insight.value)" -ForegroundColor White
        }
    } else {
        Write-Host "❌ Errore: $($result.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Errore: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 4: Crea modello personalizzato
Write-Host "4. MODELLO PERSONALIZZATO" -ForegroundColor Yellow
Write-Host "-------------------------" -ForegroundColor Yellow

$customModel = @{
    name = "total_cost_calculator"
    expression = "\price.\quantity.\tax.\shipping.(price * quantity + tax + shipping)"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/business/models" -Method POST -Body $customModel -ContentType "application/json"
    $result = $response.Content | ConvertFrom-Json
    if ($result.success) {
        Write-Host "✅ Modello personalizzato creato:" -ForegroundColor Green
        Write-Host "   - Nome: $($result.model_name)" -ForegroundColor White
        Write-Host "   - Espressione: $($result.lambda_expression)" -ForegroundColor White
        Write-Host "   - Parsed: $($result.parsed_term)" -ForegroundColor White
    } else {
        Write-Host "❌ Errore: $($result.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Errore: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 5: Applica modello ai dati
Write-Host "5. APPLICAZIONE MODELLO AI DATI" -ForegroundColor Yellow
Write-Host "-------------------------------" -ForegroundColor Yellow

$testData = @{
    model_name = "total_cost_calculator"
    data = @{
        price = 25.50
        quantity = 10
        tax = 2.55
        shipping = 5.00
    }
} | ConvertTo-Json -Depth 3

try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/business/apply-model" -Method POST -Body $testData -ContentType "application/json"
    $result = $response.Content | ConvertFrom-Json
    if ($result.success) {
        Write-Host "✅ Modello applicato con successo:" -ForegroundColor Green
        Write-Host "   - Risultato: $($result.result)" -ForegroundColor White
        Write-Host "   - Passi: $($result.steps)" -ForegroundColor White
        Write-Host "   - Forma normale: $($result.is_normal_form)" -ForegroundColor White
    } else {
        Write-Host "❌ Errore: $($result.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Errore: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 6: Esempi di dati
Write-Host "6. ESEMPI DI DATI" -ForegroundColor Yellow
Write-Host "-----------------" -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/business/examples/sales" -Method GET
    $result = $response.Content | ConvertFrom-Json
    if ($result.success) {
        Write-Host "✅ Esempi vendite disponibili:" -ForegroundColor Green
        Write-Host "   - Record: $($result.example_data.sales_data.Count)" -ForegroundColor White
        Write-Host "   - Descrizione: $($result.description)" -ForegroundColor White
    }
} catch {
    Write-Host "❌ Errore: $($_.Exception.Message)" -ForegroundColor Red
}

try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/business/examples/inventory" -Method GET
    $result = $response.Content | ConvertFrom-Json
    if ($result.success) {
        Write-Host "✅ Esempi inventario disponibili:" -ForegroundColor Green
        Write-Host "   - Record: $($result.example_data.inventory_data.Count)" -ForegroundColor White
        Write-Host "   - Descrizione: $($result.description)" -ForegroundColor White
    }
} catch {
    Write-Host "❌ Errore: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "SCENARI DEL MONDO REALE" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "🛒 E-COMMERCE:" -ForegroundColor Yellow
Write-Host "   - linear_sales: Calcolo vendite base" -ForegroundColor White
Write-Host "   - discount_sales: Gestione sconti e promozioni" -ForegroundColor White
Write-Host "   - bulk_sales: Sconti per quantità" -ForegroundColor White
Write-Host "   - stock_update: Gestione inventario real-time" -ForegroundColor White
Write-Host ""

Write-Host "🏪 RETAIL:" -ForegroundColor Yellow
Write-Host "   - seasonal_sales: Analisi vendite stagionali" -ForegroundColor White
Write-Host "   - trend_analysis: Identificazione trend" -ForegroundColor White
Write-Host "   - customer_segmentation: Segmentazione clienti" -ForegroundColor White
Write-Host "   - profit_margin: Analisi margini" -ForegroundColor White
Write-Host ""

Write-Host "🏭 MANUFACTURING:" -ForegroundColor Yellow
Write-Host "   - stock_value: Valutazione inventario" -ForegroundColor White
Write-Host "   - turnover_rate: Efficienza rotazione" -ForegroundColor White
Write-Host "   - growth_rate: Analisi crescita" -ForegroundColor White
Write-Host "   - roi: Return on Investment" -ForegroundColor White
Write-Host ""

Write-Host "💰 FINANCE:" -ForegroundColor Yellow
Write-Host "   - profit_margin: Analisi profittabilità" -ForegroundColor White
Write-Host "   - roi: Valutazione investimenti" -ForegroundColor White
Write-Host "   - growth_rate: Analisi crescita aziendale" -ForegroundColor White
Write-Host "   - moving_average: Analisi trend finanziari" -ForegroundColor White
Write-Host ""

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "✅ BUSINESS ANALYTICS TEST COMPLETATO" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Per utilizzare il sistema:" -ForegroundColor Green
Write-Host "1. Avvia il backend: python start_backend.py" -ForegroundColor White
Write-Host "2. Usa gli endpoint /api/business/*" -ForegroundColor White
Write-Host "3. Integra con i tuoi dataset aziendali" -ForegroundColor White
Write-Host "4. Crea modelli personalizzati per le tue esigenze" -ForegroundColor White

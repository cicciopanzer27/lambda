# Test script per calcoli lambda complessi
# Test l'espressione IsZero(0) fornita dall'utente

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Test Lambda Visualizer - Calcoli Complessi" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Espressione semplice (identità)
Write-Host "TEST 1 - Identità: (\x.x) y" -ForegroundColor Yellow
$body1 = '{"expression": "(\\x.x) y", "max_steps": 10}'
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/analyze" -Method POST -Body $body1 -ContentType "application/json"
    $result = $response.Content | ConvertFrom-Json
    if ($result.success) {
        Write-Host "✅ Parsing riuscito!" -ForegroundColor Green
        Write-Host "   Original: $($result.beta_reduction.original_term)" -ForegroundColor White
        Write-Host "   Final: $($result.beta_reduction.final_term)" -ForegroundColor White
        Write-Host "   Steps: $($result.beta_reduction.steps_taken)" -ForegroundColor White
        Write-Host "   Normal form: $($result.beta_reduction.is_normal_form)" -ForegroundColor White
    } else {
        Write-Host "❌ Errore: $($result.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Errore nella richiesta: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 2: Costante K
Write-Host "TEST 2 - Costante K: (\x.\y.x) a b" -ForegroundColor Yellow
$body2 = '{"expression": "(\\x.\\y.x) a b", "max_steps": 10}'
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/analyze" -Method POST -Body $body2 -ContentType "application/json"
    $result = $response.Content | ConvertFrom-Json
    if ($result.success) {
        Write-Host "✅ Parsing riuscito!" -ForegroundColor Green
        Write-Host "   Original: $($result.beta_reduction.original_term)" -ForegroundColor White
        Write-Host "   Final: $($result.beta_reduction.final_term)" -ForegroundColor White
        Write-Host "   Steps: $($result.beta_reduction.steps_taken)" -ForegroundColor White
        Write-Host "   Normal form: $($result.beta_reduction.is_normal_form)" -ForegroundColor White
    } else {
        Write-Host "❌ Errore: $($result.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Errore nella richiesta: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 3: IsZero(0) - Il test complesso dell'utente
Write-Host "TEST 3 - IsZero(0): Espressione complessa" -ForegroundColor Yellow
$body3 = '{"expression": "((\\n.n(\\x.\\t.\\f.f)(\\t.\\f.t))(\\f.\\x.x))", "max_steps": 50}'
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/analyze" -Method POST -Body $body3 -ContentType "application/json"
    $result = $response.Content | ConvertFrom-Json
    if ($result.success) {
        Write-Host "✅ Parsing riuscito!" -ForegroundColor Green
        Write-Host "   Original: $($result.beta_reduction.original_term)" -ForegroundColor White
        Write-Host "   Final: $($result.beta_reduction.final_term)" -ForegroundColor White
        Write-Host "   Steps: $($result.beta_reduction.steps_taken)" -ForegroundColor White
        Write-Host "   Normal form: $($result.beta_reduction.is_normal_form)" -ForegroundColor White
        Write-Host ""
        Write-Host "   Reduction Steps:" -ForegroundColor Cyan
        foreach ($step in $result.beta_reduction.reduction_steps) {
            Write-Host "     Step $($step.step): $($step.term)" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ Errore: $($result.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Errore nella richiesta: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 4: Numerale di Church 2
Write-Host "TEST 4 - Church Numeral 2: (\f.\x.f(f x))" -ForegroundColor Yellow
$body4 = '{"expression": "\\f.\\x.f(f x)", "max_steps": 10}'
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/analyze" -Method POST -Body $body4 -ContentType "application/json"
    $result = $response.Content | ConvertFrom-Json
    if ($result.success) {
        Write-Host "✅ Parsing riuscito!" -ForegroundColor Green
        Write-Host "   Original: $($result.beta_reduction.original_term)" -ForegroundColor White
        Write-Host "   Final: $($result.beta_reduction.final_term)" -ForegroundColor White
        Write-Host "   Steps: $($result.beta_reduction.steps_taken)" -ForegroundColor White
        Write-Host "   Normal form: $($result.beta_reduction.is_normal_form)" -ForegroundColor White
    } else {
        Write-Host "❌ Errore: $($result.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Errore nella richiesta: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Test completati!" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

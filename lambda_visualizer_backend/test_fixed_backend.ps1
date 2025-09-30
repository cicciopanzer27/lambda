# Test script per il backend con parser corretto
# Testa tutti i bug identificati e risolti

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Test Backend con Parser Corretto" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Identità semplice
Write-Host "TEST 1 - Identità: (\x.x) y" -ForegroundColor Yellow
$body1 = '{"expression": "(\\x.x) y", "max_steps": 10}'
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/analyze" -Method POST -Body $body1 -ContentType "application/json"
    $result = $response.Content | ConvertFrom-Json
    if ($result.success) {
        Write-Host "✅ SUCCESS" -ForegroundColor Green
        Write-Host "   Parsed: $($result.parsed_term)" -ForegroundColor White
        Write-Host "   Final: $($result.beta_reduction.final_term)" -ForegroundColor White
        Write-Host "   Steps: $($result.beta_reduction.steps_taken)" -ForegroundColor White
        Write-Host "   Normal form: $($result.beta_reduction.is_normal_form)" -ForegroundColor White
    } else {
        Write-Host "❌ Error: $($result.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 2: Costante K
Write-Host "TEST 2 - Costante K: (\x.\y.x) a b" -ForegroundColor Yellow
$body2 = '{"expression": "(\\x.\\y.x) a b", "max_steps": 10}'
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/analyze" -Method POST -Body $body2 -ContentType "application/json"
    $result = $response.Content | ConvertFrom-Json
    if ($result.success) {
        Write-Host "✅ SUCCESS" -ForegroundColor Green
        Write-Host "   Parsed: $($result.parsed_term)" -ForegroundColor White
        Write-Host "   Final: $($result.beta_reduction.final_term)" -ForegroundColor White
        Write-Host "   Steps: $($result.beta_reduction.steps_taken)" -ForegroundColor White
        Write-Host "   Normal form: $($result.beta_reduction.is_normal_form)" -ForegroundColor White
    } else {
        Write-Host "❌ Error: $($result.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 3: Variabili concatenate (BUG FIX)
Write-Host "TEST 3 - Variabili concatenate: (\x.x x)" -ForegroundColor Yellow
$body3 = '{"expression": "(\\x.x x)", "max_steps": 10}'
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/analyze" -Method POST -Body $body3 -ContentType "application/json"
    $result = $response.Content | ConvertFrom-Json
    if ($result.success) {
        Write-Host "✅ SUCCESS" -ForegroundColor Green
        Write-Host "   Parsed: $($result.parsed_term)" -ForegroundColor White
        Write-Host "   Final: $($result.beta_reduction.final_term)" -ForegroundColor White
        Write-Host "   Steps: $($result.beta_reduction.steps_taken)" -ForegroundColor White
        Write-Host "   Normal form: $($result.beta_reduction.is_normal_form)" -ForegroundColor White
    } else {
        Write-Host "❌ Error: $($result.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 4: Applicazione n f
Write-Host "TEST 4 - Applicazione n f" -ForegroundColor Yellow
$body4 = '{"expression": "n f", "max_steps": 10}'
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/analyze" -Method POST -Body $body4 -ContentType "application/json"
    $result = $response.Content | ConvertFrom-Json
    if ($result.success) {
        Write-Host "✅ SUCCESS" -ForegroundColor Green
        Write-Host "   Parsed: $($result.parsed_term)" -ForegroundColor White
        Write-Host "   Final: $($result.beta_reduction.final_term)" -ForegroundColor White
        Write-Host "   Steps: $($result.beta_reduction.steps_taken)" -ForegroundColor White
        Write-Host "   Normal form: $($result.beta_reduction.is_normal_form)" -ForegroundColor White
    } else {
        Write-Host "❌ Error: $($result.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 5: Applicazione f x y
Write-Host "TEST 5 - Applicazione f x y" -ForegroundColor Yellow
$body5 = '{"expression": "f x y", "max_steps": 10}'
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/analyze" -Method POST -Body $body5 -ContentType "application/json"
    $result = $response.Content | ConvertFrom-Json
    if ($result.success) {
        Write-Host "✅ SUCCESS" -ForegroundColor Green
        Write-Host "   Parsed: $($result.parsed_term)" -ForegroundColor White
        Write-Host "   Final: $($result.beta_reduction.final_term)" -ForegroundColor White
        Write-Host "   Steps: $($result.beta_reduction.steps_taken)" -ForegroundColor White
        Write-Host "   Normal form: $($result.beta_reduction.is_normal_form)" -ForegroundColor White
    } else {
        Write-Host "❌ Error: $($result.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 6: IsZero(0) - Espressione complessa utente
Write-Host "TEST 6 - IsZero(0): Espressione complessa" -ForegroundColor Yellow
$body6 = '{"expression": "((\\n.n(\\x.\\t.\\f.f)(\\t.\\f.t))(\\f.\\x.x))", "max_steps": 50}'
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/analyze" -Method POST -Body $body6 -ContentType "application/json"
    $result = $response.Content | ConvertFrom-Json
    if ($result.success) {
        Write-Host "✅ SUCCESS" -ForegroundColor Green
        Write-Host "   Parsed: $($result.parsed_term)" -ForegroundColor White
        Write-Host "   Final: $($result.beta_reduction.final_term)" -ForegroundColor White
        Write-Host "   Steps: $($result.beta_reduction.steps_taken)" -ForegroundColor White
        Write-Host "   Normal form: $($result.beta_reduction.is_normal_form)" -ForegroundColor White
        Write-Host ""
        Write-Host "   Reduction Steps:" -ForegroundColor Cyan
        foreach ($step in $result.beta_reduction.reduction_steps) {
            Write-Host "     Step $($step.step): $($step.term)" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ Error: $($result.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Test completati!" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

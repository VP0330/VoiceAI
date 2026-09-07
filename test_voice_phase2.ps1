# Test script for Phase 2 voice endpoints
# Run: powershell -ExecutionPolicy Bypass -File test_voice_phase2.ps1

Write-Host "=== Phase 2 Voice Agent Testing ===" -ForegroundColor Cyan

# Test 1: Create voice session
Write-Host "`n1. Creating voice session..." -ForegroundColor Yellow
$session_response = Invoke-WebRequest -Uri http://localhost:8000/api/voice/session/start `
  -Method Post `
  -ContentType "application/json" `
  -Body (@{} | ConvertTo-Json) `
  -UseBasicParsing

$session_data = $session_response.Content | ConvertFrom-Json
$session_id = $session_data.session_id

Write-Host "✓ Session created: $session_id" -ForegroundColor Green
Write-Host "  WebSocket URL: $($session_data.websocket_url)" -ForegroundColor Gray

# Test 2: Get session status
Write-Host "`n2. Checking session status..." -ForegroundColor Yellow
$status_response = Invoke-WebRequest -Uri "http://localhost:8000/api/voice/session/$session_id/status" `
  -Method Get `
  -UseBasicParsing

$status_data = $status_response.Content | ConvertFrom-Json
Write-Host "✓ Session status:" -ForegroundColor Green
Write-Host "  Status: $($status_data.status)" -ForegroundColor Gray
Write-Host "  Insights: $($status_data.insights_count)" -ForegroundColor Gray

# Test 3: Voice processing (requires actual audio file)
Write-Host "`n3. Voice processing (requires audio file)" -ForegroundColor Yellow
Write-Host "  To test voice processing:" -ForegroundColor Gray
Write-Host "  - Prepare a .wav/.mp3 audio file" -ForegroundColor Gray
Write-Host "  - Use: Invoke-WebRequest -Uri http://localhost:8000/api/voice/process -Method Post -Form @{session_id='$session_id'} -File @{audio_file='path/to/audio.wav'}" -ForegroundColor Gray

# Test 4: WebSocket connection test
Write-Host "`n4. WebSocket connection info:" -ForegroundColor Yellow
Write-Host "  URL: $($session_data.websocket_url)" -ForegroundColor Gray
Write-Host "  Use wscat or your client to connect:" -ForegroundColor Gray
Write-Host "  wscat -c $($session_data.websocket_url)" -ForegroundColor Gray
Write-Host "  Then send: {`"type`": `"transcript_turn`", `"speaker`": `"user`", `"text`": `"Hello`"}" -ForegroundColor Gray

Write-Host "`n=== Phase 2 Setup Complete ===" -ForegroundColor Cyan
Write-Host "Backend is ready for voice agent processing!" -ForegroundColor Green
Write-Host "Next: Add Deepgram and ElevenLabs API keys to .env" -ForegroundColor Yellow

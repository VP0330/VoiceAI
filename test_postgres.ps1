$body = @{
    transcript = "Interviewer: Tell me about your biggest achievement. Interviewee: I led a team that improved efficiency by 40% through automation. The team responded positively and morale improved significantly."
    session_id = "postgres-test-$(Get-Date -Format 'yyyyMMddHHmmss')"
} | ConvertTo-Json

Write-Host "Testing /api/analyze endpoint with PostgreSQL..."
$response = Invoke-WebRequest -Uri 'http://localhost:8000/api/analyze' -Method Post -Body $body -ContentType 'application/json' -UseBasicParsing
$result = $response.Content | ConvertFrom-Json
Write-Host ($result | ConvertTo-Json -Depth 10)

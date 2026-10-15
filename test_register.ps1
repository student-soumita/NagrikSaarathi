$headers = @{ "Content-Type" = "application/json" }
$body = '{"full_name": "Soumita Chatterjee", "email": "chatterjeesoumita06@gmail.com", "password": "Test@1234"}'
try {
    $resp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/auth/register" -Method POST -Body $body -Headers $headers
    Write-Host "SUCCESS:" ($resp | ConvertTo-Json)
} catch {
    Write-Host "ERROR:" $_.Exception.Response.StatusCode
    Write-Host $_.ErrorDetails.Message
}

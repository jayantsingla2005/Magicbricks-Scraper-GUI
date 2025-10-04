$ErrorActionPreference = 'Stop'

# GitHub Personal Access Token (PAT) provided by user
$token = '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'

$headers = @{
  Authorization = "token $token"
  'User-Agent' = 'augment-agent'
}

$body = @{ name = 'Magicbricks-Scraper-GUI'; private = $false } | ConvertTo-Json

$response = Invoke-RestMethod -Headers $headers -Method Post -Uri 'https://api.github.com/user/repos' -Body $body -ContentType 'application/json'

# Output the repository HTML URL for downstream steps
$response.html_url


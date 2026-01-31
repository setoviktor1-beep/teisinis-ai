# Script to remove secrets from git history
$file = "TAISYMO_INSTRUKCIJOS.md"

if (Test-Path $file) {
    $content = Get-Content $file -Raw
    
    # Replace actual secrets with placeholders
    $content = $content -replace '599280134086-uhhoa02i9qsskts6e93ubcsqtasor3o9\.apps\.googleusercontent\.com', 'your_google_client_id_here'
    $content = $content -replace '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', 'your_google_client_secret_here'
    $content = $content -replace '599280134086-[a-z0-9]+\.apps\.googleusercontent\.com', 'your_google_client_id_here'
    $content = $content -replace 'GOCSPX-[A-Za-z0-9_-]+', 'your_google_client_secret_here'
    
    Set-Content $file -Value $content -NoNewline
    git add $file
}

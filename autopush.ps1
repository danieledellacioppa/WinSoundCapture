param (
    [string]$commitMessage = "Auto commit"
)

# Verifica se ci sono modifiche da committare
$changes = git status --porcelain

if (-not $changes) {
    Write-Host "No changes to commit." -ForegroundColor Yellow
    exit
}

# Aggiunge tutti i file
git add --all
Write-Host "All changes added to staging."

# Esegue il commit con il messaggio fornito
git commit -m "$commitMessage"
Write-Host "Committed with message: $commitMessage"

# Esegue il push
git push
Write-Host "Changes pushed successfully."

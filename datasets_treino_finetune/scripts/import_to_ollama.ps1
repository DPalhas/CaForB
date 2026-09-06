# import_to_ollama.ps1 — Import the exported GGUF into Ollama (Windows).
#
# Prereqs:
#   1. caforb-v1.Q4_K_M.gguf + Modelfile in this directory
#   2. Ollama running (ollama serve)
#
# Run from datasets_treino_finetune/:
#   powershell -ExecutionPolicy Bypass -File scripts\import_to_ollama.ps1

$ErrorActionPreference = "Stop"

$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$gguf = Join-Path $dir "caforb-v1.Q4_K_M.gguf"
$modelfile = Join-Path $dir "Modelfile"

if (-not (Test-Path $gguf)) {
    Write-Host "ERROR: $gguf not found." -ForegroundColor Red
    Write-Host "Download caforb-v1.Q4_K_M.gguf from the cloud pod into this directory first."
    exit 1
}

Write-Host "Creating Ollama model 'caforb-v1'..."
ollama create caforb-v1 -f $modelfile

Write-Host "Testing..."
ollama run caforb-v1 "Reply with exactly: OK"

Write-Host ""
Write-Host "Done. To switch the app to the new model:"
Write-Host "  In core/services/llm_services.py, set:"
Write-Host "      DEFAULT_MODEL = `"caforb-v1`""

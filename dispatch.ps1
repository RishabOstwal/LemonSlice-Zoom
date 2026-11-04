# Usage: ./dispatch.ps1 ["<zoom link>"] ["Bot name"]
# Prompts for the Zoom link if it isn't passed as an argument.
param(
    [string]$MeetingUrl,
    [string]$BotName = "Lil Spark"
)

Set-Location $PSScriptRoot

if (-not $MeetingUrl) {
    $MeetingUrl = Read-Host "Zoom meeting URL"
}

if (-not $MeetingUrl) {
    Write-Host "A Zoom meeting URL is required."
    exit 1
}

uv run python dispatch.py $MeetingUrl --bot-name $BotName
exit $LASTEXITCODE

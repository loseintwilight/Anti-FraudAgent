$projectDir = "d:\Anti-FraudAgent\antiFraud-ai-agent-main\antiFraud-ai-agent\antiFraud-ai-agent-admin-v2"
$env:CI = "true"
$process = Start-Process -FilePath "node" -ArgumentList "`"$projectDir\node_modules\vite\bin\vite.js`"","build" -NoNewWindow -RedirectStandardOutput "$projectDir\build_stdout.txt" -RedirectStandardError "$projectDir\build_stderr.txt" -WorkingDirectory $projectDir -PassThru
$process.WaitForExit(120000)
Write-Host "Exit code: $($process.ExitCode)"
$outFile = "$projectDir\build_stdout.txt"
$errFile = "$projectDir\build_stderr.txt"
if (Test-Path $outFile) {
    Get-Content $outFile
    Remove-Item $outFile
}
if (Test-Path $errFile) {
    Write-Host "=== STDERR ==="
    Get-Content $errFile
    Remove-Item $errFile
}
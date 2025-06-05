Write-Host "`nPre-validation Checks:"

$filePath = "fqdn_input.txt"

if (-not (Test-Path $filePath)) {
    Write-Host "File not found. Creating sample fqdn_input.txt..."
    @"
a.glb.aa.com 17502
b.glb.aa.com 17502
c.glb.aa.com 17502
"@ | Out-File -Encoding UTF8 $filePath
}

try {
    $lines = Get-Content $filePath -Raw -ErrorAction Stop
    #Write-Host "`nRaw input received from $filePath:`n$lines"
    Write-Host "`nRaw input received from ${filePath}:`n$lines"

}
catch {
    Write-Host "Failed to read from $filePath. Error: $_"
    exit 1
}

$pools = @()
$seen = @{}
$errors = @()
$i = 0

$lines -split "`r?`n" | ForEach-Object {
    $i++
    $line = $_.Trim()
    if ($line -eq "") { return }

    $parts = $line -split "\s+"
    if ($parts.Count -ne 2) {
        $errors += "Line ${i}: Invalid format - '$line'"
        return
    }

    $hostname = $parts[0]
    $portStr  = $parts[1]

    if ($hostname -notmatch "^[a-zA-Z0-9.-]+$") {
        $errors += "Line ${i}: Invalid FQDN - '$hostname'"
        return
    }

    [int]$port = 0
    if (-not [int]::TryParse($portStr, [ref]$port) -or $port -lt 1 -or $port -gt 65535) {
        $errors += "Line ${i}: Invalid TCP port - '$portStr'"
        return
    }

    $key = "$hostname`:$port"
    if ($seen.ContainsKey($key)) {
        $errors += "Line ${i}: Duplicate entry '$key'"
        return
    }

    $seen[$key] = $true

    $pools += @{
        hostname = $hostname
        port     = $port
    }
}
    $outputPath = "pools_output.json"
if ($errors.Count -gt 0) {
    Write-Host "`nValidation failed with the following errors:"
    $errors | ForEach-Object { Write-Host $_ }
   
} else {
    Write-Host "`nValidation passed. Generating output JSON..."


}

try {
    $pools | ConvertTo-Json -Depth 3 | Out-File -FilePath $outputPath -Encoding UTF8 -ErrorAction Stop
    Write-Host "Output written to: $outputPath"
} catch {
    Write-Host "Failed to write output file. Error: $_"
}


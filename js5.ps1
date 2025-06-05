Write-Host "`nPre-validation Checks:"

$filePath = "fqdn_input.txt"

if (-not (Test-Path $filePath)) {
    Write-Host "File not found. Creating sample fqdn_input.txt..."
    @"
o.glb.ac.com 12345
o1.glb.ac.com 12346
u.glb.ac.com 12347
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

# Constants (match Python script)
$localSubnets = @("100.116.121.0/24", "100.124.121.0/24")
$urlRewrites = @(
    @{ regex = "100[.]116[.]123[.]240"; replace = "epm.glb.cala.attmx.avayacloud.com" },
    @{ regex = "100[.]124[.]123[.]240"; replace = "epmgeo.glb.cala.attmx.avayacloud.com" }
)
$headerUpdates = @(
    @{ header = "TerminationURL"; regex = "http"; replace = "https" }
)
$whitelist = '${CONSTANTS:my_whitelist}'

$pools = @{}
$seen = @{}
$errors = @()
$i = 0

$lines -split "`r?`n" | ForEach-Object {
    $i++
    $line = $_.Trim()
    if ($line -eq "") { return }

    $parts = $line -split "\s+"
    if ($parts.Count -lt 2) {
        $errors += "Line ${i}: Invalid format - '$line'"
        return
    }

    $fqdn = $parts[0]
    $portStr = $parts[1]

    # Validate FQDN (basic check for hostname.domain)
    if ($fqdn -notmatch "^(?!-)([a-zA-Z0-9-]{1,63}(?<!-)\.)+[a-zA-Z]{2,63}$") {
        $errors += "Line ${i}: Invalid FQDN - '$fqdn'"
        return
    }

    [int]$port = 0
    if (-not [int]::TryParse($portStr, [ref]$port) -or $port -lt 1 -or $port -gt 65535) {
        $errors += "Line ${i}: Invalid TCP port - '$portStr'"
        return
    }

    # Key to check duplicates (hostname and port)
    $hostname = ($fqdn -split '\.')[0].ToLower()
    $domain = ($fqdn -split '\.', 2)[1]
    $key = "$hostname`:$port"

    if ($seen.ContainsKey($key)) {
        $errors += "Line ${i}: Duplicate hostname '$hostname' and port '$port'"
        return
    }
    $seen[$key] = $true

    # Build poolName
    $baseName = $hostname.ToUpper()
    $poolName = "CUSTOMER_${baseName}_$port"

    # Build escaped fqdn for regex: replace dots with [.]
  $escapedFqdn = $hostname + ((($domain -split '\.') | ForEach-Object { "[.]$_" }) -join "")


    # Add both HTTPS and HTTP pools to dictionary
    foreach ($protocol in @("HTTPS", "HTTP")) {
        $protoLower = if ($protocol -eq "HTTPS") { "https" } else { "http" }
        $poolKey = "${poolName}_$protocol"

        $pools[$poolKey] = @{
            description = "$poolName $protocol Pool Selection"
            excludeLog = $false
            localSubnets = $localSubnets
            poolName = $poolName
            regexUrl = "^${protoLower}://($escapedFqdn):443/"
            urlQueryStringReplaceEncodeFull = $true
            urlQueryStringReplace = $urlRewrites
            responseHeadersUpdate = $headerUpdates
            whitelist = $whitelist
        }
    }
}
$outputPath = "pools_output.json"
    
if ($errors.Count -gt 0) {
    Write-Host "`nValidation failed with the following errors:"
    $errors | ForEach-Object { Write-Host $_ }
    #exit 1
} else {
    Write-Host "`nValidation passed. Generating output JSON..."

    
}
    Write-Host "`n. Generating output JSON..."

    $outputObject = @{ POOLS = $pools }

try {
        $outputObject | ConvertTo-Json -Depth 5 | Out-File -FilePath $outputPath -Encoding UTF8 -ErrorAction Stop
        Write-Host "Output written to: $outputPath"
    }
    catch {
        Write-Host "Failed to write output file. Error: $_"
        exit 1
    }
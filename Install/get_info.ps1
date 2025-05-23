<#
.SYNOPSIS
Get required applications status.

.DESCRIPTION
This script is used to gather system information about the required applications.

#>

# --------------------------------------------------------------------------
<# Note:
  * Accepts input only via the pipeline, either line by line, 
    or as a single, multi-line string.
  * The input is assumed to have a header line whose column names
    mark the start of each field
    * Column names are assumed to be *single words* (must not contain spaces).
  * The header line is assumed to be followed by a separator line
    (its format doesn't matter).
#>
function parse_winget_list {
    [CmdletBinding()]
    param(
        [Parameter(ValueFromPipeline)] [string] $InputObject
    )

    begin {
        Set-StrictMode -Version 1
        $lineNdx = 0
    }

    process {
        $lines = 
            if ($InputObject.Contains("`n")) { $InputObject.TrimEnd("`r", "`n") -split '\r?\n' }
            else { $InputObject }
            
        foreach ($line in $lines) {
            ++$lineNdx
            if ($lineNdx -eq 1) { 
                # header line
                $headerLine = $line 
            }
            elseif ($lineNdx -eq 2) { 
                # separator line
                # Get the indices where the fields start.
                $fieldStartIndices = [regex]::Matches($headerLine, '\b\S').Index

                # Calculate the field lengths.
                $fieldLengths = foreach ($i in 1..($fieldStartIndices.Count-1)) { 
                    $fieldStartIndices[$i] - $fieldStartIndices[$i - 1] - 1
                }

                # Get the column names
                $colNames = foreach ($i in 0..($fieldStartIndices.Count-1)) {
                    if ($i -eq $fieldStartIndices.Count-1) {
                        $headerLine.Substring($fieldStartIndices[$i]).Trim()
                    } else {
                        $headerLine.Substring($fieldStartIndices[$i], $fieldLengths[$i]).Trim()
                    }
                } 
            }
            else {
                # data line
                $oht = [ordered] @{} # ordered helper hashtable for object constructions.
                $i = 0
                foreach ($colName in $colNames) {
                    $oht[$colName] = 
                        if ($fieldStartIndices[$i] -lt $line.Length) {
                            if ($fieldLengths[$i] -and $fieldStartIndices[$i] + $fieldLengths[$i] -le $line.Length) {
                                $line.Substring($fieldStartIndices[$i], $fieldLengths[$i]).Trim()
                            }
                            else {
                                $line.Substring($fieldStartIndices[$i]).Trim()
                            }
                        }
                    ++$i
                }
                # Convert the helper hashable to an object and output it.
                [pscustomobject] $oht
            }
        }
    }
}

# ...existing code...

[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new() 

# Test if winget is available
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    # display message with hyperlink 
    Write-Host "Winget not activated. Please install winget and try again."
    Write-Host "Access: https://learn.microsoft.com/en-us/windows/package-manager/winget/"
    exit 1
}

# Parse the winget list output into object
$wgl = (winget list) -match '^(\p{L}|-)' | parse_winget_list | Sort-Object Id

# Initialize the result object with the applications to check
$result = @{
    "Microsoft.WSL" = @{
        Name = ""
        Installed = $false
        Version = $null
    }
    "RedHat.Podman" = @{
        Name = ""
        Installed = $false
        Version = $null
    }
    "Anaconda.Miniconda3" = @{
        Name = ""
        Installed = $false
        Version = $null
    }
    "Git.Git" = @{
        Name = ""
        Installed = $false
        Version = $null
    }

    # Add more applications here if needed
}

# Create the applications list from the keys of the result object
$applications = $result.Keys

# Get the keys from the first object in $wgl
$keys = $wgl[0].PSObject.Properties.Name

# Iterate over the applications and update the result object
foreach ($app in $applications) {
    $appInfo = $wgl | Where-Object { $_.Id -eq $app }
    if ($null -eq $appInfo) {
        Write-Host "$app is not installed."
    } else {
        $appName = $appInfo."$($keys[0])" # Access the property dynamically using the indexed key to avoid problem with localization
        $appVersion = $appInfo."$($keys[2])"  
        

        $result.$app.Name = $appName
        $result.$app.Installed = $true
        $result.$app.Version = $appVersion
        Write-Host "$app is installed. Version: $appVersion"
    }
}

$indexedKeys.GetEnumerator() | ForEach-Object { Write-Host "$($_.Key): $($_.Value)" }
# Convert the result object to JSON and save it to a file
$jsonOutput = $result | ConvertTo-Json -Depth 3
$jsonOutput | Out-File -FilePath "D:/github/webRotas/Install/output.json"
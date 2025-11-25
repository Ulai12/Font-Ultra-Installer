# SystemOps.ps1
param(
    [string]$Command,
    [string]$FontPath,
    [string]$FontName
)

function Register-Font {
    param($Path, $Name)
    try {
        $dest = Join-Path $env:WINDIR\Fonts (Split-Path $Path -Leaf)
        
        # Copy if not in Fonts folder
        if ($Path -ne $dest) {
            Copy-Item -Path $Path -Destination $dest -Force -ErrorAction Stop
        }

        # Registry
        $regName = $Name + " (TrueType)" # Simplification, ideally we detect type
        New-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts' `
            -Name $regName -PropertyType String -Value (Split-Path $dest -Leaf) -Force | Out-Null
            
        Write-Host "SUCCESS"
    } catch {
        Write-Host "ERROR: $_"
        exit 1
    }
}

function Restart-Explorer {
    Stop-Process -Name explorer -Force
    Write-Host "RESTARTED"
}

function Unregister-Font {
    param($FontName, $FileName)
    try {
        $regPath = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts'
        
        # 1. Remove from Registry
        # We need to find the exact registry key. $FontName might be the key name or part of it.
        # If we have the exact key name, great. If not, we search by value ($FileName).
        
        $targetKey = $null
        $props = Get-ItemProperty -Path $regPath
        foreach ($prop in $props.PSObject.Properties) {
            if ($prop.Value -eq $FileName) {
                $targetKey = $prop.Name
                break
            }
        }

        if ($targetKey) {
            Remove-ItemProperty -Path $regPath -Name $targetKey -Force -ErrorAction Stop
        }

        # 2. Delete File
        $fontPath = Join-Path $env:WINDIR\Fonts $FileName
        if (Test-Path $fontPath) {
            Remove-Item -Path $fontPath -Force -ErrorAction SilentlyContinue
        }
            
        Write-Host "SUCCESS"
    } catch {
        Write-Host "ERROR: $_"
        exit 1
    }
}

if ($Command -eq "register") {
    Register-Font -Path $FontPath -Name $FontName
} elseif ($Command -eq "unregister") {
    # For unregister, FontPath acts as FileName (e.g. arial.ttf)
    Unregister-Font -FileName $FontPath 
} elseif ($Command -eq "restart-explorer") {
    Restart-Explorer
} else {
    Write-Host "Unknown command"
    exit 1
}

#
# Import Az modules when not in CloudShell
#

if ([string]::IsNullOrEmpty($Env:ACC_VERSION)) {
    Write-Host
    Write-Host "Importing Az modules"

    Import-Module Az
    Import-Module Az.ApplicationInsights
    Import-Module Az.CosmosDB
    Import-Module Az.Network
    Import-Module Az.Resources
    Import-Module Az.Storage
    Import-Module Az.Websites
}
else {
    # When running in CloudShell we don't need to import Az modules
    Write-Host
    Write-Host "Running in CloudShell"
}

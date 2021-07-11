<#
   .SYNOPSIS
    This script is used to centralize all environment configuration for other scripts

   .PARAMETER Environment
        DEV
#>

param(
    [string] $Environment
)

$ErrorActionPreference = "Stop"

#
# Select environment if not provided as parameter
#

if ([string]::IsNullOrWhiteSpace($Environment)) {
    $message = "Select the environment to configure:"
    $options = [System.Management.Automation.Host.ChoiceDescription[]] @("&DEV", "&TST")

    $result = $host.UI.PromptForChoice("Environment", $message, $options, 0) 
    $Environment = $options[$result].Label.Replace("&", "")
}

#
# Environment independent settings
#

$global:Environment = $Environment

$global:organizationAbbr = "EMA"
$global:platformAbbr = "DAP"
$global:projectName = "ePI"
$global:projectAbbr = "ePI"

$global:resourceNamePrefix = (`
    $global:organizationAbbr + "-" + `
    $global:platformAbbr + "-" + `
    $global:projectAbbr + "-" + `
    $Environment `
    ).ToLowerInvariant()
$global:convResourceNamePrefix = $resourceNamePrefix + "-conv"
$global:fhirResourceNamePrefix = $resourceNamePrefix + "-fhir"

$global:resourceGroupLocation = "West Europe"
$global:resourceGroupLocationAbbr = "we"

#
# Environment specific settings
# (may overwrite some environment independent settings!)
#

switch ($Environment) {
    "DEV" {
        $global:tenantId = "4efbf65c-4a81-4f2d-835a-e8630de67663" # EMA test tenant
        $global:subscriptionId = "cbc0681b-7fea-4d32-ac52-6276bb0c2996" # EMA test subscription
        
        $global:convResourceGroupName = "dev-dap-epi-proto-00001-rg"
        $global:fhirResourceGroupName = "dev-dap-epi-proto-00002-rg"

        $global:fhirAppServicePlanSku = "B1"
    }
    "TST" {
        $global:tenantId = "4efbf65c-4a81-4f2d-835a-e8630de67663" # EMA test tenant
        $global:subscriptionId = "cbc0681b-7fea-4d32-ac52-6276bb0c2996" # EMA test subscription
        
        $global:convResourceGroupName = "test-dap-epi-proto-00001-rg"
        $global:fhirResourceGroupName = "test-dap-epi-proto-00002-rg"

        $global:fhirAppServicePlanSku = "S1"
    }
    default {
        Write-Host
        Write-Host -ForegroundColor Red "*** ERROR! Script aborted! ***"
        Write-Host -ForegroundColor Red "Unknown environment $($Environment)!"
        exit 1
    }
}

#
# Derived settings
#

$global:resourceTags = @{
    Platform  = $global:platformAbbr
    Project = $global:projectName
    Environment = $Environment
}

$global:convLogAnalyticsWsName = $convResourceNamePrefix + "-laws"
$global:convAppInsightsName = $convResourceNamePrefix + "-appinsight"

$global:fhirLogAnalyticsWsName = $fhirResourceNamePrefix + "-laws"
$global:fhirAppInsightsName = $fhirResourceNamePrefix + "-appinsight"

$global:convStorageAccountName = $convResourceNamePrefix.Replace("-", "") + "sa"
$global:fhirStorageAccountName = $fhirResourceNamePrefix.Replace("-", "") + "sa"

$global:convASPName = $convResourceNamePrefix + "-asp"
$global:convAppName = $convResourceNamePrefix + "-app"

$global:fhirASPName = $fhirResourceNamePrefix + "-asp"
$global:fhirAPIName = $fhirResourceNamePrefix + "-api"
$global:fhirAPIUrl = "https://$($fhirAPIName).azurewebsites.net"
$global:fhirAPIMName = $fhirResourceNamePrefix + "-apim"
$global:fhirDBName = $fhirResourceNamePrefix + "-cosmosdb"
$global:fhirKeyVaultName = $fhirResourceNamePrefix + "-kv"
$global:fhirSPAName = $fhirResourceNamePrefix + "-web"

#
# Names for KeyVault secrets
#

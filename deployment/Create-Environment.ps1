<#
   .SYNOPSIS
    Creates an Azure environment for Fronius Charger Connectivity

   .PARAMETER Environment
        DEV
        TEST
        QA
        PROD
#>

param(
    [string] $Environment,

    #
    # Flags for deploying only selected resources
    #

    [bool]$DeployConvResourceGroup = $true,
    [bool]$DeployFhirResourceGroup = $true,

    [bool]$DeployConvLogAnalyticsWs = $true,
    [bool]$DeployFhirLogAnalyticsWs = $true,

    [bool]$DeployConvStorageAccount = $true,
    [bool]$DeployFhirStorageAccount = $true,

    [bool]$DeployConvASP = $true,
    [bool]$DeployConvFunctionApp = $true,

    [bool]$DeployFhirServer = $true,
    [bool]$DeployAPIM = $true,
    [bool]$DeploySPA = $true
)

Clear-Host

$ErrorActionPreference = "Stop"

#region Get environment configuration, import necessary modules and login to Azure

& $PSScriptRoot\Get-EnvironmentConfig.ps1 -Environment $Environment

& $PSScriptRoot\Scriptlets\Import-AzModules.ps1
Import-Module $PSScriptRoot\Scriptlets\ArmHelpers.psm1 -Force
Import-Module $PSScriptRoot\Scriptlets\KeyVaultHelpers.psm1 -Force

& $PSScriptRoot\Scriptlets\Connect-Subscription.ps1

Write-Host "Signed in as"
Get-AzContext

#endregion

#region DeployConvResourceGroup

if ($DeployConvResourceGroup) {
    Write-Host
    Write-Host "Check for existing resource group: '$convResourceGroupName'"
    $resourceGroup = Get-AzResourceGroup | Where-Object { $_.ResourceGroupName -eq $convResourceGroupName }
    if (!$resourceGroup) {
        Write-Host "Creating resource group '$convResourceGroupName' in location '$resourceGroupLocation'"
        New-AzResourceGroup -Name $convResourceGroupName `
            -Location $resourceGroupLocation `
            -Tag $resourceTags
    }
    else {
        Write-Host "Using existing resource group: '$convResourceGroupName'"
    }
}

#endregion

#region DeployFhirResourceGroup

if ($DeployFhirResourceGroup) {
    Write-Host
    Write-Host "Check for existing resource group: '$fhirResourceGroupName'"
    $resourceGroup = Get-AzResourceGroup | Where-Object { $_.ResourceGroupName -eq $fhirResourceGroupName }
    if (!$resourceGroup) {
        Write-Host "Creating resource group '$fhirResourceGroupName' in location '$resourceGroupLocation'"
        New-AzResourceGroup -Name $fhirResourceGroupName `
            -Location $resourceGroupLocation `
            -Tag $resourceTags
    }
    else {
        Write-Host "Using existing resource group: '$fhirResourceGroupName'"
    }
}

#endregion

#region DeployConvLogAnalyticsWs

if ($DeployConvLogAnalyticsWs) {
    $logAnalyticsParams = @{
        logAnalyticsWsName = $convLogAnalyticsWsName
        appInsightsName    = $convAppInsightsName
        resourceTags       = $resourceTags
    }
    New-ArmDeployment -BaseName "ConvLogAnalyticsWorkspace" `
        -ResourceGroupName $convResourceGroupName `
        -TemplateFilePath "$PSScriptRoot\Templates\LogAnalyticsWs.json" `
        -TemplateParams $logAnalyticsParams
}

#endregion

#region DeployFhirLogAnalyticsWs

if ($DeployFhirLogAnalyticsWs) {
    $logAnalyticsParams = @{
        logAnalyticsWsName = $fhirLogAnalyticsWsName
        appInsightsName    = $fhirAppInsightsName
        resourceTags       = $resourceTags
    }
    New-ArmDeployment -BaseName "FhirLogAnalyticsWorkspace" `
        -ResourceGroupName $fhirResourceGroupName `
        -TemplateFilePath "$PSScriptRoot\Templates\LogAnalyticsWs.json" `
        -TemplateParams $logAnalyticsParams
}

#endregion

#region DeployConvStorageAccount

if ($DeployConvStorageAccount) {
    $storageAccountParams = @{
        storageAccountName = $convStorageAccountName 
        storageAccountType = "Standard_LRS"
        resourceTags       = $resourceTags
    }
    New-ArmDeployment -BaseName "ConvStorageAccount" `
        -ResourceGroupName $convResourceGroupName `
        -TemplateFilePath "$PSScriptRoot\Templates\StorageAccountConv.json" `
        -TemplateParams $storageAccountParams
}

#endregion

#region DeployFhirStorageAccount

if ($DeployFhirStorageAccount) {
    $storageAccountParams = @{
        storageAccountName = $fhirStorageAccountName 
        storageAccountType = "Standard_LRS"
        resourceTags       = $resourceTags
    }
    New-ArmDeployment -BaseName "FhirStorageAccount" `
        -ResourceGroupName $fhirResourceGroupName `
        -TemplateFilePath "$PSScriptRoot\Templates\StorageAccountFhir.json" `
        -TemplateParams $storageAccountParams
}

#endregion

#region DeployConvASP

if ($DeployConvASP) {
    $appServicePlanParams = @{
        appServicePlanName = $convASPName
        resourceTags       = $resourceTags
    }
    New-ArmDeployment -BaseName "ConvASP" `
        -ResourceGroupName $convResourceGroupName `
        -TemplateFilePath "$PSScriptRoot\Templates\AppServicePlanConv.json" `
        -TemplateParams $appServicePlanParams
}

#endregion

#region DeployConvFunctionApp

if ($DeployConvFunctionApp) {
    $appParams = @{
        appName            = $convAppName
        appServicePlanName = $convASPName
        appInsightsName    = $convAppInsightsName
        storageAccountName = $convStorageAccountName
        resourceTags       = $resourceTags
    }
    New-ArmDeployment -BaseName "ConvFunctionApp" `
        -ResourceGroupName $convResourceGroupName `
        -TemplateFilePath "$PSScriptRoot\Templates\FunctionAppConv.json" `
        -TemplateParams $appParams
}

#endregion

#region DeployFhirServer

if ($DeployFhirServer) {
    $fhirAppInsights = Get-AzApplicationInsights -ResourceGroupName $fhirResourceGroupName -Name $fhirAppInsightsName
    $fhirAppInsightsKey = $fhirAppInsights.InstrumentationKey

    $fhirServerParams = @{
        serviceName        = $fhirAPIName 
        appServicePlanName = $fhirASPName
        appServicePlanSku  = $fhirAppServicePlanSku
        appInsightsKey     = $fhirAppInsightsKey
        dbName             = $fhirDBName
        keyVaultName       = $fhirKeyVaultName
        fhirVersion        = "R5"
        resourceTags       = $resourceTags
    }
    New-ArmDeployment -BaseName "FhirServer" `
        -ResourceGroupName $fhirResourceGroupName `
        -TemplateFilePath "$PSScriptRoot\Templates\FhirServer.json" `
        -TemplateParams $fhirServerParams
}

#endregion

#region DeployAPIM

if ($DeployAPIM) {
    $policyApiRead = @"
<policies>
    <inbound>
        <base />
    </inbound>
    <backend>
        <base />
    </backend>
    <outbound>
        <base />
        <!-- Change FHIR-API urls in response to APIM urls -->
        <redirect-content-urls />
    </outbound>
    <on-error>
        <base />
    </on-error>
</policies>
"@

    $policyApiWrite = @"
<policies>
    <inbound>
        <base />
    </inbound>
    <backend>
        <base />
    </backend>
    <outbound>
        <base />
        <!-- Change FHIR-API urls in response to APIM urls -->
        <redirect-content-urls />
    </outbound>
    <on-error>
        <base />
    </on-error>
</policies>
"@

    $policyProductExternalRead = @"
<policies>
    <inbound>
        <base />
        <!-- Limit calls per subscription to 20 per minute and 20.000 per month -->
        <rate-limit calls="20" renewal-period="60" remaining-calls-variable-name="remainingCallsPerSubscription" />
        <quota calls="20000" renewal-period="2629800" />
    </inbound>
    <backend>
        <base />
    </backend>
    <outbound>
        <base />
    </outbound>
    <on-error>
        <base />
    </on-error>
</policies>
"@

$policyProductExternalWrite = @"
<policies>
    <inbound>
        <base />
        <!-- Limit calls per subscription to 20 per minute and 20.000 per month -->
        <rate-limit calls="20" renewal-period="60" remaining-calls-variable-name="remainingCallsPerSubscription" />
        <quota calls="20000" renewal-period="2629800" />
    </inbound>
    <backend>
        <base />
    </backend>
    <outbound>
        <base />
    </outbound>
    <on-error>
        <base />
    </on-error>
</policies>
"@

$policyProductWebRead = @"
<policies>
    <inbound>
        <base />
        <!-- Limit calls per ip-address to 20 per minute and 20.000 per month -->
        <rate-limit-by-key calls="20"
                           renewal-period="60"
                           counter-key="@(context.Request.IpAddress)"
                           remaining-calls-variable-name="remainingCallsPerIP" />
        <quota-by-key calls="20000"
                      renewal-period="2629800"
                      counter-key="@(context.Request.IpAddress)" />
        <!-- Configure CORS for SPA -->
        <cors allow-credentials="true">
            <allowed-origins>
                <origin>https://$($fhirSPAName).azurewebsites.net</origin>
            </allowed-origins>
        </cors>
    </inbound>
    <backend>
        <base />
    </backend>
    <outbound>
        <base />
    </outbound>
    <on-error>
        <base />
    </on-error>
</policies>
"@

    $apimParams = @{
        apimName                   = $fhirAPIMName
        policyApiRead              = $policyApiRead
        policyApiWrite             = $policyApiWrite
        policyProductExternalRead  = $policyProductExternalRead
        policyProductExternalWrite = $policyProductExternalWrite
        policyProductWebRead       = $policyProductWebRead
        resourceTags               = $resourceTags
    }
    New-ArmDeployment -BaseName "APIM" `
        -ResourceGroupName $fhirResourceGroupName `
        -TemplateFilePath "$PSScriptRoot\Templates\APIM.json" `
        -TemplateParams $apimParams

    Write-Host
    $apimContext = New-AzApiManagementContext -ResourceGroupName $fhirResourceGroupName -ServiceName $fhirAPIMName
        
    Write-Host "Deleting initial 'Echo API' in APIM '$fhirAPIMName'"
    $api = Get-AzApiManagementApi -Context $apimContext -ApiId "echo-api" -ErrorAction SilentlyContinue
    if ($api) {
        Remove-AzApiManagementApi -Context $apimContext -ApiId "echo-api"
    }
    
    Write-Host "Deleting initial 'Starter' product in APIM '$fhirAPIMName'"
    $product = Get-AzApiManagementProduct -Context $apimContext -ProductId "starter" -ErrorAction SilentlyContinue
    if ($product) {
        Remove-AzApiManagementProduct -Context $apimContext -ProductId "starter" -DeleteSubscriptions
    }
    
    Write-Host "Deleting initial 'Unlimited' product in APIM '$fhirAPIMName'"
    $product = Get-AzApiManagementProduct -Context $apimContext -ProductId "unlimited" -ErrorAction SilentlyContinue
    if ($product) {
        Remove-AzApiManagementProduct -Context $apimContext -ProductId "unlimited" -DeleteSubscriptions
    }

    Write-Host "Importing epi-read API in APIM '$fhirAPIMName'"
    Import-AzApiManagementApi -Context $apimContext -ApiId "epi-read-api" -ApiVersionSetId "epi-read-apiset" -ApiVersion "v1" -Path "epi" -SpecificationFormat OpenApi -SpecificationPath "$PSScriptRoot\Templates\APIM-ePI-read.yml"

    Write-Host "Importing epi-write API in APIM '$fhirAPIMName'"
    Import-AzApiManagementApi -Context $apimContext -ApiId "epi-write-api" -ApiVersionSetId "epi-write-apiset" -ApiVersion "v1" -Path "epi-w" -SpecificationFormat OpenApi -SpecificationPath "$PSScriptRoot\Templates\APIM-ePI-write.yml"
}

#endregion

#region DeploySPA

if ($DeploySPA) {
    $appParams = @{
        appName            = $fhirSPAName
        appServicePlanName = $fhirASPName
        appInsightsName    = $fhirAppInsightsName
        storageAccountName = $fhirStorageAccountName
        resourceTags       = $resourceTags
    }
    New-ArmDeployment -BaseName "FhirSPA" `
        -ResourceGroupName $fhirResourceGroupName `
        -TemplateFilePath "$PSScriptRoot\Templates\AppServiceWeb.json" `
        -TemplateParams $appParams
}

#endregion

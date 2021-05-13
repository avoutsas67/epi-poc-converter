#
# Connect to to subscription
#

Write-Host
Write-Host "Check if logged in"
$context = Get-AzContext -ListAvailable | Where-Object { $_.Tenant.Id -eq $tenantId }
if (!$context)
{
    Write-Host "Logging in..."
    Enable-AzContextAutosave
    Connect-AzAccount -TenantId $tenantId
}
else
{
    Write-Host "Already logged in"
}

Write-Host
Write-Host "Check if subscription '$subscriptionId' has been selected"
$currentContext = Get-AzContext
if ($currentContext.Subscription.Id -ne $subscriptionId)
{
    Write-Host "Selecting subscription '$subscriptionId'"
    Set-AzContext -SubscriptionId $subscriptionId
}
else
{
    Write-Host "Subscription '$subscriptionId' already selected"
}

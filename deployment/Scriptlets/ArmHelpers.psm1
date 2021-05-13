#
# Azure Resource Manager helper functions
#

<#
   .SYNOPSIS
    Deploys an ARM template

   .PARAMETER BaseName
   .PARAMETER ResourceGroupName
   .PARAMETER TemplateFilePath
   .PARAMETER TemplateParams
#>
function New-ArmDeployment
{
    param
    (
        $BaseName,
        $ResourceGroupName,
        $TemplateFilePath,
        $TemplateParams
    )

    Write-Host
    Write-Host "Deploying: $BaseName"

    $deploymentName = $BaseName + "-" + ((Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmm'))

    New-AzResourceGroupDeployment -Name $deploymentName `
                                  -ResourceGroupName $ResourceGroupName `
                                  -TemplateFile $TemplateFilePath `
                                  @TemplateParams `
                                  -Force -Verbose `
                                  -ErrorVariable ErrorMessages `
    | Out-Null

    if ($ErrorMessages)
    {
        Write-Host
        Write-Host -ForegroundColor Red "Template deployment returned the following errors:"
        Write-Host -ForegroundColor Red @(@($ErrorMessages) | ForEach-Object { $_.Exception.Message.TrimEnd("`r`n") })
    }
}

<#
   .SYNOPSIS
    Adds a role assignment if it doesn't exist

   .PARAMETER Scope
   .PARAMETER RoleName
   .PARAMETER PrincipalId
#>
function New-RoleAssignment {
    param
    (
        $Scope,
        $RoleName,
        $PrincipalId
    )
 
    Write-Host
    Write-Host "Checking role $RoleName on $Scope"

    $assignment = Get-AzRoleAssignment -ObjectId $PrincipalId -Scope $Scope -RoleDefinitionName $RoleName
    if (!$assignment) {
        Write-Host "Setting role $RoleName on $Scope"
        New-AzRoleAssignment -ObjectId $PrincipalId -Scope $Scope -RoleDefinitionName $RoleName | Out-Null
    }
}

Export-ModuleMember -Function New-ArmDeployment
Export-ModuleMember -Function New-RoleAssignment

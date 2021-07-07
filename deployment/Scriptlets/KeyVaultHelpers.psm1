#
# Azure KeyVault helper functions
#

<#
   .SYNOPSIS
    Deletes a KeyVault secret when it exists

   .PARAMETER VaultName
   .PARAMETER Name
#>
function Remove-KeyVaultSecret {
    param
    (
        $VaultName,
        $Name
    )

    $existingSecret = (Get-AzKeyVaultSecret -VaultName $VaultName -Name $Name).SecretValueText
    if ($existingSecret) {
        Write-Host
        Write-Host "Deleting $Name from vault $VaultName"

        Remove-AzKeyVaultSecret -VaultName $VaultName `
            -Name $Name `
            -Force
    }
}

<#
   .SYNOPSIS
    Adds a KeyVaultSecret when it doesn't exist

   .PARAMETER VaultName
   .PARAMETER Name
   .PARAMETER Secret
#>
function New-KeyVaultSecret {
    param
    (
        $VaultName,
        $Name,
        $Secret
    )
 
    Write-Host
    Write-Host "Check for existing '$Name'"

    $existingSecret = (Get-AzKeyVaultSecret -VaultName $VaultName -Name $Name).SecretValueText
    if (!$existingSecret) {
        Write-Host "Creating new '$Name'"

        # As we have enabled Soft-Delete on all KeyVaults (will be default and enforced in the future)
        # a deleted secret can't be overwritten but must be recovered first.
        # Because the recovery can take some time we have to wait so that we don't get a "Conflict" error on setting.
        $removed = (Get-AzKeyVaultSecret -VaultName $VaultName -Name $Name -InRemovedState)
        if ($removed) {
            Write-Host "  Need to recover '$Name' first" -NoNewline
            
            Undo-AzKeyVaultSecretRemoval -VaultName $VaultName -Name $Name | Out-Null
            
            do {
                Write-Host "." -NoNewline
                $existingSecret = (Get-AzKeyVaultSecret -VaultName $VaultName -Name $Name).SecretValueText
                Start-Sleep -Seconds 5
            } while (!$existingSecret)

            Write-Host
        }

        $secretValue = ConvertTo-SecureString $Secret -AsPlainText -Force
        Set-AzKeyVaultSecret -VaultName $VaultName `
            -Name $Name `
            -SecretValue $secretValue `
        | Out-Null
    }
    else {
        Write-Host "Using existing '$Name'"
    }
}

function Enable-PurgeProtection {
    param
    (
        $VaultName
    )
 
    Write-Host
    Write-Host "Check if purge protection is enabled for '$VaultName'"

    $resource = Get-AzResource -ResourceId (Get-AzKeyVault -VaultName $VaultName).ResourceId
    if (!$resource.Properties.enablePurgeProtection) {
        Write-Host "Enabling purge protection for '$VaultName'"

        $resource.Properties | Add-Member -MemberType "NoteProperty" -Name "enablePurgeProtection" -Value "true"
        Set-AzResource -ResourceId $resource.ResourceId -Properties $resource.Properties -Force | Out-Null
    }
    else {
        Write-Host "Purge protection already enabled for '$VaultName'"
    }    
}

Export-ModuleMember -Function Remove-KeyVaultSecret
Export-ModuleMember -Function New-KeyVaultSecret
Export-ModuleMember -Function Enable-PurgeProtection

az login

az rest --method delete --header "Accept=application/json" --uri 'https://management.azure.com/subscriptions/cbc0681b-7fea-4d32-ac52-6276bb0c2996/providers/Microsoft.ApiManagement/deletedservices/ema-dap-epi-dev-fhir-apim2?api-version=2020-06-01-preview'
az rest --method get --header "Accept=application/json" --uri 'https://management.azure.com/subscriptions/cbc0681b-7fea-4d32-ac52-6276bb0c2996/providers/Microsoft.ApiManagement/deletedservices?api-version=2021-01-01-preview'
az rest --method get --header "Accept=application/json" --uri 'https://management.azure.com/subscriptions/cbc0681b-7fea-4d32-ac52-6276bb0c2996/providers/Microsoft.ApiManagement/locations/westeurope/deletedservices/ma-dap-epi-dev-fhir-apim?api-version=2020-06-01-preview'
az rest --method put --header "Content-Type=application/json" --uri 'https://management.azure.com/subscriptions/cbc0681b-7fea-4d32-ac52-6276bb0c2996/resourceGroups/dev-dap-epi-proto-00002-rg/providers/Microsoft.ApiManagement/service/ema-dap-epi-dev-fhir-apim2?api-version=2020-06-01-preview' --body '{"properties": {"publisherEmail": "help@contoso.com","publisherName": "Contoso","restore": true},"sku": {"name": "Developer","capacity": 1},"location": "westeurope"}'

Import-Module Az.ApiManagement
Remove-AzApiManagement -ResourceGroupName dev-dap-epi-proto-00002-rg -Name ema-dap-epi-dev-fhir-apim

az account get-access-token --resource https://management.azure.com/

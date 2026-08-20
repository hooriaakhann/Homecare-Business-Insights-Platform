param projectPrefix string
param location string
param storageAccountName string
@secure()
param storageAccountKey string
param appInsightsConnectionString string
param keyVaultUri string

resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: 'plan-${projectPrefix}'
  location: location
  sku: { name: 'Y1', tier: 'Dynamic' }
  properties: {}
}

resource app 'Microsoft.Web/sites@2023-12-01' = {
  name: 'func-${projectPrefix}'
  location: location
  kind: 'functionapp,linux'
  identity: { type: 'SystemAssigned' }
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'Python|3.11'
      ftpsState: 'Disabled'
      appSettings: [
        { name: 'AzureWebJobsStorage', value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};AccountKey=${storageAccountKey};EndpointSuffix=core.windows.net' }
        { name: 'FUNCTIONS_WORKER_RUNTIME', value: 'python' }
        { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: appInsightsConnectionString }
        { name: 'KEY_VAULT_URI', value: keyVaultUri }
        { name: 'ADLS_ACCOUNT_NAME', value: storageAccountName }
      ]
    }
  }
}

output name string = app.name
output principalId string = app.identity.principalId

targetScope = 'resourceGroup'

@description('Short prefix used for resource names.')
param projectPrefix string = 'homecarebi'

@description('Azure region.')
param location string = resourceGroup().location

@secure()
param careApiToken string

@secure()
param careCompanyId string

@secure()
param sqlAdminPassword string

var suffix = uniqueString(resourceGroup().id)

module storage 'modules/storage.bicep' = {
  name: 'storage'
  params: {
    name: 'st${projectPrefix}${suffix}'
    location: location
  }
}

module monitoring 'modules/appinsights.bicep' = {
  name: 'monitoring'
  params: {
    projectPrefix: projectPrefix
    location: location
  }
}

module keyVault 'modules/keyvault.bicep' = {
  name: 'keyvault'
  params: {
    name: 'kv-${projectPrefix}-${suffix}'
    location: location
    apiToken: careApiToken
    companyId: careCompanyId
  }
}

module functionApp 'modules/functionapp.bicep' = {
  name: 'functionapp'
  params: {
    projectPrefix: projectPrefix
    location: location
    storageAccountName: storage.outputs.name
    storageAccountKey: storage.outputs.key
    appInsightsConnectionString: monitoring.outputs.connectionString
    keyVaultUri: keyVault.outputs.uri
  }
}

module synapse 'modules/synapse.bicep' = {
  name: 'synapse'
  params: {
    projectPrefix: projectPrefix
    location: location
    dataLakeAccountUrl: storage.outputs.dfsEndpoint
    dataLakeFileSystem: 'gold'
    sqlAdminPassword: sqlAdminPassword
  }
}

output storageAccountName string = storage.outputs.name
output functionAppName string = functionApp.outputs.name
output synapseWorkspaceName string = synapse.outputs.name

param name string
param location string
@secure()
param apiToken string
@secure()
param companyId string

resource vault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: name
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: { family: 'A', name: 'standard' }
    enableRbacAuthorization: true
    publicNetworkAccess: 'Enabled'
  }
}

resource token 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: vault
  name: 'care-api-token'
  properties: { value: apiToken }
}

resource company 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: vault
  name: 'care-company-id'
  properties: { value: companyId }
}

output uri string = vault.properties.vaultUri

param projectPrefix string
param location string
param dataLakeAccountUrl string
param dataLakeFileSystem string

@secure()
param sqlAdminPassword string

resource workspace 'Microsoft.Synapse/workspaces@2021-06-01' = {
  name: 'syn-${projectPrefix}'
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {
    defaultDataLakeStorage: {
      accountUrl: dataLakeAccountUrl
      filesystem: dataLakeFileSystem
    }
    managedResourceGroupName: 'mrg-${projectPrefix}'
    sqlAdministratorLogin: 'sqladminuser'
    sqlAdministratorLoginPassword: sqlAdminPassword
  }
}

output name string = workspace.name
output principalId string = workspace.identity.principalId

@description('Globally unique name for the web app (becomes <appName>.azurewebsites.net).')
param appName string

@description('Azure region for all resources. Defaults to the resource group location.')
param location string = resourceGroup().location

@description('App Service Plan SKU. B1 is the cheapest always-on tier; F1 is free but limited.')
@allowed([
  'F1'
  'B1'
  'B2'
  'S1'
])
param sku string = 'B1'

@description('Python version for the runtime stack.')
param pythonVersion string = '3.12'

var planName = '${appName}-plan'

resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: planName
  location: location
  sku: {
    name: sku
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

resource webApp 'Microsoft.Web/sites@2023-12-01' = {
  name: appName
  location: location
  kind: 'app,linux'
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|${pythonVersion}'
      appCommandLine: 'python -m uvicorn main:app --host 0.0.0.0 --port 8000'
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      healthCheckPath: '/healthz'
      appSettings: [
        {
          name: 'PYTHONPATH'
          value: '/home/site/wwwroot/.python_packages/lib/site-packages'
        }
        {
          name: 'WEBSITES_PORT'
          value: '8000'
        }
      ]
    }
  }
}

output webAppUrl string = 'https://${webApp.properties.defaultHostName}'
output webAppName string = webApp.name

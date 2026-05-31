# QR Code Generator — CI/CD with Bicep + GitHub Actions

A small but complete starter kit for learning the full deploy loop:

```
git push  ->  GitHub Actions  ->  Bicep provisions Azure  ->  app goes live
```

- **Backend:** Python + FastAPI. Returns QR codes as PNG images.
- **Frontend:** TypeScript (built with Vite). Calls the API and shows the QR code.
- **Infra:** Bicep template — a Linux App Service Plan + Python Web App.
- **Pipeline:** GitHub Actions — tests, builds, provisions infra, deploys, smoke-tests.

## Project layout

```
qr-code-generator/
├── app/                      # FastAPI backend
│   ├── main.py
│   ├── requirements.txt
│   └── test_main.py
├── frontend/                 # TypeScript frontend
│   ├── src/main.ts
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── infra/                    # Bicep infrastructure-as-code
│   ├── main.bicep
│   └── main.bicepparam
├── .github/workflows/
│   └── deploy.yml            # The CI/CD pipeline
└── .gitignore
```

## Run it locally

**Backend:**

```bash
cd app
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

**Frontend (in a second terminal):**

```bash
cd frontend
npm install
npm run dev      # opens a dev server with hot reload
```

For a local dev setup, point the frontend's fetch at `http://localhost:8000`,
or build the frontend (`npm run build`) and let FastAPI serve it — `main.py`
automatically serves `frontend/dist` at `/` once it exists.

**Run the tests:**

```bash
cd app
pip install pytest httpx
pytest
```

## Deploy to Azure

### One-time setup

1. **Create a resource group:**

   ```bash
   az group create --name qr-rg --location westeurope
   ```

2. **Create a service principal** so GitHub Actions can log in. This prints a
   JSON blob — copy the whole thing.

   ```bash
   az ad sp create-for-rbac \
     --name qr-github-actions \
     --role contributor \
     --scopes /subscriptions/<your-sub-id>/resourceGroups/qr-rg \
     --sdk-auth
   ```

3. **Add repo configuration** under *Settings → Secrets and variables → Actions*:

   | Type     | Name                   | Value                                            |
   |----------|------------------------|--------------------------------------------------|
   | Secret   | `AZURE_CREDENTIALS`    | the JSON blob from step 2                         |
   | Variable | `AZURE_RESOURCE_GROUP` | `qr-rg`                                           |
   | Variable | `AZURE_WEBAPP_NAME`    | a globally unique name, e.g. `qr-gen-yourname-42` |

### Deploy

Push to `main` (or hit "Run workflow" in the Actions tab):

```bash
git push origin main
```

The pipeline will test the backend, build the frontend, run the Bicep template
to provision the App Service, deploy the code, and finally curl the `/healthz`
endpoint to confirm it's live. Your app will be at:

```
https://<AZURE_WEBAPP_NAME>.azurewebsites.net
```

### Deploy the infra manually (optional)

You can also provision the infrastructure outside the pipeline to experiment:

```bash
az deployment group create \
  --resource-group qr-rg \
  --template-file infra/main.bicep \
  --parameters appName=qr-gen-yourname-42
```

## How the pieces connect

- **`infra/main.bicep`** declares the desired Azure state. Re-running it is
  safe and idempotent — Azure reconciles to match the template.
- **`appCommandLine`** in the Bicep tells App Service how to start the app
  (`uvicorn main:app`). `SCM_DO_BUILD_DURING_DEPLOYMENT=true` makes Azure install
  `requirements.txt` on deploy.
- **`healthCheckPath: /healthz`** lets Azure restart unhealthy instances, and the
  pipeline reuses the same endpoint for its smoke test.

## Things to try next

- Add a `box_size` / `border` control to the frontend (the API already supports them).
- Add an Azure Storage account to the Bicep template and save generated codes.
- Add a staging slot and deploy there first, then swap to production.

## Note

This kit was scaffolded and the Python backend was tested end-to-end (tests pass,
the API returns a valid PNG). The Bicep template is written against current
resource provider API versions but should be validated against your subscription
with `az bicep build --file infra/main.bicep` before your first real deploy.

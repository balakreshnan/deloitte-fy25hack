import datetime
import requests
from azure.identity import ClientSecretCredential, DefaultAzureCredential
import os
import msal

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# === CONFIGURATION ===
# tenant_id = "YOUR_TENANT_ID"
# client_id = "YOUR_CLIENT_ID"
# client_secret = "YOUR_CLIENT_SECRET"

subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
resource_group = os.getenv("AZURE_RESOURCE_GROUP")
factory_name = os.getenv("AZURE_DATA_FACTORY_NAME")

# Example pipeline run ID (get from trigger/run response or list runs API)
pipeline_run_id = "processELT"

def adf_get_pipeline_status(runid):

    returntxt = ""
    # === AUTHENTICATION ===
    # Get a token from Azure AD
    scope = "https://management.azure.com/.default"
    # credential = ClientSecretCredential(tenant_id, client_id, client_secret)
    credential = DefaultAzureCredential()
    token = credential.get_token(scope).token

    # === API CALL ===
    url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.DataFactory/factories/{factory_name}/pipelineruns/{pipeline_run_id}?api-version=2018-06-01"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        pipeline_status = response.json()
        print("Pipeline Run Status:", pipeline_status.get("status"))
        returntxt = pipeline_status.get("status")
        print("Details:", pipeline_status)
    else:
        print("Error:", response.status_code, response.text)
        returntxt = f"Error: {response.status_code}, {response.text}"

    return returntxt

def adf_pipeline_runs():
    returntxt = ""

    # https://learn.microsoft.com/en-us/rest/api/datafactory/pipeline-runs/get?view=rest-datafactory-2018-06-01&tabs=HTTP

    pipeline_name = "processELT"
    # === AUTHENTICATION ===
    # Get a token from Azure AD
    # Time window (last 24 hours here)
    end_time = datetime.datetime.utcnow()
    start_time = end_time - datetime.timedelta(hours=48)

    # === AUTHENTICATION ===
    scope = "https://management.azure.com/.default"
    # credential = ClientSecretCredential(tenant_id, client_id, client_secret)
    credential = DefaultAzureCredential()
    token = credential.get_token(scope).token

    # === API CALL: Query pipeline runs ===
    url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.DataFactory/factories/{factory_name}/queryPipelineRuns?api-version=2018-06-01"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "lastUpdatedAfter": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "lastUpdatedBefore": end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "filters": [
            {"operand": "PipelineName", "operator": "Equals", "values": [pipeline_name]}
        ]
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        runs = response.json().get("value", [])
        if runs:
            latest_run = runs[0]   # usually the most recent first
            print("Pipeline Name:", latest_run["pipelineName"])
            print("Run ID:", latest_run["runId"])
            print("Status:", latest_run["status"])
            returntxt = print("Status:", latest_run["status"])
        else:
            print("No runs found for pipeline:", pipeline_name)
            returntxt = "No runs found for pipeline."
    else:
        print("Error:", response.status_code, response.text)

    return returntxt

def adx_query():
    returntxt = ""
    end_time = datetime.datetime.utcnow()
    start_time = end_time - datetime.timedelta(hours=48)

    # ADX details
    cluster = os.getenv("ADX_CLUSTER")  # e.g., "https://<your-cluster>.<region>.kusto.windows.net"
    database = os.getenv("ADX_DATABASE")  # e.g., "your-database"
    tenant_id = os.getenv("TENANT_ID")
    client_id = os.getenv("CLIENT_ID")

    # === AUTHENTICATION ===
    # scope = "https://management.azure.com/.default"
    # scope = ["https://kusto.kusto.windows.net/.default"]
    # # credential = ClientSecretCredential(tenant_id, client_id, client_secret)
    # credential = DefaultAzureCredential()
    # token = credential.get_token(scope).token

    # Get token
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    scope = ["https://kusto.kusto.windows.net/.default"]

    app = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential=DefaultAzureCredential())
    token_response = app.acquire_token_for_client(scopes=scope)
    print(token_response)
    #access_token = token_response["access_token"]
    # Define query
    query = "StormEvents | take 10"

    # REST endpoint
    url = f"{cluster}/v2/rest/query"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "db": database,
        "csl": query
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    results = response.json()
    returntxt = results
    print("ADX Query Results:", results)

    return returntxt

if __name__ == "__main__":
    pilelineruns = adf_pipeline_runs()
    # pilelineruns = adx_query()
    print('output:' , pilelineruns)
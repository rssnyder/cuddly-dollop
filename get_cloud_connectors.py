from os import getenv

from requests import post, get, Session
from requests.adapters import HTTPAdapter, Retry

s = Session()

retries = Retry(total=50, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])

s.mount("http://", HTTPAdapter(max_retries=retries))

PARAMS = {
    "accountIdentifier": getenv("HARNESS_ACCOUNT_ID"),
}

HEADERS = {
    "x-api-key": getenv("HARNESS_PLATFORM_API_KEY"),
}


def get_connectors(kind: str, page: int = 0):

    return s.post(
        "https://app.harness.io/ng/api/connectors/listV2",
        params={
            "accountIdentifier": getenv("HARNESS_ACCOUNT_ID"),
            "pageIndex": page,
        },
        headers=HEADERS,
        json={
            "filterType": "Connector",
            "types": [
                kind,
            ]
        }
    )


def get_connector_status(identifier: str):

    return s.post(
        f"https://app.harness.io/ng/api/connectors/testConnection/{identifier}",
        params={
            "accountIdentifier": getenv("HARNESS_ACCOUNT_ID"),
        },
        headers=HEADERS
    )


if __name__ == "__main__":

    resp_data = get_connectors("CEAws").json()

    while resp_data.get("data", {}).get("pageIndex") <= resp_data.get("data", {}).get("totalPages"):
        
        for connector in resp_data.get("data", {}).get("content", []):
            connector_data = connector.get("connector")

            resp = get_connector_status(connector_data.get("identifier"))
            status = resp.json().get("status")
            if status != "SUCCESS":
                status += ": " + resp.json().get("message")

            print(f"aws,{connector_data.get('spec', {}).get('awsAccountId')},{status}")
        
        resp_data = get_connectors("CEAws", resp_data.get("data", {}).get("pageIndex") + 1).json()
    
    resp_data = get_connectors("CEAzure").json()

    while resp_data.get("data", {}).get("pageIndex") <= resp_data.get("data", {}).get("totalPages"):
        
        for connector in resp_data.get("data", {}).get("content", []):
            connector_data = connector.get("connector")

            resp = get_connector_status(connector_data.get("identifier"))
            status = resp.json().get("status")
            if status != "SUCCESS":
                status += ": " + resp.json().get("message")

            print(f"azure,{connector_data.get('spec', {}).get('subscriptionId')},{status}")
        
        resp_data = get_connectors("CEAzure", resp_data.get("data", {}).get("pageIndex") + 1).json()

    resp_data = get_connectors("GcpCloudCost").json()

    while resp_data.get("data", {}).get("pageIndex") <= resp_data.get("data", {}).get("totalPages"):
        
        for connector in resp_data.get("data", {}).get("content", []):
            connector_data = connector.get("connector")

            resp = get_connector_status(connector_data.get("identifier"))
            status = resp.json().get("status")
            if status != "SUCCESS":
                status += ": " + resp.json().get("message")

            print(f"gcp,{connector_data.get('spec', {}).get('projectId')},{status}")
        
        resp_data = get_connectors("GcpCloudCost", resp_data.get("data", {}).get("pageIndex") + 1).json()

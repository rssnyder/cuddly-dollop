from os import getenv
from csv import writer
from datetime import datetime, timedelta

from requests import post, get, Session
from requests.adapters import HTTPAdapter, Retry

from common import (
    get_aws_account_cost,
    get_azure_subscription_cost,
    get_gcp_project_cost,
)

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
            ],
        },
    )


def get_connector_status(identifier: str):
    return s.post(
        f"https://app.harness.io/ng/api/connectors/testConnection/{identifier}",
        params={
            "accountIdentifier": getenv("HARNESS_ACCOUNT_ID"),
        },
        headers=HEADERS,
    )


if __name__ == "__main__":
    with open(
        f"connectors_{datetime.now()}.csv".replace(" ", "_"), "w", newline=""
    ) as csvfile:
        csvwriter = writer(csvfile, delimiter=",")

        resp_data = get_connectors("CEAws").json()

        while resp_data.get("data", {}).get("pageIndex") <= resp_data.get(
            "data", {}
        ).get("totalPages"):
            for connector in resp_data.get("data", {}).get("content", []):
                connector_data = connector.get("connector")

                resp = get_connector_status(connector_data.get("identifier"))
                status = resp.json().get("status")
                if status != "SUCCESS":
                    status += ": " + resp.json().get("message")

                # print(f"aws,{connector_data.get('spec', {}).get('awsAccountId')},{status}")
                account_id = connector_data.get("spec", {}).get("awsAccountId")
                csvwriter.writerow(
                    ["aws", account_id, status, get_aws_account_cost(account_id)]
                )

            resp_data = get_connectors(
                "CEAws", resp_data.get("data", {}).get("pageIndex") + 1
            ).json()

        resp_data = get_connectors("CEAzure").json()

        while resp_data.get("data", {}).get("pageIndex") <= resp_data.get(
            "data", {}
        ).get("totalPages"):
            for connector in resp_data.get("data", {}).get("content", []):
                connector_data = connector.get("connector")

                resp = get_connector_status(connector_data.get("identifier"))
                status = resp.json().get("status")
                if status != "SUCCESS":
                    status += ": " + resp.json().get("message")

                # print(
                #     f"azure,{connector_data.get('spec', {}).get('subscriptionId')},{status}"
                # )
                subscrition_id = connector_data.get("spec", {}).get("subscriptionId")
                csvwriter.writerow(
                    [
                        "azure",
                        subscrition_id,
                        status,
                        get_azure_subscription_cost(subscrition_id),
                    ]
                )

            resp_data = get_connectors(
                "CEAzure", resp_data.get("data", {}).get("pageIndex") + 1
            ).json()

        resp_data = get_connectors("GcpCloudCost").json()

        while resp_data.get("data", {}).get("pageIndex") <= resp_data.get(
            "data", {}
        ).get("totalPages"):
            for connector in resp_data.get("data", {}).get("content", []):
                connector_data = connector.get("connector")

                resp = get_connector_status(connector_data.get("identifier"))
                status = resp.json().get("status")
                if status != "SUCCESS":
                    status += ": " + resp.json().get("message")

                # print(f"gcp,{connector_data.get('spec', {}).get('projectId')},{status}")
                project_id = connector_data.get("spec", {}).get("projectId")
                csvwriter.writerow(
                    ["gcp", project_id, status, get_gcp_project_cost(project_id)]
                )

            resp_data = get_connectors(
                "GcpCloudCost", resp_data.get("data", {}).get("pageIndex") + 1
            ).json()

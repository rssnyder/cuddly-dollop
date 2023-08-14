from os import getenv
from sys import argv

from requests import post, get, Session
from requests.adapters import HTTPAdapter, Retry

s = Session()

retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])

s.mount("http://", HTTPAdapter(max_retries=retries))

PARAMS = {
    "accountIdentifier": getenv("HARNESS_ACCOUNT_ID"),
    # "routingId": getenv("HARNESS_ACCOUNT_ID"),
}

HEADERS = {
    "x-api-key": getenv("HARNESS_PLATFORM_API_KEY"),
}


def test_resp(resp):
    if resp.json().get("status") != "SUCCESS":
        print(resp.text)


def get_delegates():
    return s.get(
        "https://app.harness.io/gateway/ng/api/delegate-token-ng/delegate-groups",
        params=PARAMS,
        headers=HEADERS,
    )


def get_connector(identifier: str):
    return s.get(
        f"https://app.harness.io/ng/api/connectors/{identifier}",
        params=PARAMS,
        headers=HEADERS,
    )


def create_k8s_connector(identifier: str, delegate_name: str):
    return s.post(
        "https://app.harness.io/gateway/ng/api/connectors",
        params=PARAMS,
        headers=HEADERS,
        json={
            "connector": {
                "name": delegate_name,
                "identifier": identifier,
                "description": "created via automation",
                "tags": {},
                "type": "K8sCluster",
                "spec": {
                    # "connectorType": "KubernetesClusterConfig",
                    "credential": {"type": "InheritFromDelegate", "spec": None},
                    "delegateSelectors": [delegate_name],
                },
            }
        },
    )


def create_k8s_ccm_connector(identifier: str, k8s_connector: str):
    return s.post(
        "https://app.harness.io/gateway/ng/api/connectors",
        params=PARAMS,
        headers=HEADERS,
        json={
            "connector": {
                "name": identifier,
                "identifier": identifier,
                "description": "created via automation",
                "type": "CEK8sCluster",
                "spec": {
                    "connectorType": "CEKubernetesClusterConfigDTO",
                    "featuresEnabled": ["VISIBILITY"],
                    "connectorRef": k8s_connector,
                },
            }
        },
    )


if __name__ == "__main__":
    resp = get_delegates()

    for group in resp.json().get("resource", {}).get("delegateGroupDetails", []):
        identifier = group.get("delegateGroupIdentifier")
        name = group.get("groupName")

        if len(argv) > 1:
            print(name)
            continue

        resp = get_connector(identifier)

        if resp.status_code == 200:
            print("k8s connector exists for", identifier)
        else:
            print("need to create k8s connector for", identifier)
            resp = create_k8s_connector(identifier, name)
            test_resp(resp)

        resp = get_connector(identifier + "_ccm")

        if resp.status_code == 200:
            print("k8s ccm connector exists for", identifier)
        else:
            print("need to create k8s ccm connector for", identifier)
            resp = create_k8s_ccm_connector(identifier + "_ccm", identifier)
            test_resp(resp)

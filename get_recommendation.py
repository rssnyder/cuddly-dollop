from os import getenv
from datetime import datetime
import json
import csv

from requests import post


def get_recommendations(resource_type: str, offset: int = 0, limit: int = 100):
    resp = post(
        "https://app.harness.io/ccm/api/recommendation/overview/list",
        params={
            "accountIdentifier": getenv("HARNESS_ACCOUNT_ID"),
        },
        headers={
            "Content-Type": "application/json",
            "x-api-key": getenv("HARNESS_PLATFORM_API_KEY"),
        },
        json={
            "filterType": "CCMRecommendation",
            "k8sRecommendationFilterPropertiesDTO": {
                "resourceTypes": [resource_type],
                "recommendationStates": ["OPEN"],
            },
            "offset": offset,
            "limit": limit,
        },
    )

    total = []
    if resp.status_code == 200:
        data = resp.json().get("data", {})  # .get("data", {}).get("items", [])
        total = data.get("items", [])
        if len(data.get("items")) == limit:
            total += get_recommendations(resource_type, offset + limit, limit)
    else:
        print(resp.text)
        total = []

    return [x for x in total if x.get("monthlySaving")]


def get_ec2_instance(current_date):
    with open(
        f"recommendations_ec2_instance_{current_date.strftime('%Y-%m-%d_%H:%M:%S')}.csv".replace(
            " ", "_"
        ).replace(
            ":", "_"
        ),
        "w",
    ) as file:
        print("getting EC2_INSTANCE")

        header = "awsAccountId,id,toTerminate,current_instanceFamily,current_memory,current_vcpu,current_cpuUtilisation,current_memoryUtilisation,current_monthlyCost,current_monthlySavings,same_instanceFamily,same_memory,same_vcpu,same_cpuUtilisation,same_memoryUtilisation,same_monthlyCost,same_monthlySavings,cross_instanceFamily,cross_memory,cross_vcpu,cross_cpuUtilisation,cross_memoryUtilisation,cross_monthlyCost,cross_monthlySavings"
        file.write(header + "\n")

        for recc in get_recommendations("EC2_INSTANCE"):
            details = recc.get("recommendationDetails", {})
            current = details.get("current", {})
            same = details.get("sameFamilyRecommendation", {})
            if not same:
                same = {}
            cross = details.get("crossFamilyRecommendation", {})
            if not cross:
                cross = {}

            content = [
                details.get("awsAccountId", ""),
                details.get("id", ""),
                str(details.get("showTerminated", False)),
                current.get("instanceFamily", ""),
                current.get("memory", ""),
                current.get("vcpu", ""),
                current.get("cpuUtilisation", ""),
                current.get("memoryUtilisation", ""),
                current.get("monthlyCost", ""),
                current.get("monthlySavings", ""),
                same.get("instanceFamily", ""),
                same.get("memory", ""),
                same.get("vcpu", ""),
                same.get("cpuUtilisation", ""),
                same.get("memoryUtilisation", ""),
                same.get("monthlyCost", ""),
                same.get("monthlySavings", ""),
                cross.get("instanceFamily", ""),
                cross.get("memory", ""),
                cross.get("vcpu", ""),
                cross.get("cpuUtilisation", ""),
                cross.get("memoryUtilisation", ""),
                cross.get("monthlyCost", ""),
                cross.get("monthlySavings", ""),
            ]
            content_clean = [str(x) for x in content]
            line = ",".join(content_clean)
            file.write(line + "\n")


def get_azure_instance(current_date):
    with open(
        f"recommendations_azure_instance_{current_date.strftime('%Y-%m-%d_%H:%M:%S')}.csv".replace(
            " ", "_"
        ).replace(
            ":", "_"
        ),
        "w",
    ) as file:
        print("getting AZURE_INSTANCE")

        header = "tenantId,subscriptionId,resourceGroupId,vmId,vmName,toTerminate,current_vmSize,current_region,current_memory,current_cores,current_monthlyCost,current_avgCpuUtilization,current_maxCpuUtilization,current_avgMemoryUtilization,current_maxMemoryUtilization,target_vmSize,target_region,target_memory,target_cores,target_monthlyCost,target_avgCpuUtilization,target_maxCpuUtilization,target_avgMemoryUtilization,target_maxMemoryUtilization"
        file.write(header + "\n")

        for recc in get_recommendations("AZURE_INSTANCE"):
            details = recc.get("recommendationDetails", {})
            current = details.get("current", {})
            target = details.get("target", {})
            if not target:
                target = {}

            content = [
                details.get("tenantId"),
                details.get("subscriptionId"),
                details.get("resourceGroupId"),
                details.get("vmId"),
                details.get("vmName"),
                details.get("showTerminated", False),
                current.get("vmSize"),
                current.get("region"),
                current.get("memory"),
                current.get("cores"),
                current.get("monthlyCost"),
                current.get("avgCpuUtilization"),
                current.get("maxCpuUtilization"),
                current.get("avgMemoryUtilization"),
                current.get("maxMemoryUtilization"),
                target.get("vmSize"),
                target.get("region"),
                target.get("memory"),
                target.get("cores"),
                target.get("monthlyCost"),
                target.get("avgCpuUtilization"),
                target.get("maxCpuUtilization"),
                target.get("avgMemoryUtilization"),
                target.get("maxMemoryUtilization"),
            ]
            content_clean = [str(x) for x in content]
            line = ",".join(content_clean)
            file.write(line + "\n")


def get_azure_instance(current_date):
    with open(
        f"recommendations_azure_instance_{current_date.strftime('%Y-%m-%d_%H:%M:%S')}.csv".replace(
            " ", "_"
        ).replace(
            ":", "_"
        ),
        "w",
    ) as file:
        print("getting AZURE_INSTANCE")

        header = "tenantId,subscriptionId,resourceGroupId,vmId,vmName,toTerminate,current_vmSize,current_region,current_memory,current_cores,current_monthlyCost,current_avgCpuUtilization,current_maxCpuUtilization,current_avgMemoryUtilization,current_maxMemoryUtilization,target_vmSize,target_region,target_memory,target_cores,target_monthlyCost,target_avgCpuUtilization,target_maxCpuUtilization,target_avgMemoryUtilization,target_maxMemoryUtilization"
        file.write(header + "\n")

        for recc in get_recommendations("AZURE_INSTANCE"):
            details = recc.get("recommendationDetails", {})
            current = details.get("current", {})
            target = details.get("target", {})
            if not target:
                target = {}

            content = [
                details.get("tenantId"),
                details.get("subscriptionId"),
                details.get("resourceGroupId"),
                details.get("vmId"),
                details.get("vmName"),
                details.get("showTerminated", False),
                current.get("vmSize"),
                current.get("region"),
                current.get("memory"),
                current.get("cores"),
                current.get("monthlyCost"),
                current.get("avgCpuUtilization"),
                current.get("maxCpuUtilization"),
                current.get("avgMemoryUtilization"),
                current.get("maxMemoryUtilization"),
                target.get("vmSize"),
                target.get("region"),
                target.get("memory"),
                target.get("cores"),
                target.get("monthlyCost"),
                target.get("avgCpuUtilization"),
                target.get("maxCpuUtilization"),
                target.get("avgMemoryUtilization"),
                target.get("maxMemoryUtilization"),
            ]
            content_clean = [str(x) for x in content]
            line = ",".join(content_clean)
            file.write(line + "\n")


def get_node_pool(current_date):
    with open(
        f"recommendations_node_pool_{current_date.strftime('%Y-%m-%d_%H:%M:%S')}.csv".replace(
            " ", "_"
        ).replace(
            ":", "_"
        ),
        "w",
    ) as file:
        print("getting NODE_POOL")

        # header = "tenantId,subscriptionId,resourceGroupId,vmId,vmName,toTerminate,current_vmSize,current_region,current_memory,current_cores,current_monthlyCost,current_avgCpuUtilization,current_maxCpuUtilization,current_avgMemoryUtilization,current_maxMemoryUtilization,target_vmSize,target_region,target_memory,target_cores,target_monthlyCost,target_avgCpuUtilization,target_maxCpuUtilization,target_avgMemoryUtilization,target_maxMemoryUtilization"
        # file.write(header + "\n")

        for recc in get_recommendations("NODE_POOL"):
            details = recc.get("recommendationDetails", {})
            current = details.get("current", {})
            target = details.get("target", {})
            if not target:
                target = {}
            print(json.dumps(recc))

            # content = [details.get("tenantId"), details.get("subscriptionId"), details.get("resourceGroupId"), details.get("vmId"), details.get("vmName"), details.get("showTerminated", False), current.get("vmSize"), current.get("region"), current.get("memory"), current.get("cores"), current.get("monthlyCost"), current.get("avgCpuUtilization"), current.get("maxCpuUtilization"), current.get("avgMemoryUtilization"), current.get("maxMemoryUtilization"), target.get("vmSize"), target.get("region"), target.get("memory"), target.get("cores"), target.get("monthlyCost"), target.get("avgCpuUtilization"), target.get("maxCpuUtilization"), target.get("avgMemoryUtilization"), target.get("maxMemoryUtilization")]
            # content_clean = [str(x) for x in content]
            # line = ",".join(content_clean)
            # file.write(line + "\n")


if __name__ == "__main__":
    current_date = datetime.now()

    get_ec2_instance(current_date)

    get_azure_instance(current_date)

    # get_node_pool(current_date)

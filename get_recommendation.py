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

        header = "clusterName,resourceName,monthlyCost,monthlySaving,total_minNodes,total_minMem,total_minCpu,current_sumNodes,current_type,current_memPerVm,current_cpusPerVm,current_onDemandPrice,current_avgPrice,target_sumNodes,target_type,target_memPerVm,target_cpusPerVm,target_onDemandPrice,target_avgPrice"
        file.write(header + "\n")

        for recc in get_recommendations("NODE_POOL"):
            details = recc.get("recommendationDetails", {})
            current = details.get("current", {})
            current_pool = current.get("nodePools", []).pop()
            target = details.get("recommended", {})
            target_pool = [
                x
                for x in details.get("recommended", {}).get("nodePools", [])
                if x.get("role") == "worker"
            ].pop()
            if not target:
                target = {}

            content = [
                recc.get("clusterName"),
                recc.get("resourceName"),
                recc.get("monthlyCost"),
                recc.get("monthlySaving"),
                details.get("resourceRequirement", {}).get("minNodes"),
                details.get("resourceRequirement", {}).get("sumMem"),
                details.get("resourceRequirement", {}).get("sumCpu"),
                current_pool.get("sumNodes"),
                current_pool.get("vm", {}).get("type"),
                current_pool.get("vm", {}).get("memPerVm"),
                current_pool.get("vm", {}).get("cpusPerVm"),
                current_pool.get("vm", {}).get("onDemandPrice"),
                current_pool.get("vm", {}).get("avgPrice"),
                target_pool.get("sumNodes"),
                target_pool.get("vm", {}).get("type"),
                target_pool.get("vm", {}).get("memPerVm"),
                target_pool.get("vm", {}).get("cpusPerVm"),
                target_pool.get("vm", {}).get("onDemandPrice"),
                target_pool.get("vm", {}).get("avgPrice"),
            ]
            content_clean = [str(x) for x in content]
            line = ",".join(content_clean)
            file.write(line + "\n")


def get_workload(current_date):
    with open(
        f"recommendations_workload_{current_date.strftime('%Y-%m-%d_%H:%M:%S')}.csv".replace(
            " ", "_"
        ).replace(
            ":", "_"
        ),
        "w",
    ) as file:
        print("getting WORKLOAD")

        header = "clusterName,namespace,resourceName,containerName,total_Mem,total_Cpu,current_requestMem,current_requestCpu,current_limitMem,current_limitCpu,target_requestMem,target_requestCpu,target_limitMem"
        file.write(header + "\n")

        for recc in get_recommendations("WORKLOAD"):
            details = recc.get("recommendationDetails", {})
            containers = details.get("containerRecommendations", {})
            for container in containers:
                container_info = containers.get(container, {})

                try:
                    content = [
                        recc.get("clusterName"),
                        recc.get("namespace"),
                        recc.get("resourceName"),
                        container,
                        container_info.get("lastDayCost", {}).get("memory"),
                        container_info.get("lastDayCost", {}).get("cpu"),
                        container_info.get("current", {})
                        .get("requests", {})
                        .get("memory"),
                        container_info.get("current", {})
                        .get("requests", {})
                        .get("cpu"),
                        container_info.get("current", {})
                        .get("limits", {})
                        .get("memory"),
                        container_info.get("current", {}).get("limits", {}).get("cpu"),
                        container_info.get("recommended", {})
                        .get("requests", {})
                        .get("memory"),
                        container_info.get("recommended", {})
                        .get("requests", {})
                        .get("cpu"),
                        container_info.get("recommended", {})
                        .get("limits", {})
                        .get("memory"),
                    ]
                except:
                    continue
                content_clean = [str(x) for x in content]
                line = ",".join(content_clean)
                file.write(line + "\n")


if __name__ == "__main__":
    current_date = datetime.now()

    get_ec2_instance(current_date)

    get_azure_instance(current_date)

    get_node_pool(current_date)

    get_workload(current_date)

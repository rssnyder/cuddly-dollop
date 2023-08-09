from os import getenv
from csv import writer
from datetime import datetime
from time import time
from calendar import monthrange
from sys import argv

from requests import get, post


PARAMS = {
    "accountIdentifier": getenv("HARNESS_ACCOUNT_ID"),
}

HEADERS = {
    "x-api-key": getenv("HARNESS_PLATFORM_API_KEY"),
}


def get_evaluations(start: int, end: int, limit: int = 100, offset: int = 0):
    resp = post(
        "https://app.harness.io/gateway/ccm/api/governance/execution/list",
        headers=HEADERS,
        params=PARAMS,
        json={
            "policyExecutionFilter": {
                "accountId": getenv("HARNESS_ACCOUNT_ID"),
                "limit": limit,
                "offset": offset,
                "time": [
                    {"operator": "AFTER", "timestamp": start},
                    {"operator": "BEFORE", "timestamp": end},
                ],
                "sortOrder": "DESCENDING",
                "ruleExecutionSortType": "LAST_UPDATED_AT",
            }
        },
    )

    data = resp.json()
    executions = []

    if data.get("status") == "SUCCESS":
        executions.extend(data.get("data", {}).get("ruleExecution", []))

        if data.get("data", {}).get("totalItems") > offset + limit:
            executions.extend(get_evaluations(start, end, limit, offset + limit))

    return executions


def get_evaluation_details(identifier: str):
    resp = get(
        f"https://app.harness.io/gateway/ccm/api/governance/status/{identifier}",
        headers=HEADERS,
        params=PARAMS,
    )

    return resp.json()


def get_date_range(current_date: datetime, back_month: int = 0):
    if back_month:
        origional_month = current_date.month
        current_date = current_date.replace(month=current_date.month - back_month)
        if origional_month <= back_month:
            current_date = current_date.replace(year=current_date.year - 1, month=12)

    start_of_month = datetime(current_date.year, current_date.month, 1)
    end_of_month = datetime(
        current_date.year,
        current_date.month,
        monthrange(current_date.year, current_date.month)[1],
        23,
        59,
        59,
    )

    return int(start_of_month.timestamp()) * 1000, int(end_of_month.timestamp()) * 1000


if __name__ == "__main__":
    if len(argv) == 1:
        back_month = 0
    else:
        back_month = int(argv[1])

    current_date = datetime.now()

    with open(
        f"evaluations_{current_date.strftime('%Y-%m-%d_%H:%M:%S')}.csv", "w", newline=""
    ) as csvfile:
        csvwriter = writer(csvfile, delimiter=",")

        csvwriter.writerow(
            [
                "timestamp",
                "ruleEnforcementName",
                "ruleName",
                "targetAccount",
                "targetRegions",
                "isDryRun",
                "resource",
            ]
        )

        date_range = get_date_range(current_date, back_month)

        for evaluation in get_evaluations(
            date_range[0], date_range[1], limit=20, offset=0
        ):
            if evaluation.get("resourceCount"):
                details = get_evaluation_details(evaluation.get("uuid"))
                for resource in details:
                    csvwriter.writerow(
                        [
                            datetime.fromtimestamp(
                                int(evaluation.get("createdAt") / 1000)
                            ).strftime("%Y-%m-%d %H:%M:%S"),
                            evaluation.get("ruleEnforcementName"),
                            evaluation.get("ruleName"),
                            evaluation.get("targetAccount"),
                            evaluation.get("targetRegions"),
                            evaluation.get("isDryRun"),
                            resource,
                        ]
                    )

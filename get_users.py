from os import getenv
from csv import writer
from datetime import datetime

from requests import post


def get_users(page: int = 0, page_size: int = 50):
    resp = post(
        "https://app.harness.io/ng/api/user/aggregate",
        params={
            "accountIdentifier": getenv("HARNESS_ACCOUNT_ID"),
            "pageSize": page_size,
            "pageIndex": page,
        },
        headers={
            "Content-Type": "application/json",
            "x-api-key": getenv("HARNESS_PLATFORM_API_KEY"),
        },
    )

    users = []
    if resp.status_code == 200:
        data = resp.json().get("data")
        users += data.get("content", [])
        if data.get("pageIndex") < data.get("totalPages"):
            users += get_users(data.get("pageIndex") + 1)
    else:
        print(resp.text)
        users += []

    return users


if __name__ == "__main__":
    current_date = datetime.now()

    with open(
        f"users_{current_date.strftime('%Y-%m-%d_%H:%M:%S')}.csv".replace(
            " ", "_"
        ).replace(":", "_"),
        "w",
    ) as file:
        header = "name,email,roles"
        file.write(header + "\n")

        for user in get_users():
            data = [
                user.get("user", {}).get("email"),
                user.get("user", {}).get("email"),
            ]
            for role in user.get("roleAssignmentMetadata"):
                data.append(f"{role.get('roleName')}:{role.get('resourceGroupName')}")

            line = ",".join(data)
            file.write(line + "\n")

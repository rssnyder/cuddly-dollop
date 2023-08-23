from csv import reader
from sys import argv
from datetime import datetime

from common import (
    CloudAccount,
    get_aws_account_cost,
    get_azure_subscription_cost,
    get_gcp_project_cost,
)


if __name__ == "__main__":
    current_date = datetime.now()

    # program arguments
    if len(argv) < 3:
        print(
            f"usage: {argv[0]} [cross account role name] [tenant id] [service account email] [csv #1] [csv #2] [csv #3]"
        )
        exit(1)

    cross_account_role = argv[1]
    tenant_id = argv[2]
    service_account_email = argv[3]
    files = argv[4:]

    # loop through file and pull in account information
    for file_csv in files:
        with open(file_csv, "r") as cc_data:
            datareader = reader(cc_data)
            next(datareader)

            with open(
                f"cloud_connectors{current_date.strftime('%Y-%m-%d_%H:%M:%S')}.txt", "w"
            ) as file:
                for row in datareader:
                    # create instance of account with given data
                    account = CloudAccount(
                        row[0],
                        row[1],
                        row[2],
                        row[3],
                        row[4],
                        row[5],
                        row[6],
                        row[7],
                    )

                    # print(account.identifier)
                    if account.payer_id == account.identifier:
                        print("CONNECTOR:skipped\t\tpayer account")

                    if account.cloud == "aws":
                        if account.payer_id == "423844416462":
                            print("CONNECTOR:skipped\t\tlegacy account")
                            continue

                        if not get_aws_account_cost(account.identifier):
                            print(
                                f"CONNECTOR:skipped\t\tno account cost last 90d {account.identifier}"
                            )

                    elif account.cloud == "azure":
                        if not get_azure_subscription_cost(account.identifier):
                            print(
                                f"CONNECTOR:skipped\t\tno account cost last 90d {account.identifier}"
                            )
                            continue

                    elif account.cloud == "gcp":
                        if not get_gcp_project_cost(account.identifier):
                            print(
                                f"CONNECTOR:skipped\t\tno account cost last 90d {account.identifier}"
                            )
                            continue

                    result = account.create_connector(
                        cross_account_role,
                        tenant_id,
                        service_account_email,
                        dry_run=False,
                    )

                    file.write(result + "\n")
                    print(result)
                    # print(account.delete_connector())

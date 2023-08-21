from csv import reader
from sys import argv

from common import (
    CloudAccount,
    get_aws_account_cost,
    get_azure_subscription_cost,
    get_gcp_project_cost,
)


if __name__ == "__main__":
    # program arguments
    if len(argv) < 3:
        print(
            f"usage: {argv[0]} [aws master account id #1] [cross account role name #1] [aws master account id #2] [cross account role name #2] [tenant id] [service account email] [csv #1] [csv #2] [csv #3]"
        )
        exit(1)

    aws_first = argv[1], argv[2]
    aws_second = argv[3], argv[4]
    tenant_id = argv[5]
    service_account_email = argv[6]
    files = argv[7:]

    # loop through file and pull in account information
    for file_csv in files:
        with open(file_csv, "r") as cc_data:
            datareader = reader(cc_data)
            next(datareader)

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
                if account.cloud == "aws":
                    if account.payer_id == aws_first[0]:
                        role_name = aws_first[1]
                    elif account.payer_id == aws_second[0]:
                        role_name = aws_second[1]
                    elif account.payer_id == "423844416462":
                        print("CONNECTOR:skipped\t\tlegacy account")
                        continue
                    else:
                        print(
                            f"CONNECTOR:skipped\t\tpayer id {account.payer_id} for account {account.name} not given"
                        )
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

                print(
                    account.create_connector(
                        role_name, tenant_id, service_account_email, dry_run=False
                    )
                )
                # print(account.delete_connector())

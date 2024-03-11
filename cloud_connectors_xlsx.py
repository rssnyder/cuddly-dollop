from csv import reader
from sys import argv
from datetime import datetime

import pandas as pd

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
            f"usage: {argv[0]} [dry run] [cross account role name] [tenant id] [service account email] [xlsx #1] [xlsx #2] [xlsx #3]"
        )
        exit(1)

    dry_run = argv[1]
    if dry_run.lower() == "dryrun":
        dry_run = True
        print(
            "DRYRUN:true\t\twe are running in dry run mode, nothing will be changed in harness"
        )
    else:
        dry_run = False
        print(
            "DRYRUN:false\t\twe are NOT running in dry run mode, changes will be made in harness"
        )
    cross_account_role = argv[2]
    tenant_id = argv[3]
    service_account_email = argv[4]
    files = argv[5:]

    with open(
        f"cloud_connectors{current_date.strftime('%Y-%m-%d_%H:%M:%S')}.txt".replace(
            " ", "_"
        ).replace(":", "_"),
        "w",
    ) as file:
        # loop through file and pull in account information
        for file_csv in files:
            sheet = pd.read_excel(file_csv)

            for _, row in sheet.iterrows():
                # create instance of account with given data
                account = CloudAccount(
                    row.Vendor,
                    row["Payer account_identifier"],
                    row["Payer account_name"],
                    row.vendor_account_identifier,
                    row.vendor_account_name,
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
                        continue

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
                    dry_run=dry_run,
                )

                file.write(result + "\n")
                print(result)

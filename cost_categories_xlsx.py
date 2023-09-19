from csv import reader
from os import getenv
from sys import argv
from time import sleep

import pandas as pd
import numpy as np

from common import CloudAccount, CostCatagory


if __name__ == "__main__":
    # program arguments
    if len(argv) < 4:
        print(
            f"usage: {argv[0]} [unit group cc name] [owner cc name] [bu cc name] [xlsx #1] [xlsx #2] [xlsx #3]"
        )
        exit(1)

    unit_group_cc_name = argv[1]
    owner_cc_name = argv[2]
    bu_cc_name = argv[3]
    files = argv[4:]

    # check that all clouds were supplied
    if len(files) < 3:
        print("You have not specified all three cloud files")
        exit(1)

    # storage for different clouds
    unit_groups = CostCatagory(unit_group_cc_name)
    owners = CostCatagory(owner_cc_name)
    bus = CostCatagory(bu_cc_name)

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
                row.BU,
                row["Costcenter Unit Group"],
                row["Costcenter Unit Group Owner"],
            )
            print(account)

            unit_groups.add(account.unit_group, account)
            owners.add(account.unit_group_owner, account)
            bus.add(account.bu, account)

    print(unit_group_cc_name, unit_groups.update())
    print(owner_cc_name, owners.update())
    print(bu_cc_name, bus.update())

    sleep(5)

    print("Here is what we did...")

    sleep(5)

    print(unit_groups)
    print()
    print(bus)
    print()
    print(owners)

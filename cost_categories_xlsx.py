from csv import reader
from os import getenv
from sys import argv, exit
from time import sleep

import pandas as pd
import numpy as np

from common import CloudAccount, CostCatagory


if __name__ == "__main__":
    # program arguments
    if len(argv) < 4:
        print(
            f"usage: {argv[0]} [unit group cc name] [owner cc name] [bu cc name] [env cc name] [buid cc name] [xlsx #1] [xlsx #2] [xlsx #3]"
        )
        exit(1)

    unit_group_cc_name = argv[1]
    owner_cc_name = argv[2]
    bu_cc_name = argv[3]
    env_cc_name = argv[4]
    buid_cc_name = argv[5]
    files = argv[6:]

    # check that all clouds were supplied
    if len(files) < 3:
        print("You have not specified all three cloud files")
        exit(1)

    # storage for different clouds
    unit_groups = CostCatagory(unit_group_cc_name)
    owners = CostCatagory(owner_cc_name)
    bus = CostCatagory(bu_cc_name)
    envs = CostCatagory(env_cc_name)
    buids = CostCatagory(buid_cc_name)

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
                row["Environment"],
                row["BUid"],
            )

            unit_groups.add(account.unit_group, account)
            owners.add(account.unit_group_owner, account)
            bus.add(account.bu, account)
            envs.add(account.env, account)
            buids.add(account.env, account)

    print("\n\n\n\n==============")
    print(unit_groups)
    print(f"Please see the above for the new {unit_group_cc_name}")
    val = input("Should we apply this update? (yes/no): ")
    if val == "yes":
        print(unit_group_cc_name, unit_groups.update())

    val = input("Should we continue? (yes/no): ")
    if val != "yes":
        exit(0)

    print("\n\n\n\n==============")
    print(owners)
    print(f"Please see the above for the new {owner_cc_name}")
    val = input("Should we apply this update? (yes/no): ")
    if val == "yes":
        print(owner_cc_name, owners.update())

    val = input("Should we continue? (yes/no): ")
    if val != "yes":
        exit(0)

    print("\n\n\n\n==============")
    print(bus)
    print(f"Please see the above for the new {bu_cc_name}")
    val = input("Should we apply this update? (yes/no): ")
    if val == "yes":
        print(bu_cc_name, bus.update())

    val = input("Should we continue? (yes/no): ")
    if val != "yes":
        exit(0)

    print("\n\n\n\n==============")
    print(envs)
    print(f"Please see the above for the new {env_cc_name}")
    val = input("Should we apply this update? (yes/no): ")
    if val == "yes":
        print(env_cc_name, envs.update())
    
    print("\n\n\n\n==============")
    print(buids)
    print(f"Please see the above for the new {buid_cc_name}")
    val = input("Should we apply this update? (yes/no): ")
    if val == "yes":
        print(buid_cc_name, buids.update())

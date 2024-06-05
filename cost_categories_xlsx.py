from sys import argv, exit
from json import dumps

import pandas as pd
import numpy as np

from common import CloudAccount, CostCatagory


if __name__ == "__main__":
    # program arguments
    if len(argv) < 7:
        print(
            f"usage: {argv[0]} [unit group cc name] [owner cc name] [bu cc name] [env cc name] [buid cc name] [az rg apmid cc name] [xlsx #1] [xlsx #2] [xlsx #3]"
        )
        exit(1)

    unit_group_cc_name = argv[1]
    owner_cc_name = argv[2]
    bu_cc_name = argv[3]
    env_cc_name = argv[4]
    buid_cc_name = argv[5]
    azrgapmid_cc_name = argv[6]
    files = argv[7:]

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
    azrgapmid = CostCatagory(azrgapmid_cc_name)
    azrgapmid_buckets = {}

    # loop through file and pull in account information
    for file_csv in files:
        sheet = pd.read_excel(file_csv)
        sheet = sheet.replace({np.nan: None})

        for _, row in sheet.iterrows():
            # create instance of account with given data
            account = CloudAccount(
                row.Vendor,
                row["Payer account_identifier"],
                row["Payer account_name"],
                row.vendor_account_identifier,
                row.get("Resource_Group"),
                row.vendor_account_name,
                row.BU,
                row["Costcenter Unit Group"],
                row["Costcenter Unit Group Owner"],
                row["Environment"],
                row["BUid"],
                row.get("RG_APMID"),
            )

            unit_groups.add(account.unit_group, account)
            owners.add(account.unit_group_owner, account)
            bus.add(account.bu, account)
            envs.add(account.env, account)
            buids.add(account.buid, account)

            if account.apm_id:
                if account.apm_id in azrgapmid_buckets:
                    azrgapmid_buckets[account.apm_id].append(account)
                else:
                    azrgapmid_buckets[account.apm_id] = [account]

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

    azrgapmid_targets = []
    for bucket in azrgapmid_buckets:
        rules = []
        for rg in azrgapmid_buckets[bucket]:
            rules.append(
                {
                    "viewConditions": [
                        {
                            "type": "VIEW_ID_CONDITION",
                            "viewField": {
                                "fieldId": "azureSubscriptionGuid",
                                "fieldName": "Subscription id",
                                "identifier": "AZURE",
                                "identifierName": "Azure",
                            },
                            "viewOperator": "IN",
                            "values": [rg.identifier],
                        },
                        {
                            "type": "VIEW_ID_CONDITION",
                            "viewField": {
                                "fieldId": "azureResourceGroup",
                                "fieldName": "Resource group name",
                                "identifier": "AZURE",
                                "identifierName": "Azure",
                            },
                            "viewOperator": "IN" if rg.rg_identifier else "NULL",
                            "values": [rg.rg_identifier if rg.rg_identifier else ""],
                        },
                    ]
                }
            )

        azrgapmid_targets.append(
            {
                "name": bucket,
                "rules": rules,
            }
        )

    print("\n\n\n\n==============")
    print("\t", dumps(azrgapmid_targets, indent=4))
    print(f"Please see the above for the new {azrgapmid_cc_name}")
    val = input("Should we apply this update? (yes/no): ")
    if val == "yes":
        print(azrgapmid.update_cost_targets(azrgapmid_targets))

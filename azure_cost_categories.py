from csv import reader
from os import getenv
from sys import argv, exit
from time import sleep
from json import dumps

import pandas as pd
import numpy as np

from common import CloudAccount, CostCatagory


class AzureAccount:
    def __init__(
        self,
        payer_id: str,
        payer: str,
        sub_id: str,
        sub_name: str,
        rg_name: str,
    ):
        self.payer_id = payer_id
        self.payer = payer
        self.sub_id = sub_id
        self.sub_name = sub_name
        self.rg_name = rg_name

    def __dict__():
        return {"subscription": sub_id, "resource_group": rg_name}


if __name__ == "__main__":
    # program arguments
    if len(argv) < 2:
        print(f"usage: {argv[0]} [azure rg xlsx]")
        exit(1)

    file_csv = argv[1]

    # storage for different cc
    cost_center_cc = {}
    environment_cc = {}
    cost_center_manager_cc = {}
    bu_cc = {}
    bu_id_cc = {}

    sheet = pd.read_excel(file_csv, keep_default_na=False)

    cost_catagories = {}
    for column in sheet.columns[6:]:
        cost_catagories.update({column: {}})

    for i, row in sheet.iterrows():
        # create instance of account with given data
        account = AzureAccount(
            row["Payer_Account_ID"],
            row["Payer_Account_Name"],
            row["Subscription_ID"],
            row["Subscription_name"],
            row["Resource_Group"],
        )

        for cost_catagory in cost_catagories:
            bucket = str(row[cost_catagory])
            if bucket not in cost_catagory:
                cost_catagories[cost_catagory][bucket] = [account]
            else:
                cost_catagories[cost_catagory][bucket].append(account)

    for cost_catagory in cost_catagories.keys():
        cc = CostCatagory(cost_catagory)
        cost_targets = []

        for bucket in cost_catagories[cost_catagory]:
            rules = []
            for rg in cost_catagories[cost_catagory][bucket]:
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
                                "values": [rg.sub_id],
                            },
                            {
                                "type": "VIEW_ID_CONDITION",
                                "viewField": {
                                    "fieldId": "azureResourceGroup",
                                    "fieldName": "Resource group name",
                                    "identifier": "AZURE",
                                    "identifierName": "Azure",
                                },
                                "viewOperator": "IN" if rg.rg_name else "NULL",
                                "values": [rg.rg_name if rg.rg_name else ""],
                            },
                        ]
                    }
                )

            cost_targets.append(
                {
                    "name": bucket,
                    "rules": rules,
                }
            )

        print("\t", dumps(cost_targets, indent=4))

        print(
            f"\n\n\n\n==============\nPlease see the above for the new {cc.name} cost catagory"
        )
        val = input("Should we apply this update? (yes/no): ")
        if val == "yes":
            print(cc.update_cost_targets(cost_targets))

        val = input("Should we continue? (yes/no): ")
        if val != "yes":
            exit(0)

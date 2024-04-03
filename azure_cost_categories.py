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
        cost_center: str,
        environment: str,
        cost_center_manager: str,
        bu: str,
        bu_id: str,
    ):
        self.payer_id = payer_id
        self.payer = payer
        self.sub_id = sub_id
        self.sub_name = sub_name
        self.rg_name = rg_name
        self.cost_center = cost_center
        self.environment = environment
        self.cost_center_manager = cost_center_manager
        self.bu = bu
        self.bu_id = bu_id


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

    for i, row in sheet.iterrows():
        # create instance of account with given data
        account = AzureAccount(
            row["Payer_Account_ID"],
            row["Payer_Account_Name"],
            row["Subscription_ID"],
            row["Subscription_name"],
            row["Resource_Group"],
            row["Azure_RG_Costcenter"],
            row["Azure_RG_Environment"],
            row["Azure_RG_Costcenter_Manager"],
            row["Azure_RG_BU"],
            row["Azure_RG_BUid"],
        )

        if account.cost_center not in cost_center_cc:
            cost_center_cc[account.cost_center] = [account]
        else:
            cost_center_cc[account.cost_center].append(account)

        if account.environment not in environment_cc:
            environment_cc[account.environment] = [account]
        else:
            environment_cc[account.environment].append(account)

        if account.cost_center_manager not in cost_center_manager_cc:
            cost_center_manager_cc[account.cost_center_manager] = [account]
        else:
            cost_center_manager_cc[account.cost_center_manager].append(account)

        if account.bu not in bu_cc:
            bu_cc[account.bu] = [account]
        else:
            bu_cc[account.bu].append(account)

        if account.bu_id not in bu_id_cc:
            bu_id_cc[account.bu_id] = [account]
        else:
            bu_id_cc[account.bu_id].append(account)

    # Azure_RG_Costcenter
    cost_catagory = CostCatagory("Azure_RG_Costcenter")
    cost_targets = []

    for bucket in cost_center_cc:
        rules = []
        for rg in cost_center_cc[bucket]:
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

        # create bucket with all tags
        cost_targets.append(
            {
                "name": bucket,
                "rules": rules,
            }
        )

    # print(dumps(cost_targets, indent=4))

    print("\t", dumps(cost_targets, indent=4))

    print(
        f"\n\n\n\n==============\nPlease see the above for the new {cost_catagory.name} cost catagory"
    )
    val = input("Should we apply this update? (yes/no): ")
    if val == "yes":
        print(cost_catagory.update_cost_targets(cost_targets))

    val = input("Should we continue? (yes/no): ")
    if val != "yes":
        exit(0)

    # Azure_RG_Environment
    cost_catagory = CostCatagory("Azure_RG_Environment")
    cost_targets = []

    for bucket in environment_cc:
        rules = []
        for rg in environment_cc[bucket]:
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

        # create bucket with all tags
        cost_targets.append(
            {
                "name": bucket,
                "rules": rules,
            }
        )

    # print(dumps(cost_targets, indent=4))

    print("\t", dumps(cost_targets, indent=4))

    print(
        f"\n\n\n\n==============\nPlease see the above for the new {cost_catagory.name} cost catagory"
    )
    val = input("Should we apply this update? (yes/no): ")
    if val == "yes":
        print(cost_catagory.update_cost_targets(cost_targets))

    val = input("Should we continue? (yes/no): ")
    if val != "yes":
        exit(0)

    # Azure_RG_Costcenter_Manager
    cost_catagory = CostCatagory("Azure_RG_Costcenter_Manager")
    cost_targets = []

    for bucket in cost_center_manager_cc:
        rules = []
        for rg in cost_center_manager_cc[bucket]:
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

        # create bucket with all tags
        cost_targets.append(
            {
                "name": bucket,
                "rules": rules,
            }
        )

    # print(dumps(cost_targets, indent=4))

    print("\t", dumps(cost_targets, indent=4))

    print(
        f"\n\n\n\n==============\nPlease see the above for the new {cost_catagory.name} cost catagory"
    )
    val = input("Should we apply this update? (yes/no): ")
    if val == "yes":
        print(cost_catagory.update_cost_targets(cost_targets))

    val = input("Should we continue? (yes/no): ")
    if val != "yes":
        exit(0)

    # Azure_RG_BU
    cost_catagory = CostCatagory("Azure_RG_BU")
    cost_targets = []

    for bucket in bu_cc:
        rules = []
        for rg in bu_cc[bucket]:
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

        # create bucket with all tags
        cost_targets.append(
            {
                "name": bucket,
                "rules": rules,
            }
        )

    # print(dumps(cost_targets, indent=4))

    print("\t", dumps(cost_targets, indent=4))

    print(
        f"\n\n\n\n==============\nPlease see the above for the new {cost_catagory.name} cost catagory"
    )
    val = input("Should we apply this update? (yes/no): ")
    if val == "yes":
        print(cost_catagory.update_cost_targets(cost_targets))

    val = input("Should we continue? (yes/no): ")
    if val != "yes":
        exit(0)

    # Azure_RG_BUid
    cost_catagory = CostCatagory("Azure_RG_BUid")
    cost_targets = []

    for bucket in bu_id_cc:
        rules = []
        for rg in bu_id_cc[bucket]:
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

        # create bucket with all tags
        cost_targets.append(
            {
                "name": bucket,
                "rules": rules,
            }
        )

    # print(dumps(cost_targets, indent=4))

    print("\t", dumps(cost_targets, indent=4))

    print(
        f"\n\n\n\n==============\nPlease see the above for the new {cost_catagory.name} cost catagory"
    )
    val = input("Should we apply this update? (yes/no): ")
    if val == "yes":
        print(cost_catagory.update_cost_targets(cost_targets))

    val = input("Should we continue? (yes/no): ")
    if val != "yes":
        exit(0)

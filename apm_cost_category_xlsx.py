from sys import argv, exit
from re import sub

import pandas as pd

from common import CostCatagory


if __name__ == "__main__":
    # program arguments
    if len(argv) < 3:
        print(f"usage: {argv[0]} [Azure RG APMID CC Name][xlsx]")
        exit(1)

    azure_rg_apmid_name = argv[1]
    xlsx = argv[2]

    # core_tags = CostCatagory(core_tags_cc_name)

    # get the cost buckets for azure rg apmid
    azure_rg_apmid = CostCatagory(azure_rg_apmid_name)
    azure_rg_apmid_buckets = azure_rg_apmid.get()
    # for bucket in azure_rg_apmid_buckets.get("costTargets", []):
    #     print(bucket.get("name"))

    sheet = pd.read_excel(xlsx)

    cost_catagories = {}

    # create cc for all columns
    for column in sheet.columns[1:]:
        cost_catagories.update({column.replace(" ", ""): {}})

    # for every row in the excel
    for _, row in sheet.iterrows():
        # get the column names
        columns = row.keys()

        # for every column
        for column in columns[1:]:
            # no spaces in cc names
            cc_name = column.replace(" ", "")
            bucket_name = str(row[column]).replace(".0", "")
            bucket_name = sub("[^0-9a-zA-Z-@()., ']+", "", bucket_name)
            if bucket_name == "nan":
                bucket_name = "No Entry"

            # add tag to cc/bucket
            if bucket_name in cost_catagories[cc_name]:
                cost_catagories[cc_name][bucket_name].append(str(row.iloc[0]))
            else:
                cost_catagories[cc_name].update({bucket_name: [str(row.iloc[0])]})

    for cc in cost_catagories:
        # create cc object
        cost_catagory = CostCatagory(cc)
        cost_targets = []

        print("\n\n==============", cc)

        for bucket in cost_catagories[cc]:
            rules = [
                {
                    "viewConditions": [
                        {
                            "type": "VIEW_ID_CONDITION",
                            "viewField": {
                                "fieldId": "labels.value",
                                "fieldName": "user_apm_id",
                                "identifier": "LABEL",
                                "identifierName": "label",
                            },
                            "viewOperator": "IN",
                            "values": cost_catagories[cc][bucket],
                        },
                        {
                            "type": "VIEW_ID_CONDITION",
                            "viewField": {
                                "fieldId": "cloudProvider",
                                "fieldName": "Cloud Provider",
                                "identifier": "COMMON",
                                "identifierName": "Common",
                            },
                            "viewOperator": "NOT_IN",
                            "values": ["AZURE"],
                        },
                    ]
                },
                {
                    "viewConditions": [
                        {
                            "type": "VIEW_ID_CONDITION",
                            "viewField": {
                                "fieldId": "labels.value",
                                "fieldName": "apm-id",
                                "identifier": "LABEL",
                                "identifierName": "label",
                            },
                            "viewOperator": "IN",
                            "values": cost_catagories[cc][bucket],
                        },
                        {
                            "type": "VIEW_ID_CONDITION",
                            "viewField": {
                                "fieldId": "cloudProvider",
                                "fieldName": "Cloud Provider",
                                "identifier": "COMMON",
                                "identifierName": "Common",
                            },
                            "viewOperator": "NOT_IN",
                            "values": ["AZURE"],
                        },
                    ]
                },
            ]

            # find appids which exist in the azure rg cc
            common_appids = [
                x.get("name")
                for x in azure_rg_apmid_buckets.get("costTargets", [])
                if x.get("name").lower()
                in (name.lower() for name in cost_catagories[cc][bucket])
            ]
            if common_appids:
                rules.append(
                    {
                        "viewConditions": [
                            {
                                "type": "VIEW_ID_CONDITION",
                                "viewField": {
                                    "fieldId": azure_rg_apmid.uuid,
                                    "fieldName": azure_rg_apmid.name,
                                    "identifier": "BUSINESS_MAPPING",
                                    "identifierName": "Cost Categories",
                                },
                                "viewOperator": "IN",
                                "values": common_appids,
                            }
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

            print(
                "\t",
                bucket,
                "tags: ",
                cost_catagories[cc][bucket],
                f"{azure_rg_apmid.name}:",
                common_appids,
            )

        print(
            f"\n\n\n\n==============\nPlease see the above for the new {cc} cost catagory"
        )
        val = input("Should we apply this update? (yes/no): ")
        if val == "yes":
            print(cost_catagory.update_cost_targets(cost_targets))

        val = input("Should we continue? (yes/no): ")
        if val != "yes":
            exit(0)

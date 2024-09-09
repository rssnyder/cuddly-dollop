from sys import argv, exit
from json import dumps

import pandas as pd

from common import CostCatagory, Bucket, format_aws_account_id


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

            bucket_name = Bucket.clean_name(str(row[column]))

            if bucket_name == "nan":
                bucket_name = "No Entry"

            # get the key to use in the bucket rule
            tagKey = row.iloc[2]
            # and the value
            tagValue = row.iloc[1]
            # sometimes its empty?
            if pd.isna(tagValue):
                continue

            # get or format account id
            account = format_aws_account_id(str(row.iloc[0]))

            # add tag to cc/bucket
            # add tag to cc/bucket
            if bucket_name in cost_catagories[cc_name]:
                if tagKey in cost_catagories[cc_name][bucket_name]:
                    cost_catagories[cc_name][bucket_name][tagKey]["accounts"].append(
                        account
                    )
                    cost_catagories[cc_name][bucket_name][tagKey]["values"].append(
                        tagValue
                    )
                else:
                    cost_catagories[cc_name][bucket_name][tagKey] = {
                        "accounts": [account],
                        "values": [tagValue],
                    }
            else:
                cost_catagories[cc_name].update(
                    {
                        bucket_name: {
                            tagKey: {"accounts": [account], "values": [tagValue]}
                        }
                    }
                )

    for cc in cost_catagories:
        # create cc object
        cost_catagory = CostCatagory(cc)
        cost_targets = []

        print("\n\n==============", cc)

        for bucket in cost_catagories[cc]:
            conditions = []
            allValues = []
            # for aws, do account specific rules
            for tagKey in cost_catagories[cc][bucket]:
                values = list(set(cost_catagories[cc][bucket][tagKey]["values"]))
                # record all tag values for later use with gcp and azure
                allValues.extend(values)

                # skip if not an aws tag
                if not tagKey.startswith("user_"):
                    continue

                conditions.append(
                    {
                        "viewConditions": [
                            {
                                "type": "VIEW_ID_CONDITION",
                                "viewField": {
                                    "fieldId": "labels.value",
                                    "fieldName": tagKey,
                                    "identifier": "LABEL",
                                    "identifierName": "label",
                                },
                                "viewOperator": "IN",
                                "values": values,
                            },
                            {
                                "type": "VIEW_ID_CONDITION",
                                "viewField": {
                                    "fieldId": "awsUsageaccountid",
                                    "fieldName": "Account",
                                    "identifier": "AWS",
                                    "identifierName": "AWS",
                                },
                                "viewOperator": "IN",
                                "values": cost_catagories[cc][bucket][tagKey][
                                    "accounts"
                                ],
                            },
                        ]
                    }
                )

            allValuesDeDupe = list(set(allValues))
            # for gcp use all the tag values, with a set key
            conditions.append(
                {
                    "viewConditions": [
                        {
                            "type": "VIEW_ID_CONDITION",
                            "viewField": {
                                "fieldId": "labels.value",
                                "fieldName": "elvh-apm-id",
                                "identifier": "LABEL",
                                "identifierName": "label",
                            },
                            "viewOperator": "IN",
                            "values": allValuesDeDupe,
                        },
                        {
                            "type": "VIEW_ID_CONDITION",
                            "viewField": {
                                "fieldId": "cloudProvider",
                                "fieldName": "Cloud Provider",
                                "identifier": "COMMON",
                                "identifierName": "Common",
                            },
                            "viewOperator": "IN",
                            "values": ["GCP"],
                        },
                    ]
                }
            )

            # for azure use buckets from the azurerm cc which has buckets the names of the tag keys
            # find appids which exist in the azure rg cc
            common_appids = [
                x.get("name")
                for x in azure_rg_apmid_buckets.get("costTargets", [])
                if x.get("name").lower() in (name.lower() for name in allValuesDeDupe)
            ]
            if common_appids:
                conditions.append(
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

            # create bucket
            cost_targets.append(
                {
                    "name": bucket,
                    "rules": conditions,
                }
            )

        print(dumps(cost_targets, indent=2))

        print(
            f"\n\n\n\n==============\nPlease see the above for the new {cc} cost catagory"
        )
        val = input("Should we apply this update? (yes/no): ")
        if val == "yes":
            print(cost_catagory.update_cost_targets(cost_targets))

        val = input("Should we continue? (yes/no): ")
        if val != "yes":
            exit(0)

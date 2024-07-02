from sys import argv, exit
from re import sub
from json import dumps

import pandas as pd
from numpy import isnan

from common import CostCatagory


if __name__ == "__main__":
    # program arguments
    if len(argv) < 2:
        print(f"usage: {argv[0]} [xlsx]")
        exit(1)

    xlsx = argv[1]

    sheet = pd.read_excel(xlsx)

    cost_catagories = {}

    # create cc for all columns
    for column in sheet.columns[3:]:
        cost_catagories.update({column.replace(" ", ""): {}})

    # for every row in the excel
    for _, row in sheet.iterrows():
        # get the column names
        columns = row.keys()

        # for every column
        for column in columns[3:]:
            # no spaces in cc names
            cc_name = column.replace(" ", "")
            bucket_name = (
                str(row[column])
                .replace(".0", "")
                .replace(b"\\xa0".decode("unicode_escape"), " ")
            )
            bucket_name = sub("[^0-9a-zA-Z-@()., ']+", "", bucket_name)
            if bucket_name == "nan":
                bucket_name = "No Entry"

            tagKey = row.iloc[2]
            tagValue = row.iloc[1]
            if pd.isna(tagValue):
                continue
            account = str(row.iloc[0])
            if len(account) < 12:
                for _ in range(12 - len(account)):
                    account = "0" + account

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
            for tagKey in cost_catagories[cc][bucket]:
                values = list(set(cost_catagories[cc][bucket][tagKey]["values"]))
                allValues.extend(values)
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
            conditions.append(
                {
                    "viewConditions": [
                        {
                            "type": "VIEW_ID_CONDITION",
                            "viewField": {
                                "fieldId": "labels.value",
                                "fieldName": "costcenter",
                                "identifier": "LABEL",
                                "identifierName": "label",
                            },
                            "viewOperator": "IN",
                            "values": list(set(allValues)),
                        }
                    ]
                }
            )
            # create bucket with all tags
            cost_targets.append(
                {
                    "name": bucket,
                    "rules": conditions,
                }
            )

            print("\t", bucket, cost_catagories[cc][bucket])

        print(dumps(cost_targets))

        print(
            f"\n\n\n\n==============\nPlease see the above for the new {cc} cost catagory"
        )
        val = input("Should we apply this update? (yes/no): ")
        if val == "yes":
            print(cost_catagory.update_cost_targets(cost_targets))

        val = input("Should we continue? (yes/no): ")
        if val != "yes":
            exit(0)

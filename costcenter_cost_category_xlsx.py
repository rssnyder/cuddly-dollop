from csv import reader
from os import getenv
from sys import argv, exit
from time import sleep
from re import sub

import pandas as pd
import numpy as np

from common import CloudAccount, CostCatagory


if __name__ == "__main__":
    # program arguments
    if len(argv) < 2:
        print(f"usage: {argv[0]} [xlsx]")
        exit(1)

    xlsx = argv[1]

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
            # create bucket with all tags
            cost_targets.append(
                {
                    "name": bucket,
                    "rules": [
                        {
                            "viewConditions": [
                                {
                                    "type": "VIEW_ID_CONDITION",
                                    "viewField": {
                                        "fieldId": "labels.value",
                                        "fieldName": "user_costcenter",
                                        "identifier": "LABEL",
                                        "identifierName": "label",
                                    },
                                    "viewOperator": "IN",
                                    "values": cost_catagories[cc][bucket],
                                }
                            ]
                        },
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
                                    "values": cost_catagories[cc][bucket],
                                }
                            ]
                        },
                    ],
                }
            )

            print("\t", bucket, cost_catagories[cc][bucket])

        print(
            f"\n\n\n\n==============\nPlease see the above for the new {cc} cost catagory"
        )
        val = input("Should we apply this update? (yes/no): ")
        if val == "yes":
            print(cost_catagory.update_cost_targets(cost_targets))

        val = input("Should we continue? (yes/no): ")
        if val != "yes":
            exit(0)

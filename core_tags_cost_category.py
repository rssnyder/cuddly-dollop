from csv import reader
from os import getenv
from sys import argv
from time import sleep

import pandas as pd
import numpy as np

from common import CloudAccount, CostCatagory


if __name__ == "__main__":
    # program arguments
    if len(argv) < 3:
        print(f"usage: {argv[0]} [core tags cc name] [xlsx]")
        exit(1)

    core_tags_cc_name = argv[1]
    xlsx = argv[2]

    core_tags = CostCatagory(core_tags_cc_name)

    sheet = pd.read_excel(xlsx)

    cost_targets = []
    for _, row in sheet.iterrows():
        cost_targets.append(
            {
                "name": row["Core Tags Cost Buckets"],
                "rules": [
                    {
                        "viewConditions": [
                            {
                                "type": "VIEW_ID_CONDITION",
                                "viewField": {
                                    "fieldId": "labels.value",
                                    "fieldName": row["Harness Key"],
                                    "identifier": "LABEL",
                                    "identifierName": "label",
                                },
                                "viewOperator": "NOT_NULL",
                                "values": [""],
                            }
                        ]
                    }
                ],
            }
        )

    print(core_tags_cc_name, core_tags.update_cost_targets(cost_targets))

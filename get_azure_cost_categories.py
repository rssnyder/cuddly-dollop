from sys import argv

from csv import writer
from datetime import datetime


from common import CostCatagory

if __name__ == "__main__":
    # program arguments
    if len(argv) < 2:
        print(f"usage: {argv[0]} [cc name]")
        exit(1)

    cc_name = argv[1]

    cc = CostCatagory(cc_name)

    current_date = datetime.now()

    with open(
        f"azure_cost_category_{cc_name}_{current_date.strftime('%Y-%m-%d_%H:%M:%S')}.csv".replace(
            " ", "_"
        ).replace(
            ":", "_"
        ),
        "w",
    ) as file:
        header = "bucket,cloud,subscription,resourcegroup"
        file.write(header + "\n")

        for item in cc.get_cc().get("costTargets"):
            for rule in item.get("rules", []):
                condition = rule.get("viewConditions", [])
                file.write(
                    ",".join(
                        [
                            f'"{item.get("name").replace("Â", "A")}"',
                            condition[0].get("viewField", {}).get("identifier"),
                            condition[0].get("values", []).pop(),
                            condition[1].get("values", []).pop(),
                        ]
                    )
                    + "\n"
                )

from csv import reader
from os import getenv
from sys import argv
from time import sleep

from common import CloudAccount, CostCatagory


if __name__ == "__main__":

    # program arguments
    if len(argv) < 4:
        print(
            f"usage: {argv[0]} [unit group cc name] [bu cc name] [csv #1] [csv #2] [csv #3]"
        )
        exit(1)

    unit_group_cc_name = argv[1]
    bu_cc_name = argv[2]
    files = argv[3:]

    # check that all clouds were supplied
    if len(files) < 3:
        print("You have not specified all three cloud files")
        exit(1)

    # storage for different clouds
    unit_groups = CostCatagory(unit_group_cc_name)
    bus = CostCatagory(bu_cc_name)

    # loop through file and pull in account information
    for file_csv in files:
        with open(file_csv, "r") as cc_data:
            datareader = reader(cc_data)
            next(datareader)

            for row in datareader:

                # create instance of account with given data
                account = CloudAccount(
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                    row[6],
                    row[7],
                )

                unit_groups.add(account.unit_group, account)
                bus.add(account.bu, account)

    print(unit_groups.update())
    print(bus.update())

    sleep(5)

    print("Here is what we did...")

    sleep(5)

    print(unit_groups)
    print()
    print(bus)

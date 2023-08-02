# ccm-python
create cloud connectors and cost categories using python

# csv files

these scripts expect csv files. if you are using the excel file format you will need to save it as a csv (comma delimited)

# authentication

the following environment variables should be set:

HARNESS_PLATFORM_API_KEY: a harness api key

HARNESS_ACCOUNT_ID: your harness account identifier

# cost_catagories.py

create cost catagories in harness based on csvs for each cloud

usage: `python3 cost_catagories.py "Unit Group" BU [csv #1] [csv #2] [csv #3]`

# cloud_connectors.py

create cloud connectors based on csv file

[cross account role name] == role name in aws that trusts harness
[tenant id] == azure tenant id
[service account email] == gcp service account email given in harness ui when creating a gcp connector

usage: `cloud_connectors.py [cross account role name] [tenant id] [service account email] [csv #1] [csv #2] [csv #3]`

# cluster_connectors.py

create k8s and k8s ccm connectors for delegates seen at the account level

usage: `cluster_connectors.py`

# get_cloud_connectors.py

get the status of all AWS, Azure, and GCP cloud connectors

usage: `get_cloud_connectors.py`

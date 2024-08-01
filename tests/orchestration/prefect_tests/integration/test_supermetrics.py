"""Test Flow for pulling data from Supermetrics to Adls."""

import os

from viadot.orchestration.prefect.flows import supermetrics_to_adls
os.system("clear")

if __name__ == '__main__':
    google_ads_params = {
        "ds_id": "AW",
        "ds_accounts": ["1007802423"],
        "ds_user": "google@velux.com",
        "date_range_type": "last_month",
        "fields": [
            "Date",
            "Campaignname",
            "Clicks",
        ],
        "max_rows": 5,
    }

    supermetrics_to_adls(
        query_params=google_ads_params,
        adls_path="raw/supermetrics/google_ads_params.csv",
        supermetrics_credentials_secret='supermetrics',
        adls_credentials_secret='app-azure-cr-datalakegen2-dev',
        overwrite=True,
    )

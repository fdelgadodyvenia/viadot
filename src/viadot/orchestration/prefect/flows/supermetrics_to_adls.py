"""Flow for pulling data from CloudForCustomers to Adls."""

from typing import Any, Dict

from prefect import flow

from viadot.orchestration.prefect.tasks import (
    supermetrics_to_df,
    df_to_adls,
)


@flow
def supermetrics_to_adls(  # noqa: PLR0913, PLR0917
    # Supermetrics
    query_params: Dict[str, Any] = None,
    # ADLS
    adls_path: str | None = None,
    overwrite: bool = False,
    # Auth
    supermetrics_credentials_secret: str | None = None,
    supermetrics_config_key: str | None = None,
    adls_credentials_secret: str | None = None,
    adls_config_key: str | None = None,
    **kwargs: dict[str, Any] | None,
) -> None:
    """Download records from Supermetrics and upload them to Azure Data Lake.

    Args:
        query_params (dict(str, optional): Params to compose the query.
        adls_path (str): The destination path.
        overwrite (bool, optional): Whether to overwrite files in the lake. Defaults to
            False.
        supermetrics_credentials_secret (str, optional): The name of the Azure
            Key Vault secret storing the Supermetrics credentials. Defaults to None.
        supermetrics_config_key (str, optional): The key in the viadot config
            holding relevant credentials. Defaults to None.
        adls_credentials_secret (str, optional): The name of the Azure Key Vault secret
            storing the ADLS credentials. Defaults to None.
        adls_config_key (str, optional): The key in the viadot config holding relevant
            credentials. Defaults to None.
        kwargs: The parameters to pass to the DataFrame constructor.
    """
    df = supermetrics_to_df(
        query_params=query_params,
        credentials_secret=supermetrics_credentials_secret,
        config_key=supermetrics_config_key,
        **kwargs,
    )
    return df_to_adls(
        df=df,
        path=adls_path,
        credentials_secret=adls_credentials_secret,
        config_key=adls_config_key,
        overwrite=overwrite,
    )

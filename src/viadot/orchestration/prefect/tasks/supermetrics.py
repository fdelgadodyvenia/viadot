"""Tasks for interacting with Supermetrics."""

from typing import Any, Dict

import pandas as pd
from viadot.orchestration.prefect.utils import get_credentials
from viadot.sources import Supermetrics

from prefect import task


@task(retries=3, retry_delay_seconds=10, timeout_seconds=60 * 60)
def supermetrics_to_df(  # noqa: PLR0913, PLR0917
    query_params: Dict[str, Any] = None,
    credentials_secret: str | None = None,
    config_key: str | None = None,
    credentials: dict[str, Any] | None = None,
    **kwargs: dict[str, Any] | None,
) -> pd.DataFrame:
    """Extracts Cloud for Customers records as pd.DataFrame.

    Args:
        query_params (dict(str, optional): Params to compose the query. 
        credentials_secret (str, optional): The name of the secret storing the
            credentials.
            More info on: https://docs.prefect.io/concepts/blocks/
        config_key (str, optional): The key in the viadot config holding relevant
            credentials.
        credentials (dict, optional): Supermetrics credentials.
        kwargs: The parameters to pass to DataFrame constructor.

    Returns:
        pd.Dataframe: The pandas `DataFrame` containing data from the file.
    """
    if not (credentials_secret or config_key or credentials):
        msg = """Either `credentials_secret`, `config_key`, or `credentials`
            has to be specified and not empty."""
        raise ValueError(msg)

    credentials = credentials or get_credentials(credentials_secret)
    supermetrics = Supermetrics(
        query_params=query_params,
        credentials=credentials,
        config_key=config_key,
    )

    return supermetrics.to_df(**kwargs)

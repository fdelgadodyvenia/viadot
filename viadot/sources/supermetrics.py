import json
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from ..config import get_source_credentials
from ..exceptions import CredentialError
from ..utils import handle_api_response
from .base import Source

from pydantic import BaseModel


class SupermetricsCredentials(BaseModel):
    user: str
    api_key: str


class Supermetrics(Source):
    """
    A class implementing the Supermetrics API.

    Documentation for this API is located at:
    https://supermetrics.com/docs/product-api-getting-started/
    Usage limits: https://supermetrics.com/docs/product-api-usage-limits/.

    Parameters
    ----------
    config_key (str, optional): The key in the viadot config holding relevant
        credentials. Defaults to None.
    credentials : Dict[str, Any], optional
        Credentials for API connection configuration
        (`api_key` and `user`).
    query_params : Dict[str, Any], optional
        The parameters to pass to the GET query.
        See https://supermetrics.com/docs/product-api-get-data/ for full specification,
        by default None.
    """

    API_ENDPOINT = "https://api.supermetrics.com/enterprise/v2/query/data/json"

    def __init__(
        self,
        *args,
        credentials: SupermetricsCredentials = None,
        config_key: str = None,
        query_params: Dict[str, Any] = None,
        **kwargs,
    ):
        credentials = credentials or get_source_credentials(config_key)
            
        if not (credentials.get("user") and credentials.get("api_key")):
            raise CredentialError(
                "'user' and 'api_key' credentials are required."
            )
                        
        validated_creds = dict(
            SupermetricsCredentials(**credentials)
        )  # validate the credentials schema
        super().__init__(*args, credentials=validated_creds, **kwargs)

        self.api_key = self.credentials["api_key"]
        self.user = self.credentials["user"]

        self.query_params = query_params

    def to_json(self, timeout=(3.05, 60 * 30)) -> Dict[str, Any]:
        """
        Description:
            Download query results to a dictionary.
            Note that Supermetrics API will sometimes hang and not return any error
            message, so we're adding a timeout to GET.

            See [requests docs]
            (https://docs.python-requests.org/en/master/user/advanced/#timeouts)
            for an explanation of why this timeout value will work on long-running
            queries but fail fast on connection issues.

        Args:
            timeout (int, optional):  Defaults to 30 minuntes.

        Returns:
            Returning object himself transformed into JSON.
        """

        if not self.query_params:
            raise ValueError("Please build the query first")

        params = {"json": json.dumps(self.query_params)}
        headers = {"Authorization": f"Bearer {self.api_key}"}

        response = handle_api_response(
            url=self.API_ENDPOINT, params=params, headers=headers, timeout=timeout
        )
        return response.json()

    @classmethod
    def _get_col_names_google_analytics(
        cls,
        response: dict,
    ) -> List[str]:
        """
        Description:
            Get cols name.

        Args:
            response (dict):  Dictionary with the json response from API call.

        Returns:
            columns (list): List of Google Analytics columns names.
        """

        # Supermetrics allows pivoting GA data, in which case it generates
        # additional columns, which are not enlisted in response's query metadata
        # but are instead added as the first row of data.
        is_pivoted = any(
            field["field_split"] == "column"
            for field in response["meta"]["query"]["fields"]
        )

        if is_pivoted:
            if not response["data"]:
                raise ValueError(
                    "Couldn't find column names as query returned no data."
                )
            columns = response["data"][0]
        else:
            # non-pivoted data; query fields match result fields
            cols_meta = response["meta"]["query"]["fields"]
            columns = [col_meta["field_name"] for col_meta in cols_meta]
        return columns

    @classmethod
    def _get_col_names_other(cls, response: dict) -> List[str]:
        """
        Description:
            Get cols name.

        Args:
            response (dict):  Dictionary with the json response from API call.

        Returns:
            columns (list): List of columns names (to Google Analytics use
            _get_col_names_google_analytics().
        """

        cols_meta = response["meta"]["query"]["fields"]
        columns = [col_meta["field_name"] for col_meta in cols_meta]
        return columns

    def _get_col_names(self) -> List[str]:
        """
        Description:
            Get cols name.

        Args:
            None.

        Returns:
           list of columns names.
        """

        response: dict = self.to_json()
        if self.query_params["ds_id"] == "GA":
            return Supermetrics._get_col_names_google_analytics(response)
        else:
            return Supermetrics._get_col_names_other(response)

    def to_df(self, if_empty: str = "fail") -> pd.DataFrame:
        """
        Description:
            Download data into a pandas DataFrame.

            Note that Supermetric can calculate some fields on the fly and alias them
            in the returned result. For example, if the query requests the `position`
            field, Supermetric may return an `Average position` caclulated field.
            For this reason we take columns names from the actual results rather than
            from input fields.

        Args:
            if_empty (str, optional): What to do if query returned no data. Defaults
            to "warn".

        Return:
            Pandas DataFrame with json information.
        """

        try:
            columns = self._get_col_names()
        except ValueError:
            columns = None

        data = self.to_json()["data"]

        if data:
            df = pd.DataFrame(data[1:], columns=columns).replace("", np.nan)
        else:
            df = pd.DataFrame(columns=columns)

        if df.empty:
            self._handle_if_empty(if_empty)
    
        

        return df

    def query(self, params: Dict[str, Any]):
        """
        Description:
            Create the Query.

        Args:
            params (dict): Query parameters {param:value, }

        Return:
            Object updated.
        """

        self.query_params = params
        self.query_params["api_key"] = self.api_key
        return self

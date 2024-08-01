"""Module Test Supermetrics Class."""
import unittest
from unittest import mock
import pytest
from viadot.sources.supermetrics import Supermetrics
from viadot.exceptions import CredentialError  # Import the correct exception


class TestSupermetrics:
    """Test Supermetrics Class."""

    @pytest.fixture(scope='function')
    def supermetrics(self):
        """Test Supermetrics Instance."""
        credentials = {"user": "test_user", "api_key": "test_api_key"}
        return Supermetrics(credentials=credentials)

    @mock.patch('viadot.sources.supermetrics.handle_api_response')
    def test_to_json(self, mock_handle_api_response, supermetrics):
        """Test to_json method."""
        mock_handle_api_response.return_value.json.return_value = \
            {"data": [], "meta": {"query": {"fields": []}}}
        supermetrics.query({"ds_id": "test_id"})
        result = supermetrics.to_json()
        assert "data" in result
        assert "meta" in result

    def test__get_col_names_google_analytics(self, supermetrics):
        """Test get_col_names_google_analytics method."""
        response = {
            "data": [["header1", "header2"], ["row1col1", "row1col2"]],
            "meta": {"query": {"fields": [{"field_name": "header1",
                                           "field_split": "column"},
                                          {"field_name": "header2",
                                           "field_split": "column"}]}}
        }
        columns = supermetrics._get_col_names_google_analytics(response)
        assert columns == ["header1", "header2"]

    def test__get_col_names_google_analytics_no_data(self, supermetrics):
        """Test get_col_names_google_analytics_no_data method."""
        response = {
            "data": [],
            "meta": {"query": {"fields": [{"field_name": "header1",
                                           "field_split": "column"},
                                          {"field_name": "header2",
                                           "field_split": "column"}]}}
        }
        with pytest.raises(ValueError, match="Couldn't find column names as query \
                                              returned no data."):
            supermetrics._get_col_names_google_analytics(response)

    def test__get_col_names_other(self, supermetrics):
        """Test get_col_names_other method."""
        response = {
            "meta": {
                "query": {
                    "fields": [
                        {"field_name": "header1"},
                        {"field_name": "header2"}
                    ]
                }
            }
        }
        columns = supermetrics._get_col_names_other(response)
        assert columns == ["header1", "header2"]

    @mock.patch.object(Supermetrics, 'to_json')
    def test__get_col_names(self, mock_to_json, supermetrics):
        """Test get_col_names method."""
        mock_to_json.return_value = {
            "data": [
                ["header1", "header2"],
                ["row1col1", "row1col2"]
            ],
            "meta": {
                "query": {
                    "fields": [
                        {
                            "field_name": "header1",
                            "field_split": "column"
                        },
                        {
                            "field_name": "header2",
                            "field_split": "column"
                        }
                    ]
                }
            }
        }
        supermetrics.query({"ds_id": "GA"})
        columns = supermetrics._get_col_names()
        assert columns == ["header1", "header2"]

    @mock.patch.object(Supermetrics, 'to_json')
    def test_to_df(self, mock_to_json, supermetrics):
        """Test to_df method."""
        mock_to_json.return_value = {
            "data": [["header1", "header2"], ["row1col1", "row1col2"]],
            "meta": {"query": {"fields": [{"field_name": "header1"},
                                          {"field_name": "header2"}]}}
        }
        supermetrics.query({"ds_id": "test_id"})
        df = supermetrics.to_df()
        assert not df.empty
        expected_columns = ["header1", "header2", "_viadot_source",
                            "_viadot_downloaded_at_utc"]
        assert list(df.columns) == expected_columns

    def test_query(self, supermetrics):
        """Test query method."""
        params = {"ds_id": "test_id"}
        supermetrics.query(params)
        assert supermetrics.query_params["ds_id"] == "test_id"
        assert supermetrics.query_params["api_key"] == "test_api_key"

    def test_invalid_credentials(self):
        """Test if invalid credentials."""
        with pytest.raises(CredentialError, match="'user' and 'api_key' \
                                                    credentials are required."):
            Supermetrics(credentials={"user": "", "api_key": ""})

    def test_no_query_params(self, supermetrics):
        """Test if no query_params."""
        with pytest.raises(ValueError, match="Please build the query first"):
            supermetrics.to_json()

    @mock.patch.object(Supermetrics, '_handle_if_empty')
    @mock.patch.object(Supermetrics, 'to_json')
    def test_to_df_empty(self, mock_to_json, mock_handle_if_empty, supermetrics):
        """Test if df empty."""
        mock_to_json.return_value = {
            "data": [],
            "meta": {
                "query": {
                    "fields": [
                        {"field_name": "header1"},
                        {"field_name": "header2"}
                    ]
                }
            }
        }
        supermetrics.query({"ds_id": "test_id"})
        df = supermetrics.to_df(if_empty="handle")
        assert df.empty
        mock_handle_if_empty.assert_called_once_with("handle")

    @mock.patch('viadot.sources.supermetrics.handle_api_response')
    def test_handle_api_response_error(self, mock_handle_api_response, supermetrics):
        """Test if api response error."""
        mock_handle_api_response.side_effect = Exception("API error")
        supermetrics.query({"ds_id": "test_id"})
        with pytest.raises(Exception, match="API error"):
            supermetrics.to_json()


if __name__ == '__main__':
    unittest.main()

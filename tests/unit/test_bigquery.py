import pandas as pd
import pandas_gbq
import pytest

from viadot.sources import BigQuery


@pytest.fixture(scope="function")
def BIGQ():
    BQ = BigQuery(config_key="BIGQUERY_TESTS")
    yield BQ


QUERY_PIVOTED = """
        SELECT name, SUM(number) AS total
           FROM `bigquery-public-data.usa_names.usa_1910_2013`
        GROUP BY name, gender
        ORDER BY total DESC 
        LIMIT 4
        """

RESPONSE_PIVOTED = {
    "name": {0: "James", 1: "John", 2: "Robert", 3: "Michael"},
    "total": {0: 4924235, 1: 4818746, 2: 4703680, 3: 4280040},
}


def test_query_to_df(BIGQ):
    # Testing function which returns a DataFrame provided by query from BigQuery API.
    df_expected = BIGQ.query_to_df(query=QUERY_PIVOTED)
    assert df_expected.to_dict() == RESPONSE_PIVOTED


def test_query_is_df(BIGQ):
    # Checking if the output of the function query_to_df is pd.DataFrame object
    df = BIGQ.query_to_df(QUERY_PIVOTED)
    assert isinstance(df, pd.DataFrame)


def test_list_project(BIGQ):
    # Testing function which returns project_id from credentials.
    project = BIGQ.get_project_id()
    assert project == "manifest-geode-341308"


def test_list_datasets(BIGQ):
    # Testing function which returns datasets from project
    datasets = list(BIGQ.list_datasets())
    assert datasets == ["manigeo", "official_empty"]


def test_list_tables(BIGQ):
    # Testing function which returns tables name from project
    table_id1 = "manigeo.manigeo_tab"
    table_id2 = "manigeo.manigeo_tab1"
    table_id3 = "manigeo.manigeo_tab2"
    table_id4 = "manigeo.space"
    df = pd.DataFrame({"my_value": ["val1", "val2", "val3"]})
    pandas_gbq.to_gbq(df, table_id1, if_exists="replace")
    pandas_gbq.to_gbq(df, table_id2, if_exists="replace")
    pandas_gbq.to_gbq(df, table_id3, if_exists="replace")
    pandas_gbq.to_gbq(df, table_id4, if_exists="replace")
    datasets = BIGQ.list_datasets()
    tables = list(BIGQ.list_tables(datasets[0]))
    assert tables == ["space", "manigeo_tab1", "manigeo_tab", "manigeo_tab2"]

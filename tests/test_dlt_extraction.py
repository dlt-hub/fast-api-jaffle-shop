"""
This tests extracts the full dataset with the dlt rest_api source
# NOTE: for speed reasons we limit to orders in january 2017
"""

import pytest

import dlt
from dlt.destinations import duckdb

import requests
from fastapi.testclient import TestClient
from app.main import app

from dlt.sources.rest_api import rest_api_source

from tests.utils import EXPECTED_TABLES_COUNTS_JANUARY_2017

app = TestClient(app)


class FastAPISession(requests.Session):
    def __init__(self, client):
        super().__init__()
        self.client = client

    def send(self, prepared_request, **kwargs):
        return self.client.request(
            method=prepared_request.method, url=prepared_request.url
        )


def row_counts(dataset: dlt.Dataset, tables: list[str] = None) -> dict[str, int]:
    counts = dataset.row_counts(table_names=tables).arrow().to_pydict()
    return {t: c for t, c in zip(counts["table_name"], counts["row_count"])}


def test_extract_full_dataset():
    """
    This tests extracts the full dataset with the dlt rest_api source
    """
    source = rest_api_source(
        {
            "client": {
                "base_url": "http://localhost:8000/api/v1",
                "paginator": {
                    "type": "header_link",
                },
                "session": FastAPISession(app),
            },
            "resources": [
                "customers",
                "products",
                "stores",
                "supplies",
                # orders includes items
                # we only load orders for january 2017
                {
                    "name": "orders",
                    "endpoint": {
                        "path": "orders",
                        "params": {
                            "page_size": 1000,
                            "start_date": "2017-01-01",
                            "end_date": "2017-01-31",
                        },
                    },
                },
            ],
        },
    )

    pipeline = dlt.pipeline(
        pipeline_name="rest_api_example",
        destination=duckdb(credentials="test.db"),
        dataset_name="rest_api_data",
        dev_mode=True,
    )

    pipeline.run(source)
    assert row_counts(pipeline.dataset()) == EXPECTED_TABLES_COUNTS_JANUARY_2017


@pytest.mark.skip(reason="This is a live test against the deployed shop")
def test_live_jaffle_shop():
    """
    This tests extracts the full dataset with the dlt rest_api source
    """
    source = rest_api_source(
        {
            "client": {
                "base_url": "https://fast-api-jaffle-shop-jz2mh.ondigitalocean.app",
                "paginator": {
                    "type": "header_link",
                },
                "session": FastAPISession(app),
            },
            "resources": [
                "customers",
                "products",
                "stores",
                "supplies",
                # orders includes items
                # we only load orders for january 2017
                {
                    "name": "orders",
                    "endpoint": {
                        "path": "orders",
                        "params": {
                            "start_date": "2017-01-01",
                            "end_date": "2017-01-31",
                        },
                    },
                },
            ],
        },
    )

    pipeline = dlt.pipeline(
        pipeline_name="rest_api_example",
        destination=duckdb(credentials="test.db"),
        dataset_name="rest_api_data",
        dev_mode=True,
    )

    pipeline.run(source)
    assert row_counts(pipeline.dataset()) == {
        "customers": 935,
        "products": 10,
        "stores": 6,
        "supplies": 65,
        "orders": 3303,  # 3303 orders in january 2017
        "orders__items": 5072,
    }


def test_expected_columns_schema():
    """
    This tests extracts the full dataset with the dlt rest_api source
    """
    source = rest_api_source(
        {
            "client": {
                "base_url": "http://localhost:8000/api/v1",
                "paginator": {
                    "type": "header_link",
                },
                "session": FastAPISession(app),
            },
            "resources": [
                "customers",
                "products",
                "stores",
                "supplies",
                # orders includes items
                # we only load orders for january 2017
                {
                    "name": "orders",
                    "endpoint": {
                        "path": "orders",
                        "params": {
                            "page_size": 1000,
                            "start_date": "2017-01-01",
                            "end_date": "2017-01-31",
                        },
                    },
                },
            ],
        },
    )
    pipeline = dlt.pipeline(
        pipeline_name="rest_api_example",
        destination=duckdb(credentials="test.db"),
        dataset_name="rest_api_data",
        dev_mode=True,
    )
    pipeline.run(source)

    expected_table_columns = {
        "customers": {
            "id": {"name": "id", "data_type": "text", "nullable": True},
            "name": {"name": "name", "data_type": "text", "nullable": True},
        },
        "products": {
            "sku": {"name": "sku", "data_type": "text", "nullable": True},
            "name": {"name": "name", "data_type": "text", "nullable": True},
            "type": {"name": "type", "data_type": "text", "nullable": True},
            "price": {"name": "price", "data_type": "double", "nullable": True},
            "description": {
                "name": "description",
                "data_type": "text",
                "nullable": True,
            },
        },
        "stores": {
            "id": {"name": "id", "data_type": "text", "nullable": True},
            "name": {"name": "name", "data_type": "text", "nullable": True},
            "opened_at": {
                "name": "opened_at",
                "data_type": "timestamp",
                "nullable": True,
            },
            "tax_rate": {"name": "tax_rate", "data_type": "double", "nullable": True},
        },
        "supplies": {
            "id": {"name": "id", "data_type": "text", "nullable": True},
            "name": {"name": "name", "data_type": "text", "nullable": True},
            "cost": {"name": "cost", "data_type": "double", "nullable": True},
            "perishable": {"name": "perishable", "data_type": "bool", "nullable": True},
            "sku": {"name": "sku", "data_type": "text", "nullable": True},
        },
        "orders": {
            "id": {"name": "id", "data_type": "text", "nullable": True},
            "customer_id": {
                "name": "customer_id",
                "data_type": "text",
                "nullable": True,
            },
            "store_id": {"name": "store_id", "data_type": "text", "nullable": True},
            "ordered_at": {
                "name": "ordered_at",
                "data_type": "timestamp",
                "nullable": True,
            },
            "subtotal": {"name": "subtotal", "data_type": "double", "nullable": True},
            "tax_paid": {"name": "tax_paid", "data_type": "double", "nullable": True},
            "order_total": {
                "name": "order_total",
                "data_type": "double",
                "nullable": True,
            },
        },
        "orders__items": {
            "id": {"name": "id", "data_type": "text", "nullable": True},
            "order_id": {"name": "order_id", "data_type": "text", "nullable": True},
            "sku": {"name": "sku", "data_type": "text", "nullable": True},
        },
    }

    for expected_table_name, expected_columns in expected_table_columns.items():
        table = pipeline.default_schema.tables[expected_table_name]
        table_columns = table["columns"]
        for expected_col_name, expected_col in expected_columns.items():
            assert table_columns[expected_col_name] == expected_col

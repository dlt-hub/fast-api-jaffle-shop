# FastAPI Jaffle Shop

This is a FastAPI version of the dbt jaffle shop project. The jaffle shop dataset is copied from [dbt jaffle data](https://github.com/dbt-labs/jaffle-shop/jaffle-data).

When the API is running, docs are available at /docs. For all entities, there are collection and single entity endpoints to retrieve the data. The collection endpoints are paginated and have a limit of 100 items. The link to the next page is returned in the response headers. The orders endpoint includes the order items nested inside each order object.

## Requirements

This project requires python 3.10+ and uv to be installed.

## Run tests

Some tests are quite slow as the dataset is quite large. To run the tests faster, use the following command:

```bash
make test-fast
```

All tests can be run with:

```bash
make test
```

## Run dev with reload

```bash
make run-dev
```

## Run uvicorn

```bash
make run
```

## Folder Structure

```bash
/app - FastAPI app
/seed - Seed data as csv files from dbt jaffle shop project
```

## Deployment

This app is currently deployed to the dlthub digital ocean app platform. Pushes to the main branch will result in a deployment. Please run `make freeze-requirements` to update the requirements.txt file from the uv lockfile, as that is what Digital Ocean uses to install the dependencies.

## Example dlt rest api source to sync orders from january 2017 and all other entities fully

```python
from dlt.sources.rest_api import rest_api_source

source = rest_api_source(
    {
        "client": {
                "base_url": "https://jaffle-shop.dlthub.com/",
                "paginator": {
                    "type": "header_link",
                },
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
```

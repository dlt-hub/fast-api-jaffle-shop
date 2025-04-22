"""
All jaffle shop routers for api v1
"""

from typing import List

import duckdb
from urllib.parse import urlencode
from fastapi import APIRouter, Depends, Response, Request

from app.db import get_db
from app.const import DEFAULT_PAGE_SIZE, API_V1_PREFIX
from app.models import Customer, Order, Item, Product, Store, Supply

general_router = APIRouter(tags=["general"])
customers_router = APIRouter(tags=["customers"])
orders_router = APIRouter(tags=["orders"])
item_router = APIRouter(tags=["items"])
product_router = APIRouter(tags=["products"])
supplies_router = APIRouter(tags=["supplies"])
store_router = APIRouter(tags=["stores"])


def _get_list_response(db: duckdb.DuckDBPyConnection, query: str):
    """
    Get a list response from a collection endpoint
    """
    cursor = db.sql(query)
    column_names = [desc[0] for desc in cursor.description]
    return [dict(zip(column_names, row)) for row in cursor.fetchall()]


def _get_paged_response(
    db: duckdb.DuckDBPyConnection,
    request: Request,
    table_name: str,
    page: int = 1,
    response: Response = None,
    where_clause: str = "",
    sort_by: str = "",
    page_size: int = DEFAULT_PAGE_SIZE,
):
    """
    Get a paged response from a collection endpoint
    Will insert next header if applicable
    """

    offset = (page - 1) * page_size
    last_item = offset + page_size
    count = db.query(f"SELECT COUNT(*) FROM {table_name} {where_clause}").fetchone()[0]

    # get base url from request
    # forwarded_host = request.headers.get(
    #     "X-Forwarded-Host", request.headers.get("Host")
    # )
    # scheme = request.headers.get("X-Forwarded-Proto", "http")

    url = API_V1_PREFIX + f"/{table_name}"
    query_params = dict(request.query_params)
    if last_item < count and response:
        query_params["page"] = page + 1
        next_link = f'<{url}?{urlencode(query_params)}>; rel="next"'
        response.headers["Link"] = next_link

    return _get_list_response(
        db,
        f"SELECT * FROM {table_name} {where_clause} {sort_by} LIMIT {page_size} OFFSET {offset}",
    )


def _get_single_response(db: duckdb.DuckDBPyConnection, query: str):
    """
    Get a single response from a collection endpoint
    """
    cursor = db.sql(query)
    column_names = [desc[0] for desc in cursor.description]
    return dict(zip(column_names, cursor.fetchone()))


#
# Customers
#


@general_router.get("/row-counts")
async def row_counts(db: duckdb.DuckDBPyConnection = Depends(get_db)):
    selected_tables = ["customers", "orders", "items", "products", "stores", "supplies"]
    queries = []
    for table in selected_tables:
        queries.append(
            f"SELECT '{table}' as table_name, COUNT(*) as row_count FROM {table}"
        )

    query = " UNION ALL ".join(queries)
    return _get_list_response(db, query)


@customers_router.get(
    "/customers",
    response_model=List[Customer],
    description=(
        "Returns a paginated list of customers.\n\n"
        "Pagination is controlled via the `page` query parameter (see `page`).\n\n"
        "Each page returns a fixed number of results (see `page_size`).\n\n"
        "If more results are available, the response will include a `Link` header with `rel=\"next\"` "
        "that points to the next page.\n\n"
    )
)
async def get_customers(
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    response: Response = None,
    request: Request = None,
    db: duckdb.DuckDBPyConnection = Depends(get_db),
):
    return _get_paged_response(
        db=db,
        request=request,
        table_name="customers",
        page=page,
        response=response,
        page_size=page_size,
    )


@customers_router.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(
    customer_id: str, db: duckdb.DuckDBPyConnection = Depends(get_db)
):
    return _get_single_response(
        db, f"SELECT * FROM customers WHERE id = '{customer_id}'"
    )


#
# Orders
#


def _enrich_orders(db: duckdb.DuckDBPyConnection, orders: list[dict]):
    """
    Enrich orders with list of items
    """
    for order in orders:
        order["items"] = _get_list_response(
            db, f"SELECT * FROM items WHERE order_id = '{order['id']}'"
        )
    return orders


@orders_router.get(
    "/orders",
    response_model=List[Order],
    description=(
        "Returns a paginated list of orders.\n\n"
        "Pagination is controlled via the `page` query parameter (see `page`).\n\n"
        "Each page returns a fixed number of results (see `page_size`).\n\n"
        "If more results are available, the response will include a `Link` header with `rel=\"next\"` "
        "that points to the next page.\n\n"
    )
)
async def get_orders(
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    start_date: str = None,
    end_date: str = None,
    response: Response = None,
    request: Request = None,
    db: duckdb.DuckDBPyConnection = Depends(get_db),
):
    where_clause = ""
    if start_date:
        where_clause += f" AND ordered_at::DATE >= '{start_date}'"
    if end_date:
        where_clause += f" AND ordered_at::DATE <= '{end_date}'"
    if where_clause:
        where_clause = f"WHERE {where_clause[5:]}"
    orders = _get_paged_response(
        db=db,
        request=request,
        table_name="orders",
        page=page,
        page_size=page_size,
        response=response,
        where_clause=where_clause,
    )
    return _enrich_orders(db, orders)


@orders_router.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: str, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    return _enrich_orders(
        db, [_get_single_response(db, f"SELECT * FROM orders WHERE id = '{order_id}'")]
    )[0]


#
# Items
#
@item_router.get(
    "/items",
    response_model=List[Item],
    description=(
        "Returns a paginated list of items.\n\n"
        "Pagination is controlled via the `page` query parameter (see `page`).\n\n"
        "Each page returns a fixed number of results (see `page_size`).\n\n"
        "If more results are available, the response will include a `Link` header with `rel=\"next\"` "
        "that points to the next page.\n\n"
    )
)
async def get_items(
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    response: Response = None,
    request: Request = None,
    db: duckdb.DuckDBPyConnection = Depends(get_db),
):
    return _get_paged_response(
        db=db,
        request=request,
        table_name="items",
        page=page,
        response=response,
        page_size=page_size,
    )


@item_router.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: str, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    return _get_single_response(db, f"SELECT * FROM items WHERE id = '{item_id}'")


#
# Products
#
@product_router.get(
    "/products",
    response_model=List[Product],
    description=(
        "Returns a paginated list of products.\n\n"
        "Pagination is controlled via the `page` query parameter (see `page`).\n\n"
        "Each page returns a fixed number of results (see `page_size`).\n\n"
        "If more results are available, the response will include a `Link` header with `rel=\"next\"` "
        "that points to the next page.\n\n"
    )
)
async def get_products(
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    response: Response = None,
    request: Request = None,
    db: duckdb.DuckDBPyConnection = Depends(get_db),
):
    return _get_paged_response(
        db=db,
        request=request,
        table_name="products",
        page=page,
        response=response,
        page_size=page_size,
    )


@product_router.get("/products/{sku}", response_model=Product)
async def get_product(sku: str, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    return _get_single_response(db, f"SELECT * FROM products WHERE sku = '{sku}'")


#
# Stores
#
@store_router.get(
    "/stores",
    response_model=List[Store],
    description=(
        "Returns a paginated list of stores.\n\n"
        "Pagination is controlled via the `page` query parameter (see `page`).\n\n"
        "Each page returns a fixed number of results (see `page_size`).\n\n"
        "If more results are available, the response will include a `Link` header with `rel=\"next\"` "
        "that points to the next page.\n\n"
    )
)
async def get_stores(
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    response: Response = None,
    request: Request = None,
    db: duckdb.DuckDBPyConnection = Depends(get_db),
):
    return _get_paged_response(
        db=db,
        request=request,
        table_name="stores",
        page=page,
        response=response,
        page_size=page_size,
    )


@store_router.get("/stores/{store_id}", response_model=Store)
async def get_store(store_id: str, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    return _get_single_response(db, f"SELECT * FROM stores WHERE id = '{store_id}'")


#
# Supplies
#
@supplies_router.get(
    "/supplies",
    response_model=List[Supply],
    description=(
        "Returns a paginated list of supplies.\n\n"
        "Pagination is controlled via the `page` query parameter (see `page`).\n\n"
        "Each page returns a fixed number of results (see `page_size`).\n\n"
        "If more results are available, the response will include a `Link` header with `rel=\"next\"` "
        "that points to the next page.\n\n"
    )
)
async def get_supplies(
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    response: Response = None,
    request: Request = None,
    db: duckdb.DuckDBPyConnection = Depends(get_db),
):
    return _get_paged_response(
        db=db,
        request=request,
        table_name="supplies",
        page=page,
        response=response,
        page_size=page_size,
    )


@supplies_router.get("/supplies/{supply_id}", response_model=Supply)
async def get_supply(supply_id: str, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    return _get_single_response(db, f"SELECT * FROM supplies WHERE id = '{supply_id}'")

import duckdb
import logging

logger = logging.getLogger()


POPULATED_DB: duckdb.DuckDBPyConnection | None = None


def get_db() -> duckdb.DuckDBPyConnection:
    """Create in memory duckdb database from seed csv files"""
    global POPULATED_DB

    if POPULATED_DB is None:
        db = duckdb.connect(database=":memory:")
        db.sql("SET memory_limit = '500MB'")
        db.sql("SET threads = 1")
        db.sql(
            "CREATE TABLE customers AS SELECT * FROM read_csv('seed/raw_customers.csv');"
        )
        db.sql("CREATE TABLE orders AS SELECT * FROM read_csv('seed/raw_orders.csv');")
        db.sql("CREATE TABLE items AS SELECT * FROM read_csv('seed/raw_items.csv');")
        db.sql(
            "CREATE TABLE products AS SELECT * FROM read_csv('seed/raw_products.csv');"
        )
        db.sql("CREATE TABLE stores AS SELECT * FROM read_csv('seed/raw_stores.csv');")
        db.sql(
            "CREATE TABLE supplies AS SELECT * FROM read_csv('seed/raw_supplies.csv');"
        )
        POPULATED_DB = db

        logger.warning("Loaded seed data")
        logger.warning(
            f"Customers: {db.sql('SELECT COUNT(*) FROM customers').fetchone()[0]}"
        )
        logger.warning(f"Orders: {db.sql('SELECT COUNT(*) FROM orders').fetchone()[0]}")
        logger.warning(f"Items: {db.sql('SELECT COUNT(*) FROM items').fetchone()[0]}")
        logger.warning(
            f"Products: {db.sql('SELECT COUNT(*) FROM products').fetchone()[0]}"
        )
        logger.warning(f"Stores: {db.sql('SELECT COUNT(*) FROM stores').fetchone()[0]}")
        logger.warning(
            f"Supplies: {db.sql('SELECT COUNT(*) FROM supplies').fetchone()[0]}"
        )

    return POPULATED_DB

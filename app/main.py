from fastapi import FastAPI
from app import routers
from app.const import API_V1_PREFIX
from app.models import Message
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="dltHub Jaffle Shop API",
    version="1.0.0",
    description="The dltHub Jaffle Shop API is a RESTful API that provides access to the dbt Jaffle Shop dataset. The code for this API is open source and available at https://github.com/dlt-hub/fast-api-jaffle-shop.",
    license_info={
        "name": "APACHE",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    contact={
        "name": "dltHub",
        "url": "https://dlthub.com",
        "email": "support@dlt.hub",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,  # only if you use cookies/Authorization
)

# api v1
app.include_router(routers.customers_router, prefix=API_V1_PREFIX)
app.include_router(routers.orders_router, prefix=API_V1_PREFIX)
app.include_router(routers.item_router, prefix=API_V1_PREFIX)
app.include_router(routers.product_router, prefix=API_V1_PREFIX)
app.include_router(routers.supplies_router, prefix=API_V1_PREFIX)
app.include_router(routers.store_router, prefix=API_V1_PREFIX)
app.include_router(routers.general_router, prefix=API_V1_PREFIX)


@app.get("/", response_model=Message)
async def root():
    return {
        "message": "dltHub Jaffle Shop API. Docs are available at /docs. OpenAPI Spec is available at /openapi.json. Please be considerate with the number of requests you make to this API."
    }


@app.get("/ping", response_model=Message)
async def ping():
    return {"message": "pong"}

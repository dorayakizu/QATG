from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.config import settings
from services.odoo_client import odoo_client

from routers.auth import router as auth_router
from routers.employee import router as employee_router
from routers.department import router as department_router
from routers.product import router as product_router
from routers.sale_order import router as sale_order_router
from routers.attribute import router as attribute_router
from routers.bom import router as bom_router

@asynccontextmanager
async def lifespan(app: FastAPI):

    await odoo_client.startup()

    print("Odoo Client Started")

    yield

    await odoo_client.shutdown()

    print("Odoo Client Closed")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

app.include_router(auth_router)
app.include_router(employee_router)
app.include_router(department_router)
app.include_router(sale_order_router)
app.include_router(product_router)
app.include_router(attribute_router)
app.include_router(bom_router)

from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.config import settings
from schemas.employee import EmployeeCreate, EmployeeUpdate
from services.odoo_client import odoo_client


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


# ==========================================
# GET ALL
# ==========================================
@app.get("/employees")
async def get_employees():

    return await odoo_client.request(
        "GET",
        "/api/employees"
    )


# ==========================================
# GET ONE
# ==========================================
@app.get("/employees/{employee_id}")
async def get_employee(employee_id: int):

    return await odoo_client.request(
        "GET",
        f"/api/employees/{employee_id}"
    )


# ==========================================
# CREATE
# ==========================================
@app.post("/employees")
async def create_employee(
    employee: EmployeeCreate
):

    return await odoo_client.request(
        "POST",
        "/api/employees",
        employee.model_dump()
    )


# ==========================================
# UPDATE
# ==========================================
@app.put("/employees/{employee_id}")
async def update_employee(
    employee_id: int,
    employee: EmployeeUpdate
):

    return await odoo_client.request(
        "PUT",
        f"/api/employees/{employee_id}",
        employee.model_dump(
            exclude_none=True
        )
    )


# ==========================================
# DELETE
# ==========================================
@app.delete("/employees/{employee_id}")
async def delete_employee(
    employee_id: int
):

    return await odoo_client.request(
        "DELETE",
        f"/api/employees/{employee_id}"
    )
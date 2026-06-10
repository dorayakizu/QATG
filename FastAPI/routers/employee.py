from fastapi import APIRouter

from schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate
)

from services.odoo_client import (odoo_client)

router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)


# ==========================================
# GET ALL
# ==========================================
@router.get("")
async def get_employees(
    name: str | None = None,
    email: str | None = None,
    job_title: str | None = None,
    department_id: str | None = None,
    job_id: str | None = None,
    parent_id: str | None = None,
    coach_id: str | None = None,
    company_id: str | None = None,
    user_id: str | None = None,

    limit: int = 20,
    offset: int = 0,
    sort_by: str = "id",
    sort_order: str = "asc"

):

    params = {
        "limit": limit,
        "offset": offset,
        "sort_by": sort_by,
        "sort_order": sort_order

    }

    if name:
        params["name"] = name

    if email:
        params["email"] = email

    if job_title:
        params["job_title"] = job_title

    if department_id:
        params["department_id"] = department_id
    if job_id:
        params["job_id"] = job_id
    if parent_id:
        params["parent_id"] = parent_id
    if coach_id:
        params["coach_id"] = coach_id
    if company_id:
        params["company_id"] = company_id
    if user_id:
        params["user_id"] = user_id


    return await odoo_client.request(
        "GET",
        "/api/employees",
        params=params
    )



# ==========================================
# GET ONE
# ==========================================
@router.get("/{employee_id}")
async def get_employee(employee_id: int):
    return await odoo_client.request(
        "GET",
        f"/api/employees/{employee_id}"
    )

# ==========================================
# CREATE
# ==========================================
@router.post("")
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
@router.put("/{employee_id}")
async def update_employee(
    employee_id: int,
    employee: EmployeeUpdate
):
    return await odoo_client.request(
        "PUT",
        f"/api/employees/{employee_id}",
        employee.model_dump(exclude_none=True)
    )

# ==========================================
# DELETE
# ==========================================
@router.delete("/{employee_id}")
async def delete_employee(employee_id: int):
    return await odoo_client.request(
        "DELETE",
        f"/api/employees/{employee_id}"
    )
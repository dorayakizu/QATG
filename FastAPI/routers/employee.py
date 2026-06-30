from fastapi import APIRouter, Depends
from schemas.employee import (EmployeeCreate,EmployeeUpdate)
from services.odoo_client import (odoo_client)
from core.dependencies import get_current_user_login

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
    department_id: int | None = None,
    job_id: int | None = None,
    parent_id: int | None = None,
    coach_id: int | None = None,
    company_id: int | None = None,
    user_id: int | None = None,
    fields: str | None = None,

    limit: int = 20,
    offset: int = 0,
    sort_by: str = "id",
    sort_order: str = "asc",

    current_user: str = Depends(get_current_user_login)

):

    params = {
        "limit": limit,
        "offset": offset,
        "sort_by": sort_by,
        "sort_order": sort_order

    }

    if fields:
        params["fields"] = fields

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
        params=params,
        user_login=current_user
    )



# ==========================================
# GET ONE
# ==========================================
@router.get("/{employee_id}")
async def get_employee(
    employee_id: int,
    current_user: str = Depends(get_current_user_login) # BỔ SUNG DEPENDS
):
    return await odoo_client.request(
        "GET",
        f"/api/employees/{employee_id}",
        user_login=current_user # TRUYỀN XUỐNG ODOO
    )

# ==========================================
# CREATE
# ==========================================
@router.post("")
async def create_employee(
    employee: EmployeeCreate,
    current_user: str = Depends(get_current_user_login) # BỔ SUNG DEPENDS
):
    return await odoo_client.request(
        "POST",
        "/api/employees",
        json_data=employee.model_dump(), # Đổi từ biến thứ 3 thành tham số json_data cho chuẩn xác
        user_login=current_user # TRUYỀN XUỐNG ODOO
    )

# ==========================================
# UPDATE
# ==========================================
@router.put("/{employee_id}")
async def update_employee(
    employee_id: int,
    employee: EmployeeUpdate,
    current_user: str = Depends(get_current_user_login) # BỔ SUNG DEPENDS
):
    return await odoo_client.request(
        "PUT",
        f"/api/employees/{employee_id}",
        json_data=employee.model_dump(exclude_none=True), # Đổi thành json_data
        user_login=current_user # TRUYỀN XUỐNG ODOO
    )

# ==========================================
# DELETE
# ==========================================
@router.delete("/{employee_id}")
async def delete_employee(
    employee_id: int,
    current_user: str = Depends(get_current_user_login) # BỔ SUNG DEPENDS
):
    return await odoo_client.request(
        "DELETE",
        f"/api/employees/{employee_id}",
        user_login=current_user # TRUYỀN XUỐNG ODOO
    )
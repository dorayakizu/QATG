from fastapi import APIRouter
# Giả định các schema này đã được tạo thành công
from schemas.department import (
    DepartmentCreate, 
    DepartmentUpdate # Dùng chung model cho update và create nếu logic backend cho phép
)

from services.odoo_client import odoo_client

router = APIRouter(
    prefix="/departments",
    tags=["Departments"]
)


# ==========================================
# GET ALL (Lấy danh sách phòng ban)
# ==========================================
@router.get("")
async def get_all_departments(
    name: str | None = None,
    manager_id: int | None = None,
    parent_id: int | None = None,
    limit: int = 20,
    offset: int = 0
):
    params = {
        "limit": limit,
        "offset": offset
    }

    if name:
        params["name"] = name
    if manager_id:
        params["manager_id"] = manager_id
    if parent_id:
        params["parent_id"] = parent_id

    return await odoo_client.request(
        "GET",
        "/api/departments",
        params=params
    )


# ==========================================
# GET ONE (Lấy chi tiết phòng ban)
# ==========================================
@router.get("/{department_id}")
async def get_department(department_id: int):
    return await odoo_client.request(
        "GET",
        f"/api/departments/{department_id}"
    )

# ==========================================
# CREATE (Tạo phòng ban mới)
# ==========================================
@router.post("")
async def create_department(
    department: DepartmentCreate
):
    return await odoo_client.request(
        "POST",
        "/api/departments",
        department.model_dump()
    )

# ==========================================
# UPDATE (Cập nhật phòng ban)
# ==========================================
@router.put("/{department_id}")
async def update_department(
    department_id: int,
    department: DepartmentUpdate
):
    return await odoo_client.request(
        "PUT",
        f"/api/departments/{department_id}",
        department.model_dump(exclude_none=True)
    )

# ==========================================
# DELETE (Xóa phòng ban)
# ==========================================
@router.delete("/{department_id}")
async def delete_department(department_id: int):
    return await odoo_client.request(
        "DELETE",
        f"/api/departments/{department_id}"
    )
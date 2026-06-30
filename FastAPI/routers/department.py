from fastapi import APIRouter, Depends
# Giả định các schema này đã được tạo thành công
from schemas.department import (
    DepartmentCreate,
    DepartmentUpdate  # Dùng chung model cho update và create nếu logic backend cho phép
)

from services.odoo_client import odoo_client
from core.dependencies import get_current_user_login

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
        fields: str | None = None,  # BỔ SUNG: Tham số chọn trường dữ liệu

        limit: int = 20,
        offset: int = 0,

        current_user: str = Depends(get_current_user_login)  # BỔ SUNG: Trích xuất user đăng nhập
):
    params = {
        "limit": limit,
        "offset": offset
    }

    if fields:
        params["fields"] = fields
    if name:
        params["name"] = name
    if manager_id:
        params["manager_id"] = manager_id
    if parent_id:
        params["parent_id"] = parent_id

    return await odoo_client.request(
        "GET",
        "/api/departments",
        params=params,
        user_login=current_user  # TRUYỀN XUỐNG ODOO
    )


# ==========================================
# GET ONE (Lấy chi tiết phòng ban)
# ==========================================
@router.get("/{department_id}")
async def get_department(
        department_id: int,
        current_user: str = Depends(get_current_user_login)  # BỔ SUNG DEPENDS
):
    return await odoo_client.request(
        "GET",
        f"/api/departments/{department_id}",
        user_login=current_user  # TRUYỀN XUỐNG ODOO
    )


# ==========================================
# CREATE (Tạo phòng ban mới)
# ==========================================
@router.post("")
async def create_department(
        department: DepartmentCreate,
        current_user: str = Depends(get_current_user_login)  # BỔ SUNG DEPENDS
):
    return await odoo_client.request(
        "POST",
        "/api/departments",
        json_data=department.model_dump(),  # CHUẨN HÓA KEYWORD ARGUMENT
        user_login=current_user  # TRUYỀN XUỐNG ODOO
    )


# ==========================================
# UPDATE (Cập nhật phòng ban)
# ==========================================
@router.put("/{department_id}")
async def update_department(
        department_id: int,
        department: DepartmentUpdate,
        current_user: str = Depends(get_current_user_login)  # BỔ SUNG DEPENDS
):
    return await odoo_client.request(
        "PUT",
        f"/api/departments/{department_id}",
        json_data=department.model_dump(exclude_none=True),  # CHUẨN HÓA KEYWORD ARGUMENT
        user_login=current_user  # TRUYỀN XUỐNG ODOO
    )


# ==========================================
# DELETE (Xóa phòng ban)
# ==========================================
@router.delete("/{department_id}")
async def delete_department(
        department_id: int,
        current_user: str = Depends(get_current_user_login)  # BỔ SUNG DEPENDS
):
    return await odoo_client.request(
        "DELETE",
        f"/api/departments/{department_id}",
        user_login=current_user  # TRUYỀN XUỐNG ODOO
    )
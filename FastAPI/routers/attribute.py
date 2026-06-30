from fastapi import APIRouter, Depends
# Nhúng file schema vừa tạo ở trên
from schemas.attribute import (
    AttributeCreate,
    AttributeUpdate
)

from services.odoo_client import odoo_client
from core.dependencies import get_current_user_login

router = APIRouter(
    prefix="/attributes",
    tags=["Attributes"]
)


# ==========================================
# GET ALL (Lấy danh sách thuộc tính)
# ==========================================
@router.get("")
async def get_all_attributes(
        name: str | None = None,
        create_variant: str | None = None,
        fields: str | None = None,  # Hỗ trợ serialize động

        limit: int = 20,
        offset: int = 0,
        sort_by: str = "id",
        sort_order: str = "asc",

        current_user: str = Depends(get_current_user_login)  # Trạm kiểm duyệt JWT Token
):
    params = {
        "limit": limit,
        "offset": offset,
        "sort_by": sort_by,
        "sort_order": sort_order
    }

    if fields: params["fields"] = fields
    if name: params["name"] = name
    if create_variant: params["create_variant"] = create_variant

    return await odoo_client.request(
        "GET",
        "/api/attributes",
        params=params,
        user_login=current_user
    )


# ==========================================
# GET ONE (Lấy chi tiết một thuộc tính)
# ==========================================
@router.get("/{attribute_id}")
async def get_attribute(
        attribute_id: int,
        current_user: str = Depends(get_current_user_login)
):
    return await odoo_client.request(
        "GET",
        f"/api/attributes/{attribute_id}",
        user_login=current_user
    )


# ==========================================
# CREATE (Tạo thuộc tính mới)
# ==========================================
@router.post("")
async def create_attribute(
        attribute: AttributeCreate,
        current_user: str = Depends(get_current_user_login)
):
    return await odoo_client.request(
        "POST",
        "/api/attributes",
        # Sử dụng mode="json" và exclude_none=True để chuẩn hóa dữ liệu
        json_data=attribute.model_dump(mode="json", exclude_none=True),
        user_login=current_user
    )


# ==========================================
# UPDATE (Cập nhật thuộc tính)
# ==========================================
@router.put("/{attribute_id}")
async def update_attribute(
        attribute_id: int,
        attribute: AttributeUpdate,
        current_user: str = Depends(get_current_user_login)
):
    return await odoo_client.request(
        "PUT",
        f"/api/attributes/{attribute_id}",
        # exclude_none=True giúp thực hiện Partial Update hoàn hảo
        json_data=attribute.model_dump(mode="json", exclude_none=True),
        user_login=current_user
    )


# ==========================================
# DELETE (Xóa thuộc tính)
# ==========================================
@router.delete("/{attribute_id}")
async def delete_attribute(
        attribute_id: int,
        current_user: str = Depends(get_current_user_login)
):
    return await odoo_client.request(
        "DELETE",
        f"/api/attributes/{attribute_id}",
        user_login=current_user
    )

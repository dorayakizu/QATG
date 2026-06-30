from fastapi import APIRouter, Depends

# Nhúng file schema vừa tạo ở trên
from schemas.bom import (
    BomCreate,
    BomUpdate
)

from services.odoo_client import odoo_client
from core.dependencies import get_current_user_login

router = APIRouter(
    prefix="/boms",
    tags=["Bill of Materials"]
)


# ==========================================
# GET ALL (Lấy danh sách Định mức sản xuất)
# ==========================================
@router.get("")
async def get_all_boms(
        product_tmpl_id: int | None = None,
        product_id: int | None = None,
        type: str | None = None,
        fields: str | None = None,  # Hỗ trợ serialize động

        limit: int = 20,
        offset: int = 0,
        sort_by: str = "id",
        sort_order: str = "desc",

        current_user: str = Depends(get_current_user_login)  # Trạm kiểm duyệt JWT Token
):
    params = {
        "limit": limit,
        "offset": offset,
        "sort_by": sort_by,
        "sort_order": sort_order
    }

    if fields: params["fields"] = fields
    if product_tmpl_id: params["product_tmpl_id"] = product_tmpl_id
    if product_id: params["product_id"] = product_id
    if type: params["type"] = type

    return await odoo_client.request(
        "GET",
        "/api/boms",
        params=params,
        user_login=current_user
    )


# ==========================================
# GET ONE (Lấy chi tiết một Định mức)
# ==========================================
@router.get("/{bom_id}")
async def get_bom(
        bom_id: int,
        current_user: str = Depends(get_current_user_login)
):
    return await odoo_client.request(
        "GET",
        f"/api/boms/{bom_id}",
        user_login=current_user
    )


# ==========================================
# CREATE (Tạo Định mức mới kèm nguyên vật liệu)
# ==========================================
@router.post("")
async def create_bom(
        bom: BomCreate,
        current_user: str = Depends(get_current_user_login)
):
    return await odoo_client.request(
        "POST",
        "/api/boms",
        # Sử dụng mode="json" và exclude_none=True để chuẩn hóa dữ liệu
        json_data=bom.model_dump(mode="json", exclude_none=True),
        user_login=current_user
    )


# ==========================================
# UPDATE (Cập nhật Định mức và thành phần)
# ==========================================
@router.put("/{bom_id}")
async def update_bom(
        bom_id: int,
        bom: BomUpdate,
        current_user: str = Depends(get_current_user_login)
):
    return await odoo_client.request(
        "PUT",
        f"/api/boms/{bom_id}",
        # exclude_none=True giúp thực hiện Partial Update hoàn hảo
        json_data=bom.model_dump(mode="json", exclude_none=True),
        user_login=current_user
    )


# ==========================================
# DELETE (Xóa Định mức)
# ==========================================
@router.delete("/{bom_id}")
async def delete_bom(
        bom_id: int,
        current_user: str = Depends(get_current_user_login)
):
    return await odoo_client.request(
        "DELETE",
        f"/api/boms/{bom_id}",
        user_login=current_user
    )


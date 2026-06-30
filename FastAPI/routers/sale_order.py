from fastapi import APIRouter, Depends
# Giả định bạn đã tạo các model Pydantic này trong schemas/sale_order.py
from schemas.sale_order import (
    SaleOrderCreate,
    SaleOrderUpdate
)

from services.odoo_client import odoo_client
from core.dependencies import get_current_user_login

router = APIRouter(
    prefix="/sale_orders",
    tags=["Sale Orders"]
)


# ==========================================
# GET ALL (Lấy danh sách đơn hàng)
# ==========================================
@router.get("")
async def get_all_sale_orders(
        name: str | None = None,
        partner_id: int | None = None,
        state: str | None = None,
        fields: str | None = None,  # Hỗ trợ serialize động [cite: 394]

        limit: int = 20,
        offset: int = 0,
        sort_by: str = "id",
        sort_order: str = "desc",  # Thường đơn hàng mới nhất sẽ xếp trên cùng

        current_user: str = Depends(get_current_user_login)  # Trạm kiểm duyệt JWT Token [cite: 410]
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
    if partner_id:
        params["partner_id"] = partner_id
    if state:
        params["state"] = state

    return await odoo_client.request(
        "GET",
        "/api/sale_orders",
        params=params,
        user_login=current_user  # Truyền ngầm tài khoản xuống Odoo [cite: 416]
    )


# ==========================================
# GET ONE (Lấy chi tiết một đơn hàng)
# ==========================================
@router.get("/{order_id}")
async def get_sale_order(
        order_id: int,
        current_user: str = Depends(get_current_user_login)
):
    return await odoo_client.request(
        "GET",
        f"/api/sale_orders/{order_id}",
        user_login=current_user
    )


# ==========================================
# CREATE (Tạo đơn hàng mới)
# ==========================================
@router.post("")
async def create_sale_order(
        order: SaleOrderCreate,
        current_user: str = Depends(get_current_user_login)
):
    return await odoo_client.request(
        "POST",
        "/api/sale_orders",
        # BỔ SUNG THÊM exclude_none=True VÀO ĐÂY
        json_data=order.model_dump(mode="json", exclude_none=True),
        user_login=current_user
    )


# ==========================================
# UPDATE (Cập nhật đơn hàng)
# ==========================================
@router.put("/{order_id}")
async def update_sale_order(
        order_id: int,
        order: SaleOrderUpdate,
        current_user: str = Depends(get_current_user_login)
):
    return await odoo_client.request(
        "PUT",
        f"/api/sale_orders/{order_id}",
        # BỔ SUNG mode="json" TẠI ĐÂY [cite: 391, 392]
        json_data=order.model_dump(mode="json", exclude_none=True),
        user_login=current_user
    )


# ==========================================
# DELETE (Xóa đơn hàng)
# ==========================================
@router.delete("/{order_id}")
async def delete_sale_order(
        order_id: int,
        current_user: str = Depends(get_current_user_login)
):
    return await odoo_client.request(
        "DELETE",
        f"/api/sale_orders/{order_id}",
        user_login=current_user
    )
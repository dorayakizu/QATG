from fastapi import APIRouter, Depends

# Nhúng file schema vừa tạo ở trên
from schemas.product import (
    ProductCreate,
    ProductUpdate
)

from services.odoo_client import odoo_client
from core.dependencies import get_current_user_login

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# ==========================================
# GET ALL (Lấy danh sách sản phẩm)
# ==========================================
@router.get("")
async def get_all_products(
        name: str | None = None,
        default_code: str | None = None,
        type: str | None = None,
        categ_id: int | None = None,
        sale_ok: bool | None = None,
        purchase_ok: bool | None = None,
        is_storable: bool | None = None,

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

    # Lọc và đưa các tham số có giá trị vào params
    if fields: params["fields"] = fields
    if name: params["name"] = name
    if default_code: params["default_code"] = default_code
    if type: params["type"] = type
    if categ_id is not None: params["categ_id"] = categ_id
    if sale_ok is not None: params["sale_ok"] = sale_ok
    if purchase_ok is not None: params["purchase_ok"] = purchase_ok
    if is_storable is not None: params["is_storable"] = is_storable

    return await odoo_client.request(
        "GET",
        "/api/products",
        params=params,
        user_login=current_user  # Truyền ngầm tài khoản xuống Odoo
    )


# ==========================================
# GET ONE (Lấy chi tiết một sản phẩm)
# ==========================================
@router.get("/{product_id}")
async def get_product(
        product_id: int,
        current_user: str = Depends(get_current_user_login)
):
    return await odoo_client.request(
        "GET",
        f"/api/products/{product_id}",
        user_login=current_user
    )


# ==========================================
# CREATE (Tạo sản phẩm mới)
# ==========================================
@router.post("")
async def create_product(
        product: ProductCreate,
        current_user: str = Depends(get_current_user_login)
):
    return await odoo_client.request(
        "POST",
        "/api/products",
        # exclude_none=True chống ghi đè giá trị rỗng
        json_data=product.model_dump(mode="json", exclude_none=True),
        user_login=current_user
    )


# ==========================================
# UPDATE (Cập nhật sản phẩm)
# ==========================================
@router.put("/{product_id}")
async def update_product(
        product_id: int,
        product: ProductUpdate,
        current_user: str = Depends(get_current_user_login)
):
    return await odoo_client.request(
        "PUT",
        f"/api/products/{product_id}",
        # exclude_none=True giúp thực hiện Partial Update hoàn hảo
        json_data=product.model_dump(mode="json", exclude_none=True),
        user_login=current_user
    )


# ==========================================
# DELETE (Xóa sản phẩm)
# ==========================================
@router.delete("/{product_id}")
async def delete_product(
        product_id: int,
        current_user: str = Depends(get_current_user_login)
):
    return await odoo_client.request(
        "DELETE",
        f"/api/products/{product_id}",
        user_login=current_user
    )
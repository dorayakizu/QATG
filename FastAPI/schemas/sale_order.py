from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime




# ==========================================
# SCHEMAS CHO SALE ORDER LINE (CHI TIẾT SẢN PHẨM)
# ==========================================

class SaleOrderLineCreate(BaseModel):
    """
    Schema dùng khi TẠO MỚI một dòng sản phẩm trong đơn hàng.
    Chỉ bắt buộc truyền product_id. Các trường khác nếu không truyền, Odoo sẽ tự lấy giá gốc[cite: 614, 641].
    """
    product_id: int
    product_uom_qty: Optional[float] = Field(default=1.0, description="Số lượng sản phẩm")
    price_unit: Optional[float] = Field(default=None, description="Đơn giá (Nếu để trống, Odoo tự tính)")
    tax_ids: Optional[List[int]] = Field(default=None, description="Danh sách ID các loại thuế")


class SaleOrderLineUpdate(BaseModel):
    """
    Schema dùng khi CẬP NHẬT danh sách sản phẩm.
    Hỗ trợ 3 trường hợp: Thêm mới, Sửa, và Xóa[cite: 620, 641].
    """
    id: Optional[int] = Field(default=None, description="ID của dòng sản phẩm (Bắt buộc nếu muốn sửa hoặc xóa)")
    product_id: Optional[int] = Field(default=None,
                                      description="ID sản phẩm (Dùng khi muốn thêm mới một dòng vào đơn hàng cũ)")
    product_uom_qty: Optional[float] = Field(default=None, description="Cập nhật số lượng")
    price_unit: Optional[float] = Field(default=None, description="Cập nhật đơn giá")
    tax_ids: Optional[List[int]] = Field(default=None, description="Cập nhật danh sách ID thuế")
    delete: Optional[bool] = Field(default=False, description="Truyền true nếu muốn xóa dòng sản phẩm này")


# ==========================================
# SCHEMAS CHO SALE ORDER (ĐƠN HÀNG TỔNG)
# ==========================================

class SaleOrderCreate(BaseModel):
    """
    Schema dùng khi TẠO MỚI một đơn bán hàng.
    """
    partner_id: int = Field(..., description="ID của Khách hàng (Bắt buộc) ")
    validity_date: Optional[date] = Field(default=None, description="Ngày hết hạn báo giá (YYYY-MM-DD)")
    date_order: Optional[datetime] = Field(default=None,
                                           description="Ngày đặt hàng. Nếu không truyền, Odoo lấy giờ hiện tại [cite: 628]")
    payment_term_id: Optional[int] = Field(default=None, description="ID điều khoản thanh toán")
    state: Optional[str] = Field(description="Trạng thái đơn hàng")
    # Lồng danh sách chi tiết sản phẩm vào đơn hàng
    order_line: Optional[List[SaleOrderLineCreate]] = Field(default=None,
                                                            description="Danh sách sản phẩm thêm vào đơn hàng")


class SaleOrderUpdate(BaseModel):
    """
    Schema dùng khi CẬP NHẬT một đơn bán hàng.
    Mọi trường đều là Optional để hỗ trợ Partial Update (Chỉ sửa những gì cần thiết)[cite: 633].
    """
    partner_id: Optional[int] = Field(default=None, description="Cập nhật ID Khách hàng")
    validity_date: Optional[date] = Field(default=None, description="Cập nhật ngày hết hạn báo giá (YYYY-MM-DD)")
    date_order: Optional[datetime] = Field(default=None, description="Cập nhật ngày đặt hàng")
    payment_term_id: Optional[int] = Field(default=None, description="Cập nhật ID điều khoản thanh toán")
    state: Optional[str] = Field(description="Trạng thái đơn hàng")

    # Lồng danh sách cập nhật chi tiết sản phẩm
    order_line: Optional[List[SaleOrderLineUpdate]] = Field(default=None,
                                                            description="Danh sách thao tác Thêm/Sửa/Xóa sản phẩm")
from pydantic import BaseModel, Field
from typing import List, Optional


# ==========================================
# SCHEMA CHO THUỘC TÍNH SẢN PHẨM (ATTRIBUTES)
# ==========================================
class ProductAttributeLine(BaseModel):
    """
    Schema dùng chung cho việc cấu hình biến thể (Màu sắc, Kích thước...)
    Dùng cho cả Create và Update.
    """
    attribute_id: int = Field(..., description="ID của thuộc tính (Bắt buộc)")
    value_ids: List[int] = Field(default=[], description="Danh sách ID các giá trị của thuộc tính")


# ==========================================
# SCHEMA CHO SẢN PHẨM (PRODUCT)
# ==========================================
class ProductCreate(BaseModel):
    """
    Schema dùng khi TẠO MỚI sản phẩm.
    Dựa theo Odoo API, bắt buộc phải truyền 'name' và 'categ_id'.
    """
    name: str = Field(..., description="Tên sản phẩm (Bắt buộc)")
    categ_id: int = Field(..., description="ID danh mục sản phẩm (Bắt buộc)")

    # Các trường tùy chọn (Odoo sẽ tự lấy default nếu không truyền)
    default_code: Optional[str] = Field(default=None, description="Mã nội bộ / SKU")
    type: Optional[str] = Field(default="consu", description="Loại sản phẩm (consu, service, product)")
    list_price: Optional[float] = Field(default=None, description="Giá bán")
    standard_price: Optional[float] = Field(default=None, description="Giá vốn")
    weight: Optional[float] = Field(default=None, description="Trọng lượng")
    volume: Optional[float] = Field(default=None, description="Thể tích")
    sale_ok: Optional[bool] = Field(default=None, description="Có thể bán")
    purchase_ok: Optional[bool] = Field(default=None, description="Có thể mua")
    is_storable: Optional[bool] = Field(default=None, description="Là sản phẩm lưu kho")
    responsible_id: Optional[int] = Field(default=None, description="ID người phụ trách")

    # Mảng thuộc tính lồng nhau
    attributes: Optional[List[ProductAttributeLine]] = Field(default=None, description="Danh sách thuộc tính")


class ProductUpdate(BaseModel):
    """
    Schema dùng khi CẬP NHẬT sản phẩm.
    Tất cả các trường đều là Optional để hỗ trợ Partial Update.
    """
    name: Optional[str] = Field(default=None, description="Tên sản phẩm")
    categ_id: Optional[int] = Field(default=None, description="ID danh mục sản phẩm")
    default_code: Optional[str] = Field(default=None, description="Mã nội bộ / SKU")
    type: Optional[str] = Field(default=None, description="Loại sản phẩm")
    list_price: Optional[float] = Field(default=None, description="Giá bán")
    standard_price: Optional[float] = Field(default=None, description="Giá vốn")
    weight: Optional[float] = Field(default=None, description="Trọng lượng")
    volume: Optional[float] = Field(default=None, description="Thể tích")
    sale_ok: Optional[bool] = Field(default=None, description="Có thể bán")
    purchase_ok: Optional[bool] = Field(default=None, description="Có thể mua")
    is_storable: Optional[bool] = Field(default=None, description="Là sản phẩm lưu kho")
    responsible_id: Optional[int] = Field(default=None, description="ID người phụ trách")

    # Mảng thuộc tính lồng nhau
    attributes: Optional[List[ProductAttributeLine]] = Field(default=None, description="Cập nhật danh sách thuộc tính")
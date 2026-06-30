from pydantic import BaseModel, Field
from typing import List, Optional


# ==========================================
# SCHEMA CHO THÀNH PHẦN NGUYÊN VẬT LIỆU (BOM LINES)
# ==========================================
class BomLineCreate(BaseModel):
    """
    Schema dùng khi THÊM MỚI một thành phần nguyên vật liệu vào BOM.
    """
    product_id: int = Field(..., description="ID của nguyên vật liệu/thành phần (Bắt buộc)")
    product_qty: Optional[float] = Field(default=1.0, description="Số lượng tiêu hao")


class BomLineUpdate(BaseModel):
    """
    Schema dùng khi CẬP NHẬT danh sách thành phần nguyên vật liệu.
    Hỗ trợ Thêm mới, Sửa và Xóa thông qua "Command Tuples".
    """
    id: Optional[int] = Field(default=None, description="ID của dòng BOM Line (Bắt buộc nếu muốn sửa hoặc xóa)")
    product_id: Optional[int] = Field(default=None,
                                      description="ID của nguyên vật liệu (Dùng khi thêm mới hoặc đổi nguyên liệu)")
    product_qty: Optional[float] = Field(default=None, description="Cập nhật số lượng tiêu hao")
    delete: Optional[bool] = Field(default=False, description="Truyền true nếu muốn xóa thành phần này")


# ==========================================
# SCHEMA CHO ĐỊNH MỨC SẢN XUẤT (BILL OF MATERIAL)
# ==========================================
class BomCreate(BaseModel):
    """
    Schema dùng khi TẠO MỚI một BOM.
    Bắt buộc phải có Sản phẩm mẫu (product_tmpl_id).
    """
    product_tmpl_id: int = Field(..., description="ID của Sản phẩm mẫu (Bắt buộc)")
    product_id: Optional[int] = Field(default=None,
                                      description="ID của Biến thể sản phẩm (Nếu BOM này chỉ dành cho 1 biến thể cụ thể)")
    product_qty: Optional[float] = Field(default=None, description="Số lượng sản phẩm tạo ra từ BOM này")
    type: Optional[str] = Field(default=None, description="Loại BOM: 'normal' (Sản xuất) hoặc 'phantom' (Bộ kit)")

    # Mảng thành phần lồng nhau
    bom_lines: Optional[List[BomLineCreate]] = Field(default=None, description="Danh sách nguyên vật liệu")


class BomUpdate(BaseModel):
    """
    Schema dùng khi CẬP NHẬT một BOM.
    Tất cả các trường đều là Optional để hỗ trợ Partial Update.
    """
    product_tmpl_id: Optional[int] = Field(default=None, description="Cập nhật ID của Sản phẩm mẫu")
    product_id: Optional[int] = Field(default=None, description="Cập nhật ID của Biến thể sản phẩm")
    product_qty: Optional[float] = Field(default=None, description="Cập nhật số lượng sản xuất")
    type: Optional[str] = Field(default=None, description="Cập nhật loại BOM")

    # Mảng thao tác Thêm/Sửa/Xóa thành phần
    bom_lines: Optional[List[BomLineUpdate]] = Field(default=None,
                                                     description="Danh sách thao tác Thêm/Sửa/Xóa nguyên vật liệu")


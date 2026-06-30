from pydantic import BaseModel, Field
from typing import List, Optional


# ==========================================
# SCHEMA CHO GIÁ TRỊ THUỘC TÍNH (ATTRIBUTE VALUES)
# ==========================================
class AttributeValueCreate(BaseModel):
    """
    Schema dùng khi TẠO MỚI một giá trị thuộc tính.
    Ví dụ: Tạo màu "Đỏ", kích thước "XL".
    """
    name: str = Field(..., description="Tên giá trị (Ví dụ: Đỏ, XL) - Bắt buộc")
    color: Optional[str] = Field(default=None, description="Mã màu HEX (Ví dụ: #FF0000)")


class AttributeValueUpdate(BaseModel):
    """
    Schema dùng khi CẬP NHẬT danh sách giá trị thuộc tính.
    Hỗ trợ cả Thêm mới, Sửa và Xóa trong cùng một mảng.
    """
    id: Optional[int] = Field(default=None, description="ID của giá trị (Bắt buộc nếu muốn sửa hoặc xóa)")
    name: Optional[str] = Field(default=None, description="Tên giá trị (Dùng khi thêm mới hoặc sửa)")
    color: Optional[str] = Field(default=None, description="Mã màu HEX")
    delete: Optional[bool] = Field(default=False, description="Truyền true nếu muốn xóa giá trị này")


# ==========================================
# SCHEMA CHO THUỘC TÍNH (ATTRIBUTE)
# ==========================================
class AttributeCreate(BaseModel):
    """
    Schema dùng khi TẠO MỚI một thuộc tính (Kèm theo danh sách giá trị nếu có).
    """
    name: str = Field(..., description="Tên thuộc tính (Ví dụ: Màu sắc, Kích thước) - Bắt buộc")
    create_variant: Optional[str] = Field(default="always",
                                          description="Cơ chế tạo biến thể: always, dynamic, no_variant")
    display_type: Optional[str] = Field(default="radio", description="Kiểu hiển thị: radio, select, color")

    # Mảng các giá trị lồng nhau
    values: Optional[List[AttributeValueCreate]] = Field(default=None,
                                                         description="Danh sách các giá trị của thuộc tính")


class AttributeUpdate(BaseModel):
    """
    Schema dùng khi CẬP NHẬT một thuộc tính.
    Sử dụng Partial Update (Chỉ sửa những gì được truyền lên).
    """
    name: Optional[str] = Field(default=None, description="Tên thuộc tính")
    create_variant: Optional[str] = Field(default=None, description="Cơ chế tạo biến thể")
    display_type: Optional[str] = Field(default=None, description="Kiểu hiển thị")

    # Mảng cập nhật các giá trị
    values: Optional[List[AttributeValueUpdate]] = Field(default=None,
                                                         description="Danh sách thao tác Thêm/Sửa/Xóa giá trị")


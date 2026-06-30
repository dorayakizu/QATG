from odoo import http
from odoo.http import request
from .base_api import BaseAPI
from odoo.exceptions import AccessError, ValidationError, MissingError, UserError


class AttributeAPIController(http.Controller, BaseAPI):

    # ==========================================
    # ATTRIBUTE HELPERS
    # ==========================================

    def _build_domain(self, kwargs):
        domain = []

        name = kwargs.get("name")
        create_variant = kwargs.get("create_variant")

        if name:
            domain.append(("name", "ilike", name))

        if create_variant:
            domain.append(("create_variant", "=", create_variant))

        return domain

    def _validate_required_fields(self, data, required_fields):
        missing_fields = [field for field in required_fields if
                          not data.get(field) or str(data.get(field)).strip() == ""]

        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"

        return True, ""

    def _validate_update_fields(self, data, required_fields):
        invalid_fields = []
        for field in required_fields:
            if field in data and (data[field] is None or str(data[field]).strip() == ""):
                invalid_fields.append(field)

        if invalid_fields:
            return False, f"Cannot set required fields to empty or null: {', '.join(invalid_fields)}"

        return True, ""

    def _get_attribute(self, attr_id):
        # Kế thừa quyền từ X-User-Login, không dùng .sudo()
        attribute = request.env["product.attribute"].browse(attr_id)
        return attribute if attribute.exists() else None

    def _serialize_attribute(self, attr):
        return {
            "id": attr.id,
            "name": attr.name,
            "create_variant": attr.create_variant,
            "display_type": attr.display_type,
            # Trả về danh sách chi tiết các giá trị (Values) của thuộc tính này
            "values": [
                {
                    "id": val.id,
                    "name": val.name,
                    "color": val.color,
                } for val in attr.value_ids
            ]
        }

    def _attribute_create_vals(self, data):
        vals = {
            "name": data.get("name"),
        }

        if "create_variant" in data:
            vals["create_variant"] = data["create_variant"]
        if "display_type" in data:
            vals["display_type"] = data["display_type"]

        # Xử lý thêm các Giá trị (Values) ngay lúc tạo mới Thuộc tính (Command Tuple 0)
        if "values" in data and isinstance(data["values"], list):
            value_commands = []
            for val in data["values"]:
                if val.get("name"):
                    val_data = {"name": val.get("name")}
                    if "color" in val:
                        val_data["color"] = val["color"]

                    value_commands.append((0, 0, val_data))

            if value_commands:
                vals["value_ids"] = value_commands

        return vals

    def _attribute_update_vals(self, attr, data):
        vals = {}

        if "name" in data:
            vals["name"] = data["name"]
        if "create_variant" in data:
            vals["create_variant"] = data["create_variant"]
        if "display_type" in data:
            vals["display_type"] = data["display_type"]

        # Xử lý linh hoạt việc Thêm/Sửa/Xóa các Giá trị bên trong Thuộc tính
        if "values" in data and isinstance(data["values"], list):
            value_commands = []
            for val in data["values"]:
                # TRƯỜNG HỢP 1: Client muốn XÓA một giá trị (Truyền "id" và "delete": true)
                if val.get("id") and val.get("delete"):
                    value_commands.append((2, val.get("id"), 0))

                # TRƯỜNG HỢP 2: Client muốn SỬA tên/màu của một giá trị hiện có (Truyền "id" và "name")
                elif val.get("id"):
                    update_vals = {}
                    if "name" in val: update_vals["name"] = val["name"]
                    if "color" in val: update_vals["color"] = val["color"]

                    if update_vals:
                        value_commands.append((1, val.get("id"), update_vals))

                # TRƯỜNG HỢP 3: Client muốn THÊM một giá trị mới vào Thuộc tính hiện hành
                elif val.get("name"):
                    create_vals = {"name": val.get("name")}
                    if "color" in val: create_vals["color"] = val["color"]

                    value_commands.append((0, 0, create_vals))

            if value_commands:
                vals["value_ids"] = value_commands

        return vals

    # ==========================================
    # GET ALL
    # ==========================================
    @http.route("/api/attributes", auth="public", type="http", methods=["GET"], csrf=False)
    def get_attributes(self, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        domain = self._build_domain(kwargs)
        limit, offset = self._get_pagination(kwargs)
        sorting = self._get_sorting(kwargs, ["id", "name"])

        allowed_fields = [
            "id", "name", "create_variant", "display_type", "value_ids"
        ]

        fields_to_read = self._get_requested_fields(kwargs, allowed_fields)
        Attribute = request.env["product.attribute"]

        try:
            total_count = Attribute.search_count(domain)
            attributes = Attribute.search(
                domain, limit=limit, offset=offset, order=sorting["order"]
            )

            data = attributes.read(fields_to_read)

            return request.make_json_response({
                "success": True,
                "total": total_count,
                "count": len(data),
                "limit": limit,
                "offset": offset,
                "sort_by": sorting["sort_by"],
                "sort_order": sorting["sort_order"],
                "data": data
            })

        except AccessError:
            return self._forbidden("Access Denied: You do not have permission to view attributes.")
        except Exception as e:
            return self._server_error(e)

    # ==========================================
    # GET ONE
    # ==========================================
    @http.route("/api/attributes/<int:attribute_id>", auth="public", type="http", methods=["GET"], csrf=False)
    def get_attribute(self, attribute_id, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        try:
            attribute = self._get_attribute(attribute_id)

            if not attribute:
                return self._not_found("Attribute")

            return request.make_json_response({
                "success": True,
                "data": self._serialize_attribute(attribute)
            })

        except AccessError:
            return self._forbidden("Access Denied: You do not have permission to view this attribute.")
        except Exception as e:
            return self._server_error(e)

    # ==========================================
    # CREATE
    # ==========================================
    @http.route("/api/attributes", auth="public", type="http", methods=["POST"], csrf=False)
    def create_attribute(self, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        try:
            data = self._get_request_data()
            is_valid, error_msg = self._validate_required_fields(data, ["name"])

            if not is_valid:
                return self._bad_request(error_msg)

            attribute = request.env["product.attribute"].create(self._attribute_create_vals(data))

            return request.make_json_response({
                "success": True,
                "id": attribute.id
            })

        except AccessError:
            return self._forbidden("Access Denied: You do not have permission to create an attribute.")
        except ValidationError as e:
            return self._bad_request(str(e))
        except Exception as e:
            return self._server_error(e)

    # ==========================================
    # UPDATE
    # ==========================================
    @http.route("/api/attributes/<int:attribute_id>", auth="public", type="http", methods=["PUT"], csrf=False)
    def update_attribute(self, attribute_id, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        try:
            attribute = self._get_attribute(attribute_id)

            if not attribute:
                return self._not_found("Attribute")

            data = self._get_request_data()
            is_valid, error_msg = self._validate_update_fields(data, ["name"])

            if not is_valid:
                return self._bad_request(error_msg)

            attribute.write(self._attribute_update_vals(attribute, data))

            return request.make_json_response({
                "success": True,
                "message": "Attribute updated"
            })

        except AccessError:
            return self._forbidden("Access Denied: You do not have permission to update this attribute.")
        except ValidationError as e:
            return self._bad_request(str(e))
        except Exception as e:
            return self._server_error(e)

    # ==========================================
    # DELETE
    # ==========================================
    @http.route("/api/attributes/<int:attribute_id>", auth="public", type="http", methods=["DELETE"], csrf=False)
    def delete_attribute(self, attribute_id, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        try:
            attribute = self._get_attribute(attribute_id)

            if not attribute:
                return self._not_found("Attribute")

            # Thực hiện lệnh xóa
            attribute.unlink()

            return request.make_json_response({
                "success": True,
                "message": "Attribute deleted"
            })

        except AccessError:
            return self._forbidden("Access Denied: You do not have permission to delete this attribute.")

        except UserError as e:
            # Bắt gọn lỗi khi Odoo chủ động chặn xóa do dính tới sản phẩm
            return self._bad_request(str(e))

        except ValidationError as e:
            return self._bad_request(str(e))

        except Exception as e:
            # Fallback: Bắt lỗi Database (IntegrityError) phòng trường hợp Odoo không ném UserError
            return self._bad_request(
                "Cannot delete attributes linked to a product!")


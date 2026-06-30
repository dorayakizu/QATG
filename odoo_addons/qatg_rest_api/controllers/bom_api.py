from odoo import http
from odoo.http import request
from .base_api import BaseAPI
from odoo.exceptions import AccessError, ValidationError, UserError, MissingError


class BomAPIController(http.Controller, BaseAPI):

    # ==========================================
    # BOM HELPERS
    # ==========================================

    def _build_domain(self, kwargs):
        domain = []

        product_tmpl_id = kwargs.get("product_tmpl_id")
        product_id = kwargs.get("product_id")
        bom_type = kwargs.get("type")

        if product_tmpl_id:
            domain.append(("product_tmpl_id", "=", int(product_tmpl_id)))

        if product_id:
            domain.append(("product_id", "=", int(product_id)))

        if bom_type:
            domain.append(("type", "=", bom_type))

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

    def _get_bom(self, bom_id):
        # Kế thừa quyền từ X-User-Login, tuyệt đối không dùng .sudo()
        bom = request.env["mrp.bom"].browse(bom_id)
        return bom if bom.exists() else None

    def _serialize_bom(self, bom):
        return {
            "id": bom.id,
            "product_tmpl": {
                "id": bom.product_tmpl_id.id,
                "name": bom.product_tmpl_id.name,
            } if bom.product_tmpl_id else None,
            "product": {
                "id": bom.product_id.id,
                "name": bom.product_id.name,
            } if bom.product_id else None,
            "product_qty": bom.product_qty,
            "product_uom_id": bom.product_uom_id.id if bom.product_uom_id else None,
            "type": bom.type,
            # Trả về danh sách chi tiết các thành phần (Components)
            "bom_lines": [
                {
                    "id": line.id,
                    "product_id": line.product_id.id,
                    "product_name": line.product_id.name,
                    "product_qty": line.product_qty,
                    "product_uom_id": line.product_uom_id.id if line.product_uom_id else None,
                } for line in bom.bom_line_ids
            ]
        }

    def _bom_create_vals(self, data):
        vals = {
            "product_tmpl_id": data.get("product_tmpl_id"),
        }

        # Các trường tùy chọn (Optional)
        if "product_id" in data:
            vals["product_id"] = data["product_id"]
        if "product_qty" in data:
            vals["product_qty"] = data["product_qty"]
        if "type" in data:
            vals["type"] = data["type"]

        # Xử lý thêm các Thành phần (Components) ngay lúc tạo mới BOM
        if "bom_lines" in data and isinstance(data["bom_lines"], list):
            line_commands = []
            for line in data["bom_lines"]:
                if line.get("product_id"):
                    line_vals = {
                        "product_id": line.get("product_id"),
                        "product_qty": line.get("product_qty", 1.0)
                    }
                    line_commands.append((0, 0, line_vals))

            if line_commands:
                vals["bom_line_ids"] = line_commands

        return vals

    def _bom_update_vals(self, bom, data):
        vals = {}

        if "product_tmpl_id" in data:
            vals["product_tmpl_id"] = data["product_tmpl_id"]
        if "product_id" in data:
            vals["product_id"] = data["product_id"]
        if "product_qty" in data:
            vals["product_qty"] = data["product_qty"]
        if "type" in data:
            vals["type"] = data["type"]

        # Xử lý linh hoạt việc Thêm/Sửa/Xóa các Component bên trong BOM
        if "bom_lines" in data and isinstance(data["bom_lines"], list):
            line_commands = []
            for line in data["bom_lines"]:
                # TRƯỜNG HỢP 1: Client muốn XÓA một thành phần (Truyền "id" và "delete": true)
                if line.get("id") and line.get("delete"):
                    line_commands.append((2, line.get("id"), 0))

                # TRƯỜNG HỢP 2: Client muốn SỬA số lượng của thành phần hiện có (Truyền "id" và "product_qty")
                elif line.get("id"):
                    update_vals = {}
                    if "product_qty" in line: update_vals["product_qty"] = line["product_qty"]
                    if "product_id" in line: update_vals["product_id"] = line["product_id"]

                    if update_vals:
                        line_commands.append((1, line.get("id"), update_vals))

                # TRƯỜNG HỢP 3: Client muốn THÊM một thành phần mới vào BOM hiện hành
                elif line.get("product_id"):
                    create_vals = {
                        "product_id": line.get("product_id"),
                        "product_qty": line.get("product_qty", 1.0)
                    }
                    line_commands.append((0, 0, create_vals))

            if line_commands:
                vals["bom_line_ids"] = line_commands

        return vals

    # ==========================================
    # GET ALL
    # ==========================================
    @http.route("/api/boms", auth="public", type="http", methods=["GET"], csrf=False)
    def get_boms(self, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        domain = self._build_domain(kwargs)
        limit, offset = self._get_pagination(kwargs)
        sorting = self._get_sorting(kwargs, ["id", "product_tmpl_id"])

        # Khai báo các trường cho phép đọc
        allowed_fields = [
            "id", "product_tmpl_id", "product_id", "product_qty",
            "product_uom_id", "type", "bom_line_ids"
        ]

        fields_to_read = self._get_requested_fields(kwargs, allowed_fields)
        Bom = request.env["mrp.bom"]

        try:
            total_count = Bom.search_count(domain)
            boms = Bom.search(domain, limit=limit, offset=offset, order=sorting["order"])

            data = boms.read(fields_to_read)

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
            return self._forbidden("Access Denied: You do not have permission to view Bill of Materials.")
        except Exception as e:
            return self._server_error(e)

    # ==========================================
    # GET ONE
    # ==========================================
    @http.route("/api/boms/<int:bom_id>", auth="public", type="http", methods=["GET"], csrf=False)
    def get_bom(self, bom_id, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        try:
            bom = self._get_bom(bom_id)

            if not bom:
                return self._not_found("Bill of Material")

            return request.make_json_response({
                "success": True,
                "data": self._serialize_bom(bom)
            })

        except AccessError:
            return self._forbidden("Access Denied: You do not have permission to view this BOM.")
        except Exception as e:
            return self._server_error(e)

    # ==========================================
    # CREATE
    # ==========================================
    @http.route("/api/boms", auth="public", type="http", methods=["POST"], csrf=False)
    def create_bom(self, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        try:
            data = self._get_request_data()
            # BOM bắt buộc phải có sản phẩm mẫu (product_tmpl_id)
            is_valid, error_msg = self._validate_required_fields(data, ["product_tmpl_id"])

            if not is_valid:
                return self._bad_request(error_msg)

            bom = request.env["mrp.bom"].create(self._bom_create_vals(data))

            return request.make_json_response({
                "success": True,
                "id": bom.id
            })

        except AccessError:
            return self._forbidden("Access Denied: You do not have permission to create a BOM.")
        except ValidationError as e:
            return self._bad_request(str(e))
        except Exception as e:
            return self._server_error(e)

    # ==========================================
    # UPDATE
    # ==========================================
    @http.route("/api/boms/<int:bom_id>", auth="public", type="http", methods=["PUT"], csrf=False)
    def update_bom(self, bom_id, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        try:
            bom = self._get_bom(bom_id)

            if not bom:
                return self._not_found("Bill of Material")

            data = self._get_request_data()
            # Không cho phép cập nhật product_tmpl_id thành rỗng
            is_valid, error_msg = self._validate_update_fields(data, ["product_tmpl_id"])

            if not is_valid:
                return self._bad_request(error_msg)

            bom.write(self._bom_update_vals(bom, data))

            return request.make_json_response({
                "success": True,
                "message": "Bill of Material updated"
            })

        except AccessError:
            return self._forbidden("Access Denied: You do not have permission to update this BOM.")
        except ValidationError as e:
            return self._bad_request(str(e))
        except Exception as e:
            return self._server_error(e)

    # ==========================================
    # DELETE
    # ==========================================
    @http.route("/api/boms/<int:bom_id>", auth="public", type="http", methods=["DELETE"], csrf=False)
    def delete_bom(self, bom_id, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        try:
            bom = self._get_bom(bom_id)

            if not bom:
                return self._not_found("Bill of Material")

            bom.unlink()

            return request.make_json_response({
                "success": True,
                "message": "Bill of Material deleted"
            })

        except AccessError:
            return self._forbidden("Access Denied: You do not have permission to delete this BOM.")
        except UserError as e:
            # Bắt lỗi nếu Odoo chặn xóa do BOM đang được sử dụng trong Lệnh sản xuất (Manufacturing Order)
            return self._bad_request(str(e))
        except ValidationError as e:
            return self._bad_request(str(e))
        except Exception as e:
            return self._server_error("Failed to delete BOM due to dependencies or internal error.")


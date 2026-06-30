from odoo import http
from odoo.http import request
from .base_api import BaseAPI
from odoo.exceptions import AccessError, ValidationError, MissingError


class SaleOrderAPIController(http.Controller, BaseAPI):

    # ==========================================
    # SALE ORDER HELPERS
    # ==========================================

    def _build_domain(self, kwargs):
        domain = []

        name = kwargs.get("name")
        partner_id = kwargs.get("partner_id")
        state = kwargs.get("state")

        if name:
            domain.append(("name", "ilike", name))

        if partner_id:
            domain.append(("partner_id", "=", int(partner_id)))

        if state:
            domain.append(("state", "=", state))

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

    def _get_sale_order(self, order_id):
        # Kế thừa quyền từ X-User-Login, không dùng .sudo()
        order = request.env["sale.order"].browse(order_id)
        return order if order.exists() else None

    def _serialize_sale_order(self, order):
        return {
            "id": order.id,
            "name": order.name,
            "state": order.state,
            "date_order": str(order.date_order) if order.date_order else None,
            "validity_date": str(order.validity_date) if order.validity_date else None,

            # TRẢ VỀ CÁC TRƯỜNG TỔNG TIỀN DO ODOO TỰ TÍNH
            "amount_untaxed": order.amount_untaxed,
            "amount_tax": order.amount_tax,
            "amount_total": order.amount_total,

            "partner": {
                "id": order.partner_id.id,
                "name": order.partner_id.name,
            } if order.partner_id else None,

            "payment_term": {
                "id": order.payment_term_id.id,
                "name": order.payment_term_id.name,
            } if order.payment_term_id else None,

            # TRẢ VỀ DANH SÁCH CHI TIẾT SẢN PHẨM (ORDER LINES)
            "order_lines": [
                {
                    "id": line.id,
                    "product_id": line.product_id.id,
                    "product_name": line.product_id.name,
                    "quantity": line.product_uom_qty,
                    "price_unit": line.price_unit,
                    "tax_ids": line.tax_id.ids,  # Trả về mảng các ID thuế đang áp dụng
                    "price_subtotal": line.price_subtotal,
                } for line in order.order_line
            ]
        }

    def _sale_order_create_vals(self, data):
        vals = {
            "partner_id": data.get("partner_id"),
        }

        # CHỈ GÁN NẾU CÓ DỮ LIỆU ĐỂ TRÁNH LỖI GHI ĐÈ BẰNG NONE
        if "validity_date" in data:
            vals["validity_date"] = data["validity_date"]
        if "date_order" in data:
            vals["date_order"] = data["date_order"]
        if "payment_term_id" in data:
            vals["payment_term_id"] = data["payment_term_id"]
        if "state" in data:
            vals["state"] = data["state"]

        # XỬ LÝ ORDER LINES (Giữ nguyên logic cực tốt của bạn)
        if "order_line" in data and isinstance(data["order_line"], list):
            lines = []
            for line in data["order_line"]:
                if line.get("product_id"):
                    line_vals = {
                        "product_id": line.get("product_id"),
                        "product_uom_qty": line.get("product_uom_qty", 1.0),
                    }
                    if "price_unit" in line:
                        line_vals["price_unit"] = line["price_unit"]
                    if "tax_ids" in line and isinstance(line["tax_ids"], list):
                        line_vals["tax_id"] = [(6, 0, line["tax_ids"])]

                    lines.append((0, 0, line_vals))

            if lines:
                vals["order_line"] = lines

        return vals

    def _sale_order_update_vals(self, order, data):
        vals = {}

        # BƯỚC SỬA: Chỉ cập nhật những trường mà Client muốn sửa
        if "partner_id" in data:
            vals["partner_id"] = data["partner_id"]
        if "validity_date" in data:
            vals["validity_date"] = data["validity_date"]
        if "date_order" in data:
            vals["date_order"] = data["date_order"]
        if "payment_term_id" in data:
            vals["payment_term_id"] = data["payment_term_id"]
        if "state" in data:
            vals["state"] = data["state"]


        # XỬ LÝ ORDER LINES KHI UPDATE (Giữ nguyên logic cực tốt của bạn)
        if "order_line" in data and isinstance(data["order_line"], list):
            lines = []
            for line in data["order_line"]:
                if line.get("id") and line.get("delete"):
                    lines.append((2, line.get("id"), 0))
                elif line.get("id"):
                    update_vals = {}
                    if "product_uom_qty" in line: update_vals["product_uom_qty"] = line["product_uom_qty"]
                    if "price_unit" in line: update_vals["price_unit"] = line["price_unit"]
                    if "tax_ids" in line and isinstance(line["tax_ids"], list):
                        update_vals["tax_id"] = [(6, 0, line["tax_ids"])]

                    if update_vals:
                        lines.append((1, line.get("id"), update_vals))
                elif line.get("product_id"):
                    create_vals = {
                        "product_id": line.get("product_id"),
                        "product_uom_qty": line.get("product_uom_qty", 1.0),
                    }
                    if "price_unit" in line: create_vals["price_unit"] = line["price_unit"]
                    if "tax_ids" in line and isinstance(line["tax_ids"], list):
                        create_vals["tax_id"] = [(6, 0, line["tax_ids"])]

                    lines.append((0, 0, create_vals))

            if lines:
                vals["order_line"] = lines

        return vals

    # ==========================================
    # GET ALL
    # ==========================================

    @http.route("/api/sale_orders", auth="public", type="http", methods=["GET"], csrf=False)
    def get_sale_orders(self, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        domain = self._build_domain(kwargs)
        limit, offset = self._get_pagination(kwargs)
        sorting = self._get_sorting(
            kwargs,
            ["id", "name", "date_order", "amount_total"]
        )

        # KHAI BÁO WHITELIST CHO DYNAMIC SERIALIZATION
        allowed_fields = [
            "id", "name", "state", "partner_id",
            "validity_date", "date_order", "payment_term_id", "amount_untaxed", "amount_tax", "amount_total"
        ]

        fields_to_read = self._get_requested_fields(kwargs, allowed_fields)

        SaleOrder = request.env["sale.order"]

        try:
            total_count = SaleOrder.search_count(domain)
            orders = SaleOrder.search(
                domain,
                limit=limit,
                offset=offset,
                order=sorting["order"]
            )

            # Sử dụng .read() để tối ưu truy xuất
            data = orders.read(fields_to_read)

            # Chuyển đổi datetime sang dạng string nếu cần thiết khi đọc qua read()
            for record in data:
                if 'date_order' in record and record['date_order']:
                    record['date_order'] = str(record['date_order'])
                if 'validity_date' in record and record['validity_date']:
                    record['validity_date'] = str(record['validity_date'])

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
            return self._forbidden("Access Denied: You do not have permission to view sale orders.")
        except Exception as e:
            return self._server_error(e)

    # ==========================================
    # GET ONE
    # ==========================================

    @http.route("/api/sale_orders/<int:order_id>", auth="public", type="http", methods=["GET"], csrf=False)
    def get_sale_order(self, order_id, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        try:
            order = self._get_sale_order(order_id)

            if not order:
                return self._not_found("Sale Order")

            return request.make_json_response({
                "success": True,
                "data": self._serialize_sale_order(order)
            })

        except AccessError:
            return self._forbidden("Access Denied: You do not have permission to view this sale order.")
        except Exception as e:
            return self._server_error(e)

    # ==========================================
    # CREATE
    # ==========================================

    @http.route("/api/sale_orders", auth="public", type="http", methods=["POST"], csrf=False)
    def create_sale_order(self, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        try:
            data = self._get_request_data()

            # Đối với Sales Order, partner_id (Khách hàng) là bắt buộc
            is_valid, error_msg = self._validate_required_fields(data, ["partner_id"])
            if not is_valid:
                return self._bad_request(error_msg)

            order = request.env["sale.order"].create(self._sale_order_create_vals(data))

            return request.make_json_response({
                "success": True,
                "id": order.id
            })

        except AccessError:
            return self._forbidden("Access Denied: You do not have permission to create a sale order.")
        except ValidationError as e:
            return self._bad_request(str(e))
        except Exception as e:
            return self._server_error(e)

    # ==========================================
    # UPDATE
    # ==========================================

    @http.route("/api/sale_orders/<int:order_id>", auth="public", type="http", methods=["PUT"], csrf=False)
    def update_sale_order(self, order_id, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        try:
            order = self._get_sale_order(order_id)

            if not order:
                return self._not_found("Sale Order")

            data = self._get_request_data()

            # Không cho phép cập nhật khách hàng thành rỗng
            is_valid, error_msg = self._validate_update_fields(data, ["partner_id"])
            if not is_valid:
                return self._bad_request(error_msg)

            order.write(self._sale_order_update_vals(order, data))

            return request.make_json_response({
                "success": True,
                "message": "Sale Order updated"
            })

        except AccessError:
            return self._forbidden("Access Denied: You do not have permission to update this sale order.")
        except ValidationError as e:
            return self._bad_request(str(e))
        except Exception as e:
            return self._server_error(e)

    # ==========================================
    # DELETE
    # ==========================================

    @http.route("/api/sale_orders/<int:order_id>", auth="public", type="http", methods=["DELETE"], csrf=False)
    def delete_sale_order(self, order_id, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        try:
            order = self._get_sale_order(order_id)

            if not order:
                return self._not_found("Sale Order")

            order.unlink()

            return request.make_json_response({
                "success": True,
                "message": "Sale Order deleted"
            })

        except AccessError:
            return self._forbidden("Access Denied: You do not have permission to delete this sale order.")
        except ValidationError as e:
            return self._bad_request(str(e))
        except Exception as e:
            return self._server_error("Failed to delete sale order due to dependencies or internal error.")


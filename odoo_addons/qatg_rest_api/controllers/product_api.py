from odoo import http
from odoo.http import request
from .base_api import BaseAPI
from odoo.exceptions import AccessError, ValidationError, MissingError


class ProductAPIController(http.Controller, BaseAPI):

    # ==========================================
    # PRODUCT HELPERS
    # ==========================================

    def _build_domain(self, kwargs):
        domain = []

        name = kwargs.get("name")
        default_code = kwargs.get("default_code")
        product_type = kwargs.get("type")
        categ_id = kwargs.get("categ_id")

        sale_ok = kwargs.get("sale_ok")
        purchase_ok = kwargs.get("purchase_ok")
        is_storable = kwargs.get("is_storable")

        if name:
            domain.append(("name", "ilike", name))

        if default_code:
            domain.append(("default_code", "ilike", default_code))

        if product_type:
            domain.append(("type", "=", product_type))

        if categ_id:
            domain.append(("categ_id", "=", int(categ_id)))

        if sale_ok is not None:
            domain.append(("sale_ok", "=", str(sale_ok).lower() == "true"))

        if purchase_ok is not None:
            domain.append(("purchase_ok", "=", str(purchase_ok).lower() == "true"))

        if is_storable is not None:
            domain.append(("is_storable", "=", str(is_storable).lower() == "true"))

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

    def _get_product(self, product_id):
        product = request.env["product.template"].browse(product_id)
        return product if product.exists() else None

    def _serialize_product(self, product):
        return {
            "id": product.id,
            "name": product.name,
            "sale_ok": product.sale_ok,
            "purchase_ok": product.purchase_ok,
            "type": product.type,
            "is_storable": product.is_storable,
            "list_price": product.list_price,
            "standard_price": product.standard_price,
            "default_code": product.default_code,
            "weight": product.weight,
            "volume": product.volume,
            "category": {
                "id": product.categ_id.id,
                "name": product.categ_id.name,
            } if product.categ_id else None,
            "responsible": {
                "id": product.responsible_id.id,
                "name": product.responsible_id.name,
            } if product.responsible_id else None,
            # Thêm thông tin Attributes khi GET chi tiết sản phẩm
            "attributes": [
                {
                    "line_id": line.id,
                    "attribute_id": line.attribute_id.id,
                    "attribute_name": line.attribute_id.name,
                    "values": [{"id": val.id, "name": val.name} for val in line.value_ids]
                } for line in product.attribute_line_ids
            ]
        }

    def _product_create_vals(self, data):
        vals = {
            "name": data.get("name"),
            "sale_ok": data.get("sale_ok", True),
            "purchase_ok": data.get("purchase_ok", True),
            "type": data.get("type", "consu"),
            "is_storable": data.get("is_storable", False),
            "list_price": data.get("list_price", 0),
            "standard_price": data.get("standard_price", 0),
            "default_code": data.get("default_code"),
            "weight": data.get("weight", 0),
            "volume": data.get("volume", 0),
            "categ_id": data.get("categ_id"),
            "responsible_id": data.get("responsible_id"),
        }

        # Xử lý gán Attributes khi TẠO MỚI sản phẩm
        attributes = data.get("attributes")
        if isinstance(attributes, list):
            attr_commands = []
            for attr in attributes:
                attr_id = attr.get("attribute_id")
                value_ids = attr.get("value_ids", [])

                if attr_id and value_ids:
                    # Dùng magic tuple (0, 0, dict) để tạo dòng attribute_line mới
                    # Dùng (6, 0, list_ids) để gán danh sách value_ids vào quan hệ Many2many
                    attr_commands.append((0, 0, {
                        "attribute_id": attr_id,
                        "value_ids": [(6, 0, value_ids)]
                    }))
            if attr_commands:
                vals["attribute_line_ids"] = attr_commands

        return vals

    def _product_update_vals(self, product, data):
        vals = {
            "name": data.get("name", product.name),
            "sale_ok": data.get("sale_ok", product.sale_ok),
            "purchase_ok": data.get("purchase_ok", product.purchase_ok),
            "type": data.get("type", product.type),
            "is_storable": data.get("is_storable", product.is_storable),
            "list_price": data.get("list_price", product.list_price),
            "standard_price": data.get("standard_price", product.standard_price),
            "default_code": data.get("default_code", product.default_code),
            "weight": data.get("weight", product.weight),
            "volume": data.get("volume", product.volume),
            "categ_id": data.get("categ_id", product.categ_id.id if product.categ_id else False),
            "responsible_id": data.get("responsible_id",
                                       product.responsible_id.id if product.responsible_id else False),
        }

        # Xử lý gán Attributes khi CẬP NHẬT sản phẩm
        attributes = data.get("attributes")
        if isinstance(attributes, list):
            # Tạo map tra cứu các attribute hiện có của sản phẩm theo attribute_id
            existing_lines = {line.attribute_id.id: line for line in product.attribute_line_ids}
            attr_commands = []
            provided_attr_ids = []

            for attr in attributes:
                attr_id = attr.get("attribute_id")
                value_ids = attr.get("value_ids", [])

                if not attr_id:
                    continue

                provided_attr_ids.append(attr_id)

                if attr_id in existing_lines:
                    # NẾU ĐÃ TỒN TẠI: Dùng (1, id, dict) để cập nhật lại danh sách value_ids
                    line_id = existing_lines[attr_id].id
                    attr_commands.append((1, line_id, {
                        "value_ids": [(6, 0, value_ids)]
                    }))
                else:
                    # NẾU LÀ THUỘC TÍNH MỚI: Dùng (0, 0, dict) để tạo dòng mới
                    if value_ids:
                        attr_commands.append((0, 0, {
                            "attribute_id": attr_id,
                            "value_ids": [(6, 0, value_ids)]
                        }))

            # TÌM VÀ XÓA các thuộc tính cũ không còn xuất hiện trong payload gửi lên
            for attr_id, line in existing_lines.items():
                if attr_id not in provided_attr_ids:
                    # Dùng (2, id, 0) để xóa bản ghi line
                    attr_commands.append((2, line.id, 0))

            vals["attribute_line_ids"] = attr_commands

        return vals

    # ==========================================
    # GET ALL
    # ==========================================

    @http.route("/api/products", auth="public", type="http", methods=["GET"], csrf=False)
    def get_products(self, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        domain = self._build_domain(kwargs)
        limit, offset = self._get_pagination(kwargs)
        sorting = self._get_sorting(
            kwargs,
            ["id", "name", "default_code", "list_price", "weight", "volume"]
        )

        allowed_fields = [
            "id", "name", "default_code", "list_price", "standard_price",
            "type", "is_storable", "sale_ok", "purchase_ok",
            "weight", "volume", "categ_id", "responsible_id",
            "attribute_line_ids"  # Thêm field này để Odoo read ra mảng các ID
        ]

        fields_to_read = self._get_requested_fields(kwargs, allowed_fields)
        Product = request.env["product.template"]

        try:
            total_count = Product.search_count(domain)
            products = Product.search(
                domain,
                limit=limit,
                offset=offset,
                order=sorting["order"]
            )

            data = products.read(fields_to_read)

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
            return self._forbidden("Access Denied: You do not have permission to view products.")
        except Exception as e:
            return self._server_error(e)

    # ==========================================
    # GET ONE
    # ==========================================

    @http.route("/api/products/<int:product_id>", auth="public", type="http", methods=["GET"], csrf=False)
    def get_product(self, product_id, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        try:
            product = self._get_product(product_id)

            if not product:
                return self._not_found("Product")

            return request.make_json_response({
                "success": True,
                "data": self._serialize_product(product)
            })

        except AccessError:
            return self._forbidden("Access Denied: You do not have permission to view this product.")
        except Exception as e:
            return self._server_error(e)

    # ==========================================
    # CREATE
    # ==========================================

    @http.route("/api/products", auth="public", type="http", methods=["POST"], csrf=False)
    def create_product(self, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        try:
            data = self._get_request_data()
            is_valid, error_msg = self._validate_required_fields(data, ["name", "categ_id"])

            if not is_valid:
                return self._bad_request(error_msg)

            product = request.env["product.template"].create(self._product_create_vals(data))

            return request.make_json_response({
                "success": True,
                "id": product.id
            })

        except AccessError:
            return self._forbidden("Access Denied: You do not have permission to create a product.")
        except ValidationError as e:
            return self._bad_request(str(e))
        except Exception as e:
            return self._server_error(e)

    # ==========================================
    # UPDATE
    # ==========================================

    @http.route("/api/products/<int:product_id>", auth="public", type="http", methods=["PUT"], csrf=False)
    def update_product(self, product_id, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        try:
            product = self._get_product(product_id)

            if not product:
                return self._not_found("Product")

            data = self._get_request_data()
            is_valid, error_msg = self._validate_update_fields(data, ["name"])

            if not is_valid:
                return self._bad_request(error_msg)

            product.write(self._product_update_vals(product, data))

            return request.make_json_response({
                "success": True,
                "message": "Product updated"
            })

        except AccessError:
            return self._forbidden("Access Denied: You do not have permission to update this product.")
        except ValidationError as e:
            return self._bad_request(str(e))
        except Exception as e:
            return self._server_error(e)

    # ==========================================
    # DELETE
    # ==========================================

    @http.route("/api/products/<int:product_id>", auth="public", type="http", methods=["DELETE"], csrf=False)
    def delete_product(self, product_id, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        try:
            product = self._get_product(product_id)

            if not product:
                return self._not_found("Product")

            product.unlink()

            return request.make_json_response({
                "success": True,
                "message": "Product deleted"
            })

        except AccessError:
            return self._forbidden("Access Denied: You do not have permission to delete this product.")
        except ValidationError as e:
            return self._bad_request(str(e))
        except Exception as e:
            return self._server_error("Failed to delete product due to dependencies or internal error.")
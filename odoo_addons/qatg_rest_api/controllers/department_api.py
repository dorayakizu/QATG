from odoo import http
from odoo.http import request
from .base_api import BaseAPI
from odoo.exceptions import AccessError, ValidationError, MissingError

class DepartmentAPIController(http.Controller, BaseAPI):

    # ==========================================
    # DEPARTMENT HELPERS
    # ==========================================
    def _build_domain(self, kwargs):
        domain = []

        name = kwargs.get("name")
        parent_id = kwargs.get("parent_id")
        manager_id = kwargs.get("manager_id")
        company_id = kwargs.get("company_id")

        if parent_id:
            domain.append(("parent_id", "=", int(parent_id)))

        if manager_id:
            domain.append(("manager_id", "=", int(manager_id)))

        if company_id:
            domain.append(("company_id", "=", int(company_id)))

        if name:
            domain.append(("name", "ilike", name))

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

    def _get_department(self, department_id):
        # ĐÃ XÓA .sudo()
        department = request.env["hr.department"].browse(department_id)
        return department if department.exists() else None

    def _serialize_department(self, department):
        return {
            "id": department.id,
            "name": department.name,
            "parent": {
                "id": department.parent_id.id,
                "name": department.parent_id.name,
            } if department.parent_id else None,
            "manager": {
                "id": department.manager_id.id,
                "name": department.manager_id.name,
            } if department.manager_id else None,
            "company": {
                "id": department.company_id.id,
                "name": department.company_id.name,
            } if department.company_id else None,
        }

    def _department_create_vals(self, data):
        return {
            "name": data.get("name"),
            "parent_id": data.get("parent_id"),
            "manager_id": data.get("manager_id"),
            "company_id": data.get("company_id"),
        }

    def _department_update_vals(self, department, data):
        return {
            "name": data.get("name", department.name),
            "parent_id": data.get(
                "parent_id",
                department.parent_id.id if department.parent_id else False
            ),
            "manager_id": data.get(
                "manager_id",
                department.manager_id.id if department.manager_id else False
            ),
            "company_id": data.get(
                "company_id",
                department.company_id.id if department.company_id else False
            ),
        }

    # ==========================================
    # GET ALL (List Departments)
    # ==========================================
    @http.route("/api/departments", auth="public", type="http", methods=["GET"], csrf=False)
    def get_departments(self, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        domain = self._build_domain(kwargs)
        limit, offset = self._get_pagination(kwargs)
        sorting = self._get_sorting(kwargs, ["id", "name"])

        # KHAI BÁO WHITELIST
        allowed_fields = [
            "id", "name", "parent_id", "manager_id", "company_id"
        ]

        # Lấy danh sách fields mà client muốn
        fields_to_read = self._get_requested_fields(kwargs, allowed_fields)

        # ĐÃ XÓA .sudo()
        Department = request.env["hr.department"]

        try:
            total_count = Department.search_count(domain)
            departments = Department.search(
                domain, limit=limit, offset=offset, order=sorting["order"]
            )

            # Sử dụng hàm read() thần thánh để Serialize động
            data = departments.read(fields_to_read)

            return request.make_json_response({
                "success": True,
                "total": total_count,
                "count": len(data),
                "data": data
            })

        except AccessError:
            return self._forbidden("Access Denied: You do not have permission to view departments.")
        except Exception as e:
            return self._server_error(e)

    # ==========================================
    # GET ONE (Get Department)
    # ==========================================
    @http.route("/api/departments/<int:department_id>", auth="public", type="http", methods=["GET"], csrf=False)
    def get_department(self, department_id, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        try:
            department = self._get_department(department_id)

            if not department:
                return self._not_found("Department")

            return request.make_json_response({
                "success": True,
                "data": self._serialize_department(department)
            })

        except AccessError:
            return self._forbidden("Access Denied: You do not have permission to view this department.")
        except Exception as e:
            return self._server_error(e)

    # ==========================================
    # CREATE (Create Department)
    # ==========================================
    @http.route("/api/departments", auth="public", type="http", methods=["POST"], csrf=False)
    def create_department(self, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        try:
            data = self._get_request_data()

            # Validation: Bắt buộc phải có tên phòng ban
            is_valid, error_msg = self._validate_required_fields(data, ["name"])
            if not is_valid:
                return self._bad_request(error_msg)

            # ĐÃ XÓA .sudo()
            department = request.env["hr.department"].create(self._department_create_vals(data))

            return request.make_json_response({
                "success": True,
                "id": department.id
            })

        except AccessError:
            return self._forbidden("Access Denied: You do not have permission to create a department.")
        except ValidationError as e:
            return self._bad_request(str(e))
        except Exception as e:
            return self._server_error(e)

    # ==========================================
    # UPDATE (Update Department)
    # ==========================================
    @http.route("/api/departments/<int:department_id>", auth="public", type="http", methods=["PUT"], csrf=False)
    def update_department(self, department_id, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        try:
            department = self._get_department(department_id)

            if not department:
                return self._not_found("Department")

            data = self._get_request_data()

            # Validation Update: Không được truyền tên rỗng
            is_valid, error_msg = self._validate_update_fields(data, ["name"])
            if not is_valid:
                return self._bad_request(error_msg)

            department.write(self._department_update_vals(department, data))

            return request.make_json_response({
                "success": True,
                "message": "Department updated"
            })

        except AccessError:
            return self._forbidden("Access Denied: You do not have permission to update this department.")
        except ValidationError as e:
            return self._bad_request(str(e))
        except Exception as e:
            return self._server_error(e)

    # ==========================================
    # DELETE (Delete Department)
    # ==========================================
    @http.route("/api/departments/<int:department_id>", auth="public", type="http", methods=["DELETE"], csrf=False)
    def delete_department(self, department_id, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        try:
            department = self._get_department(department_id)

            if not department:
                return self._not_found("Department")

            department.unlink()

            return request.make_json_response({
                "success": True,
                "message": "Department deleted successfully."
            })

        except AccessError:
            return self._forbidden("Access Denied: You do not have permission to delete this department.")
        except ValidationError as e:
            return self._bad_request(str(e))
        except Exception as e:
            # Bắt lỗi nếu xóa phòng ban đang có nhân viên (ràng buộc foreign key)
            return self._server_error(f"Failed to delete department due to dependencies or internal error.")


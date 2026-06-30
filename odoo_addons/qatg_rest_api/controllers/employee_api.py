from odoo import http
from odoo.http import request
from .base_api import BaseAPI
from odoo.exceptions import AccessError, ValidationError, MissingError

class EmployeeAPIController(http.Controller, BaseAPI):

    # ==========================================
    # EMPLOYEE HELPERS
    # ==========================================
    def _build_domain(self, kwargs):

        domain = []

        name = kwargs.get("name")
        email = kwargs.get("email")
        job_title = kwargs.get("job_title")

        department_id = kwargs.get("department_id")
        parent_id = kwargs.get("parent_id")
        company_id = kwargs.get("company_id")

        if department_id:
            domain.append(("department_id", "=", int(department_id)))

        if parent_id:
            domain.append(("parent_id", "=", int(parent_id)))

        if company_id:
            domain.append(("company_id", "=", int(company_id)))

        if name:
            domain.append(("name", "ilike", name))

        if email:
            domain.append(("work_email", "ilike", email))

        if job_title:
            domain.append(("job_title", "ilike", job_title))

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
            # Nếu field tồn tại trong payload gửi lên, NHƯNG giá trị lại rỗng hoặc None
            if field in data and (data[field] is None or str(data[field]).strip() == ""):
                invalid_fields.append(field)

        if invalid_fields:
            return False, f"Cannot set required fields to empty or null: {', '.join(invalid_fields)}"

        return True, ""

    def _get_employee(self, employee_id):
        # ĐÃ XÓA .sudo()
        # Record lấy lên sẽ gắn chặt với quyền của user đang được Impersonate
        employee = request.env["hr.employee"].browse(employee_id)

        # exists() sẽ trả về False nếu record không tồn tại HOẶC user không có quyền truy cập
        return employee if employee.exists() else None

    def _serialize_employee(self, employee):
        return {
            "id": employee.id,
            "name": employee.name,
            "email": employee.work_email,
            "phone": employee.work_phone,
            "job_title": employee.job_title,

            "department": {
                "id": employee.department_id.id,
                "name": employee.department_id.name,
            } if employee.department_id else None,

            "job": {
                "id": employee.job_id.id,
                "name": employee.job_id.name,
            } if employee.job_id else None,

            "manager": {
                "id": employee.parent_id.id,
                "name": employee.parent_id.name,
            } if employee.parent_id else None,

            "coach": {
                "id": employee.coach_id.id,
                "name": employee.coach_id.name,
            } if employee.coach_id else None,

            "user": {
                "id": employee.user_id.id,
                "name": employee.user_id.name,
                "login": employee.user_id.login,
            } if employee.user_id else None,
        }

    def _employee_create_vals(self, data):
        return {
            "name": data.get("name"),
            "work_email": data.get("email"),
            "work_phone": data.get("phone"),
            "job_title": data.get("job_title"),

            "department_id": data.get("department_id"),
            "job_id": data.get("job_id"),
            "parent_id": data.get("parent_id"),
            "coach_id": data.get("coach_id"),

            "user_id": data.get("user_id"),
        }

    def _employee_update_vals(self, employee, data):
        return {
            "name": data.get("name", employee.name),
            "work_email": data.get("email", employee.work_email),
            "work_phone": data.get("phone", employee.work_phone),
            "job_title": data.get("job_title", employee.job_title),

            "department_id": data.get(
                "department_id",
                employee.department_id.id if employee.department_id else False
            ),

            "job_id": data.get(
                "job_id",
                employee.job_id.id if employee.job_id else False
            ),

            "parent_id": data.get(
                "parent_id",
                employee.parent_id.id if employee.parent_id else False
            ),

            "coach_id": data.get(
                "coach_id",
                employee.coach_id.id if employee.coach_id else False
            ),

            "company_id": data.get(
                "company_id",
                employee.company_id.id if employee.company_id else False
            ),

            "user_id": data.get(
                "user_id",
                employee.user_id.id if employee.user_id else False
            ),
        }

    # ==========================================
    # GET ALL
    # ==========================================
    @http.route("/api/employees", auth="public", type="http", methods=["GET"], csrf=False)
    def get_employees(self, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        domain = self._build_domain(kwargs)
        limit, offset = self._get_pagination(kwargs)
        sorting = self._get_sorting(kwargs, ["id", "name", "work_email", "job_title"])

        # KHAI BÁO WHITELIST: Các trường an toàn cho phép Client được quyền lấy
        allowed_fields = [
            "id", "name", "work_email", "work_phone", "job_title",
            "department_id", "job_id", "parent_id", "coach_id", "user_id"
        ]

        # Lấy danh sách fields mà client thực sự muốn
        fields_to_read = self._get_requested_fields(kwargs, allowed_fields)

        Employee = request.env["hr.employee"]

        try:
            total_count = Employee.search_count(domain)
            employees = Employee.search(
                domain, limit=limit, offset=offset, order=sorting["order"]
            )

            # CỰC KỲ NGẮN GỌN: Dùng trực tiếp hàm read() của Odoo
            # Dữ liệu trả về sẽ tự động chỉ chứa các fields nằm trong biến 'fields_to_read'
            data = employees.read(fields_to_read)

            return request.make_json_response({
                "success": True,
                "total": total_count,
                "count": len(data),
                "data": data
            })

        except AccessError:
            return self._forbidden("Access Denied: You do not have permission to view employees.")
        except Exception as e:
            return self._server_error(e)

    # ==========================================
    # GET ONE
    # ==========================================
    @http.route("/api/employees/<int:employee_id>", auth="public", type="http", methods=["GET"], csrf=False)
    def get_employee(self, employee_id, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        try:
            employee = self._get_employee(employee_id)

            if not employee:
                return self._not_found("Employee")

            return request.make_json_response({
                "success": True,
                "data": self._serialize_employee(employee)
            })

        except AccessError:
            return self._forbidden("Access Denied: You do not have permission to view this employee.")
        except Exception as e:
            return self._server_error(e)

    # ==========================================
    # CREATE
    # ==========================================
    @http.route("/api/employees", auth="public", type="http", methods=["POST"], csrf=False)
    def create_employee(self, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        try:
            data = self._get_request_data()
            is_valid, error_msg = self._validate_required_fields(data, ["name"])
            if not is_valid:
                return self._bad_request(error_msg)

            employee = request.env["hr.employee"].create(self._employee_create_vals(data))

            return request.make_json_response({
                "success": True,
                "id": employee.id
            })

        except AccessError:
            # Lỗi 403: Chặn thao tác vượt quyền
            return self._forbidden("Access Denied: You do not have permission to create an employee.")
        except ValidationError as e:
            # Lỗi 400: Trả về chính xác thông báo lỗi dữ liệu (str(e) của ValidationError thường an toàn để hiển thị)
            return self._bad_request(str(e))
        except Exception as e:
            # Lỗi 500: Lỗi hệ thống bất ngờ (đã được ẩn chi tiết trong _server_error)
            return self._server_error(e)

    # ==========================================
    # UPDATE
    # ==========================================
    @http.route("/api/employees/<int:employee_id>", auth="public", type="http", methods=["PUT"], csrf=False)
    def update_employee(self, employee_id, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        try:
            employee = self._get_employee(employee_id)

            if not employee:
                return self._not_found("Employee")

            data = self._get_request_data()

            is_valid, error_msg = self._validate_update_fields(data, ["name"])
            if not is_valid:
                return self._bad_request(error_msg)
            # Môi trường an toàn: Nếu user không có quyền sửa, hàm write() sẽ ném ra AccessError
            employee.write(self._employee_update_vals(employee, data))

            return request.make_json_response({
                "success": True,
                "message": "Employee updated"
            })

        except AccessError:
            # Lỗi 403: Chặn thao tác vượt quyền
            return self._forbidden("Access Denied: You do not have permission to create an employee.")

        except ValidationError as e:
            # Lỗi 400: Trả về chính xác thông báo lỗi dữ liệu (str(e) của ValidationError thường an toàn để hiển thị)
            return self._bad_request(str(e))

        except Exception as e:
            # Lỗi 500: Lỗi hệ thống bất ngờ (đã được ẩn chi tiết trong _server_error)
            return self._server_error(e)

    # ==========================================
    # DELETE
    # ==========================================
    @http.route("/api/employees/<int:employee_id>", auth="public", type="http", methods=["DELETE"], csrf=False)
    def delete_employee(self, employee_id, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        try:
            employee = self._get_employee(employee_id)

            if not employee:
                return self._not_found("Employee")

            # Môi trường an toàn: Nếu user không có quyền xóa, hàm unlink() sẽ ném ra AccessError
            employee.unlink()

            return request.make_json_response({
                "success": True,
                "message": "Employee deleted"
            })

        except AccessError:
            # Lỗi 403: Chặn thao tác vượt quyền
            return self._forbidden("Access Denied: You do not have permission to create an employee.")

        except ValidationError as e:
            # Lỗi 400: Trả về chính xác thông báo lỗi dữ liệu (str(e) của ValidationError thường an toàn để hiển thị)
            return self._bad_request(str(e))

        except Exception as e:
            # Lỗi 500: Lỗi hệ thống bất ngờ (đã được ẩn chi tiết trong _server_error)
            return self._server_error(e)




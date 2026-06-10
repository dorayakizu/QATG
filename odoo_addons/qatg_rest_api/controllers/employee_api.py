from odoo import http
from odoo.http import request
from .base_api import BaseAPI

class EmployeeAPIController(http.Controller,BaseAPI):

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
            domain.append(
                ("department_id", "=", int(department_id))
            )

        if parent_id:
            domain.append(
                ("parent_id", "=", int(parent_id))
            )

        if company_id:
            domain.append(
                ("company_id", "=", int(company_id))
            )

        if name:
            domain.append(
                ("name", "ilike", name)
            )

        if email:
            domain.append(
                (
                    "work_email",
                    "ilike",
                    email
                )
            )

        if job_title:
            domain.append(
                (
                    "job_title",
                    "ilike",
                    job_title
                )
            )

        return domain

    def _get_employee(self, employee_id):

        employee = (
            request.env["hr.employee"]
            .sudo()
            .browse(employee_id)
        )

        return (
            employee
            if employee.exists()
            else None
        )

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
            "name": data.get(
                "name",
                employee.name
            ),
            "work_email": data.get(
                "email",
                employee.work_email
            ),
            "work_phone": data.get(
                "phone",
                employee.work_phone
            ),
            "job_title": data.get(
                "job_title",
                employee.job_title
            ),

            "department_id": data.get(
                "department_id",
                employee.department_id.id
                if employee.department_id
                else False
            ),

            "job_id": data.get(
                "job_id",
                employee.job_id.id
                if employee.job_id
                else False
            ),

            "parent_id": data.get(
                "parent_id",
                employee.parent_id.id
                if employee.parent_id
                else False
            ),

            "coach_id": data.get(
                "coach_id",
                employee.coach_id.id
                if employee.coach_id
                else False
            ),

            "company_id": data.get(
                "company_id",
                employee.company_id.id
                if employee.company_id
                else False
            ),

            "user_id": data.get(
                "user_id",
                employee.user_id.id
                if employee.user_id
                else False
            ),
        }

    # ==========================================
    # GET ALL
    # ==========================================
    @http.route(
        "/api/employees",
        auth="public",
        type="http",
        methods=["GET"],
        csrf=False
    )
    def get_employees(self, **kwargs):

        if not self._validate_api_key():
            return self._unauthorized()

        domain = self._build_domain(kwargs)

        limit, offset = (
            self._get_pagination(kwargs)
        )

        sorting = (
            self._get_sorting(
                kwargs,
                [
                    "id",
                    "name",
                    "work_email",
                    "job_title"
                ]
            )
        )

        Employee = (
            request.env["hr.employee"]
            .sudo()
        )

        total_count = (
            Employee.search_count(
                domain
            )
        )

        employees = Employee.search(
            domain,
            limit=limit,
            offset=offset,
            order=sorting["order"]
        )

        data = [
            self._serialize_employee(
                emp
            )
            for emp in employees
        ]

        return request.make_json_response(
            {
                "success": True,
                "total": total_count,
                "count": len(data),
                "limit": limit,
                "offset": offset,
                "sort_by": sorting["sort_by"],
                "sort_order": sorting["sort_order"],
                "data": data
            }
        )

    # ==========================================
    # GET ONE
    # ==========================================
    @http.route(
        "/api/employees/<int:employee_id>",
        auth="public",
        type="http",
        methods=["GET"],
        csrf=False
    )
    def get_employee(self, employee_id, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        employee = self._get_employee(
            employee_id
        )

        if not employee:
            return self._not_found(
                "Employee"
            )

        return request.make_json_response(
            {
                "success": True,
                "data": self._serialize_employee(
                    employee
                )
            }
        )

    # ==========================================
    # CREATE
    # ==========================================
    @http.route(
        "/api/employees",
        auth="public",
        type="http",
        methods=["POST"],
        csrf=False
    )
    def create_employee(self, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        try:
            data = (
                self._get_request_data()
            )

            employee = (
                request.env["hr.employee"]
                .sudo()
                .create(
                    self._employee_create_vals(
                        data
                    )
                )
            )

            return request.make_json_response(
                {
                    "success": True,
                    "id": employee.id
                }
            )

        except Exception as e:
            return self._server_error(e)

    # ==========================================
    # UPDATE
    # ==========================================
    @http.route(
        "/api/employees/<int:employee_id>",
        auth="public",
        type="http",
        methods=["PUT"],
        csrf=False
    )
    def update_employee(self, employee_id, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        employee = self._get_employee(employee_id)

        if not employee:
            return self._not_found("Employee")

        try:
            data = (
                self._get_request_data()
            )

            employee.write(
                self._employee_update_vals(
                    employee,
                    data
                )
            )

            return request.make_json_response(
                {
                    "success": True,
                    "message": "Employee updated"
                }
            )

        except Exception as e:
            return self._server_error(e)

    # ==========================================
    # DELETE
    # ==========================================
    @http.route(
        "/api/employees/<int:employee_id>",
        auth="public",
        type="http",
        methods=["DELETE"],
        csrf=False
    )
    def delete_employee(self, employee_id, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        employee = self._get_employee(employee_id)

        if not employee:
            return self._not_found("Employee")

        employee.unlink()

        return request.make_json_response(
            {
                "success": True,
                "message": "Employee deleted"
            }
        )

    # @http.route(
    #     "/api/employees/fields",
    #     auth="public",
    #     type="http",
    #     methods=["GET"],
    #     csrf=False
    # )
    # def get_employee_fields(self, **kwargs):
    #     if not self._validate_api_key():
    #         return self._unauthorized()
    #
    #     fields = request.env["hr.employee"]._fields
    #
    #     return request.make_json_response({
    #         "success": True,
    #         "fields": list(fields.keys())
    #     })
    #
    
    
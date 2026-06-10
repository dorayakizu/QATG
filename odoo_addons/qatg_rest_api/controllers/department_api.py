from odoo import http
from odoo.http import request
from .base_api import BaseAPI

class DepartmentAPIController(http.Controller,BaseAPI):

    # ==========================================
    # DEPARTMENT HELPERS
    # ==========================================
    def _build_domain(self, kwargs):
        """Builds the domain filter based on query parameters."""
        domain = []

        # Get required filters from kwargs
        name = kwargs.get("name")
        parent_id = kwargs.get("parent_id")
        manager_id = kwargs.get("manager_id")
        company_id = kwargs.get("company_id")

        # Build domain list (using ilike for name search, assuming parent/manager IDs are mandatory integers)
        if parent_id:
            domain.append(("parent_id", "=", int(parent_id)))

        if manager_id:
            domain.append(("manager_id", "=", int(manager_id)))

        if company_id:
            domain.append(("company_id", "=", int(company_id)))

        if name:
            domain.append(("name", "ilike", name))

        return domain

    def _get_department(self, department_id):
        """Retrieves a single Department record by ID."""
        department = (
            request.env["hr.department"]
            .sudo()
            .browse(department_id)
        )

        return (
            department
            if department.exists()
            else None
        )

    def _serialize_department(self, department):
        """Serializes Department record to standardized JSON format."""
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
        }

    def _department_create_vals(self, data):
        """Validates and formats data for creating a new Department."""
        return {
            "name": data.get("name"),

            "parent_id": data.get("parent_id"), 
            "manager_id": data.get("manager_id"),


        }

    def _department_update_vals(self, department, data):
        """Validates and formats data for updating an existing Department."""
        return {
            "name": data.get(
                "name",
                department.name
            ),
            # Check if the incoming IDs are present in the payload (i.e., provided by user)
            "parent_id": data.get("parent_id") or department.parent_id.id, 
            "manager_id": data.get("manager_id") or department.manager_id.id,
        }

    # ==========================================
    # GET ALL (List Departments)
    # ==========================================
    @http.route(
        "/api/departments",
        auth="public",
        type="http",
        methods=["GET"],
        csrf=False
    )
    def get_departments(self, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        domain = self._build_domain(kwargs)

        limit, offset = (
            self._get_pagination(
                kwargs
            )
        )

        sorting = (
            self._get_sorting(
                kwargs,
                ["id", "name"]
            )
        )

        Department = (
            request.env["hr.department"]
            .sudo()
        )

        total_count = (
            Department.search_count(
                domain
            )
        )

        departments = Department.search(
            domain,
            limit=limit,
            offset=offset,
            order=sorting["order"]
        )

        data = [
            self._serialize_department(
                dept
            ) for dept in departments
        ]

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

    # ==========================================
    # GET ONE (Get Department)
    # ==========================================
    @http.route(
        "/api/departments/<int:department_id>",
        auth="public",
        type="http",
        methods=["GET"],
        csrf=False
    )
    def get_department(self, department_id, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        department = self._get_department(department_id)

        if not department:
            return self._not_found("Department")

        return request.make_json_response({
            "success": True,
            "data": self._serialize_department(department)
        })


    # ==========================================
    # CREATE (Create Department)
    # ==========================================
    @http.route(
        "/api/departments",
        auth="public",
        type="http",
        methods=["POST"],
        csrf=False
    )
    def create_department(self, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        try:
            data = (
                self._get_request_data()
            )

            department = (
                request.env["hr.department"]
                .sudo()
                .create(
                    self._department_create_vals(
                        data
                    )
                )
            )

            return request.make_json_response({
                "success": True,
                "id": department.id
            })

        except Exception as e:
            return self._server_error(e)


    # ==========================================
    # UPDATE (Update Department)
    # ==========================================
    @http.route(
        "/api/departments/<int:department_id>",
        auth="public",
        type="http",
        methods=["PUT"],
        csrf=False
    )
    def update_department(self, department_id, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        department = self._get_department(department_id)

        if not department:
            return self._not_found("Department")

        try:
            data = (
                self._get_request_data()
            )
            
            # Use the validation method to get safe update values
            vals = self._department_update_vals(department, data)
            
            if not vals:
                 return request.make_json_response({"success": False, "error": "No valid fields provided for update."})

            department.write(vals)

            return request.make_json_response({
                "success": True,
                "message": "Department updated"
            })

        except Exception as e:
            return self._server_error(e)


    # ==========================================
    # DELETE (Delete Department)
    # ==========================================
    @http.route(
        "/api/departments/<int:department_id>",
        auth="public",
        type="http",
        methods=["DELETE"],
        csrf=False
    )
    def delete_department(self, department_id, **kwargs):
        if not self._validate_api_key():
            return self._unauthorized()

        department = self._get_department(department_id)

        if not department:
            return self._not_found("Department")
        
        # IMPORTANT: Deleting a core record like Department should require confirmation/checks.
        # For now, we follow the pattern but warn about potential side effects.
        try:
             department.unlink()
             return request.make_json_response({"success": True, "message": "Department deleted successfully."})
        except Exception as e:
            return self._server_error(f"Failed to delete department due to dependencies: {e}")



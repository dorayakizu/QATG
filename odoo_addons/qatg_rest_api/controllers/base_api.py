from odoo.http import request
import json


class BaseAPI:

    # ==========================================
    # AUTH
    # ==========================================
    def _validate_api_key(self):

        api_key = request.httprequest.headers.get(
            "X-API-Key"
        )

        stored_api_key = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "employee_api.api_key"
            )
        )

        return api_key == stored_api_key

    def _unauthorized(self):

        return request.make_json_response(
            {
                "success": False,
                "message": "Invalid API Key"
            },
            status=401
        )

    # ==========================================
    # COMMON RESPONSES
    # ==========================================
    def _not_found(
        self,
        resource="Record"
    ):

        return request.make_json_response(
            {
                "success": False,
                "message": f"{resource} not found"
            },
            status=404
        )

    def _server_error(
        self,
        error
    ):

        return request.make_json_response(
            {
                "success": False,
                "message": str(error)
            },
            status=500
        )

    # ==========================================
    # REQUEST DATA
    # ==========================================
    def _get_request_data(self):

        try:

            return json.loads(
                request.httprequest.data.decode(
                    "utf-8"
                )
            )

        except Exception:

            return {}

    # ==========================================
    # PAGINATION
    # ==========================================
    def _get_pagination(
        self,
        kwargs
    ):

        try:
            limit = int(
                kwargs.get(
                    "limit",
                    20
                )
            )
        except (
            ValueError,
            TypeError
        ):
            limit = 20

        try:
            offset = int(
                kwargs.get(
                    "offset",
                    0
                )
            )
        except (
            ValueError,
            TypeError
        ):
            offset = 0

        return limit, offset

    # ==========================================
    # SORTING
    # ==========================================
    def _get_sorting(
        self,
        kwargs,
        allowed_fields
    ):

        sort_by = kwargs.get(
            "sort_by",
            "id"
        )

        sort_order = kwargs.get(
            "sort_order",
            "asc"
        ).lower()

        if sort_by not in allowed_fields:
            sort_by = "id"

        if sort_order not in [
            "asc",
            "desc"
        ]:
            sort_order = "asc"

        return {
            "sort_by": sort_by,
            "sort_order": sort_order,
            "order": f"{sort_by} {sort_order}"
        }


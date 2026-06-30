from odoo.http import request
import json


class BaseAPI:
    # ==========================================
    # AUTH
    # ==========================================
    def _validate_api_key(self):
        # 1. Lấy thông tin từ Headers
        api_key = request.httprequest.headers.get("X-API-Key")
        user_login = request.httprequest.headers.get("X-User-Login")

        # 2. Kiểm tra Master API Key
        IrConfig = request.env["ir.config_parameter"].sudo()
        stored_api_key = IrConfig.get_param("custom_api.api_key")

        if not api_key or api_key != stored_api_key:
            return False

        # 3. Xử lý User Context (Impersonation)
        if user_login:
            # Tìm user theo login/email
            user = request.env["res.users"].sudo().search([("login", "=", user_login)], limit=1)

            if not user:
                return False  # Trả về False (401) nếu truyền X-User-Login nhưng không tìm thấy

            # Chuyển đổi môi trường sang đúng quyền của user đó
            request.update_env(user=user.id)

        else:
            # Fallback: Nếu không truyền X-User-Login thì dùng user mặc định
            api_user_id = int(IrConfig.get_param("custom_api.user_id", 0))
            if not api_user_id:
                return False
            request.update_env(user=api_user_id)

        return True

    def _unauthorized(self):

        return request.make_json_response(
            {
                "success": False,
                "message": "Invalid API Key or User Login"
            },
            status=401
        )

    # ==========================================
    # COMMON RESPONSES
    # ==========================================
    def _not_found(self,resource="Record"):
        return request.make_json_response(
            {
                "success": False,
                "message": f"{resource} not found"
            },
            status=404
        )

    def _forbidden(self, message="You do not have permission to access this resource"):
        return request.make_json_response(
            {
                "success": False,
                "message": message
            },
            status=403
        )

    def _bad_request(self, message="Bad Request"):
        return request.make_json_response(
            {
                "success": False,
                "message": message
            },
            status=400
        )

    def _server_error(self, error):
        # TỐI ƯU BẢO MẬT: Không in trực tiếp str(error) ra ngoài nữa.
        # Nếu muốn, bạn có thể dùng logging của python để in 'error' vào file log nội bộ ở đây.
        return request.make_json_response(
            {
                "success": False,
                "message": "Internal Server Error"
            },
            status=500
        )

    # ==========================================
    # REQUEST DATA
    # ==========================================
    def _get_request_data(self):
        try:
            return json.loads(request.httprequest.data.decode("utf-8"))
        except Exception:
            return {}

    # ==========================================
    # PAGINATION
    # ==========================================
    def _get_pagination(self,kwargs):
        try:
            limit = int(kwargs.get("limit",20))
        except (ValueError,TypeError):
            limit = 20

        try:
            offset = int(kwargs.get("offset",0))
        except (ValueError,TypeError):
            offset = 0

        return limit, offset

    # ==========================================
    # SORTING
    # ==========================================
    def _get_sorting(self,kwargs,allowed_fields):
        sort_by = kwargs.get("sort_by","id")

        sort_order = kwargs.get("sort_order","asc").lower()

        if sort_by not in allowed_fields:
            sort_by = "id"

        if sort_order not in ["asc","desc"]:
            sort_order = "asc"

        return {
            "sort_by": sort_by,
            "sort_order": sort_order,
            "order": f"{sort_by} {sort_order}"
        }

    def _get_requested_fields(self, kwargs, allowed_fields):
        """
        Lấy danh sách các trường cần serialize dựa trên request của client.
        Nếu client không yêu cầu cụ thể, trả về toàn bộ allowed_fields.
        """
        fields_param = kwargs.get("fields")

        if not fields_param:
            return allowed_fields

        # Tách chuỗi "id,name,email" thành danh sách ['id', 'name', 'email']
        requested_fields = [f.strip() for f in fields_param.split(",")]

        # Lọc ra những trường hợp lệ (chỉ lấy những trường có trong allowed_fields)
        valid_fields = [f for f in requested_fields if f in allowed_fields]

        return valid_fields if valid_fields else allowed_fields

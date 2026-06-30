from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm  # IMPORT THÊM THƯ VIỆN NÀY
import xmlrpc.client

from core.config import settings
from core.security import create_access_token

router = APIRouter(tags=["Auth"])


# BƯỚC 1: XÓA class LoginRequest(BaseModel) đi

# BƯỚC 2: Cập nhật hàm login để dùng OAuth2PasswordRequestForm
@router.post("/login")
def login_for_access_token(request: OAuth2PasswordRequestForm = Depends()):
    try:
        common = xmlrpc.client.ServerProxy(f'{settings.ODOO_URL}/xmlrpc/2/common')

        # Lưu ý: request.username (thay vì request.login) vì chuẩn OAuth2 dùng chữ username
        uid = common.authenticate(settings.ODOO_DB, request.username, request.password, {})

        if not uid:
            raise HTTPException(
                status_code=401,
                detail="Sai tài khoản hoặc mật khẩu"
            )

        # Trả về token (vẫn gán 'sub' bằng request.username)
        access_token = create_access_token(data={"sub": request.username})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "login": request.username,
            "uid": uid
        }

    except xmlrpc.client.Fault as e:
        raise HTTPException(status_code=500, detail=f"Odoo XML-RPC Error: {e}")
    except ConnectionRefusedError:
        raise HTTPException(status_code=503, detail="Không thể kết nối tới máy chủ Odoo")


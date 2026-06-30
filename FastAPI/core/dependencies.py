from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from core.config import settings
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def get_current_user_login(token: str = Depends(oauth2_scheme)) -> str:
    """
    Hàm này tự động lấy Token từ Header, sau đó giải mã để rút ra tên login của user.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_login: str = payload.get("sub")

        if user_login is None:
            raise HTTPException(status_code=401, detail="Token không hợp lệ.")

        return user_login

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Không thể xác thực thông tin tài khoản.")
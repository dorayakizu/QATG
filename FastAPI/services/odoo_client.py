from contextlib import asynccontextmanager

import httpx
from fastapi import HTTPException

from core.config import settings


class OdooClient:

    def __init__(self):

        self.client: httpx.AsyncClient | None = None

    async def startup(self):

        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            headers={
                "X-API-Key": settings.ODOO_API_KEY,
                "Content-Type": "application/json",
            },
            limits=httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100
            )
        )

    async def shutdown(self):

        if self.client:
            await self.client.aclose()

    async def request(
            self,
            method: str,
            endpoint: str,
            json_data: dict | None = None,
            params: dict | None = None,
            user_login: str | None = None  # BƯỚC 1: Thêm tham số định danh User
    ):

        # BƯỚC 2: Cấu hình Header động
        custom_headers = {}
        if user_login:
            custom_headers["X-User-Login"] = user_login

        try:
            response = await self.client.request(
                method=method,
                url=f"{settings.ODOO_URL}{endpoint}",
                json=json_data,
                params=params,
                headers=custom_headers  # BƯỚC 3: Truyền header phụ vào (httpx sẽ tự động gộp với X-API-Key ở startup)
            )

            if response.status_code >= 400:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.text
                )

            return response.json()

        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Odoo request timeout"
            )
        except httpx.ConnectError:
            raise HTTPException(
                status_code=503,
                detail="Cannot connect to Odoo"
            )


odoo_client = OdooClient()

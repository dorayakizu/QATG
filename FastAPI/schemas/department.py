from pydantic import BaseModel, Field

class DepartmentCreate(BaseModel):
    name: str
    manager_id: int | None = None
    parent_id: int | None = None

class DepartmentUpdate(BaseModel):
    name: str | None = None
    manager_id: int | None = None
    parent_id: int | None = None
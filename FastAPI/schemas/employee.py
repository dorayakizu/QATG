from pydantic import BaseModel, Field

class EmployeeCreate(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    job_title: str | None = None
    department_id: int | None = None
    job_id: int | None = None
    parent_id: int | None = None
    coach_id: int | None = None
    company_id: int | None = None
    user_id: int | None = None


class EmployeeUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    job_title: str | None = None
    department_id: int | None = None
    job_id: int | None = None
    parent_id: int | None = None
    coach_id: int | None = None
    company_id: int | None = None
    user_id: int | None = None
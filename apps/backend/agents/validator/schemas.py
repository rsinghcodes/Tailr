from pydantic import BaseModel, Field


class ValidationOutput(BaseModel):
    status: str = "PASSED"
    checks_run: int = 8
    violations: list[str] = Field(default_factory=list)

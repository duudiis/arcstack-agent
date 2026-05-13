from abc import ABC, abstractmethod
from pydantic import BaseModel


class ToolResult(BaseModel):
    success: bool
    output: str
    error: str | None = None


class BaseTool(ABC):
    name: str
    description: str

    @abstractmethod
    async def execute(self, params: dict) -> ToolResult:
        ...

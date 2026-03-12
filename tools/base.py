from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Type

class ToolInput(BaseModel):
    pass

class ToolOutput(BaseModel):
    pass

class BaseTool(ABC):
    name: str
    description: str
    input_model: Type[ToolInput]
    output_model: Type[ToolOutput]

    @abstractmethod
    async def execute(self, input: ToolInput) -> ToolOutput:
        pass

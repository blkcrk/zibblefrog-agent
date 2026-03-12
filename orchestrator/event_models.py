from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime, timezone
import uuid

class AgentEvent(BaseModel):
    type: str
    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent: Optional[str] = None
    step: Optional[str] = None
    status: Optional[str] = None
    content: Optional[Any] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_sse(self) -> str:
        import json
        return f"data: {json.dumps(self.model_dump())}\n\n"

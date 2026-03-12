from tools.base import BaseTool
from typing import Dict

_registry: Dict[str, BaseTool] = {}

def register(tool: BaseTool):
    _registry[tool.name] = tool

def get(name: str) -> BaseTool:
    if name not in _registry:
        raise KeyError(f"Tool not found: {name}")
    return _registry[name]

def all_tools() -> Dict[str, BaseTool]:
    return dict(_registry)

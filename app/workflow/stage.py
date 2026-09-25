from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class Stage:
    name: str
    dependencies: list[str]
    function: Callable[..., Any]

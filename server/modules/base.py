"""Module base class and result contract."""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from server.models import ModuleResult
import time


class BaseModule(ABC):
    name: str = "base"
    module_type: str = "deterministic"

    @abstractmethod
    async def run(self) -> ModuleResult:
        pass

    def _result(self, success: bool, data: dict, brief_text: str = "",
                action_items: list | None = None, error_message: str | None = None,
                duration_ms: int = 0) -> ModuleResult:
        return ModuleResult(
            module_name=self.name,
            module_type=self.module_type,
            ran_at=datetime.now(timezone.utc),
            success=success,
            data=data,
            brief_text=brief_text,
            action_items=action_items or [],
            error_message=error_message,
            duration_ms=duration_ms,
        )


async def timed_run(module: BaseModule) -> ModuleResult:
    """Run a module and measure execution time."""
    start = time.monotonic()
    try:
        result = await module.run()
        result.duration_ms = int((time.monotonic() - start) * 1000)
        return result
    except Exception as e:
        elapsed = int((time.monotonic() - start) * 1000)
        return module._result(
            success=False,
            data={},
            error_message=str(e),
            duration_ms=elapsed,
        )

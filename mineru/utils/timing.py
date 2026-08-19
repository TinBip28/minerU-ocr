"""Stage timing utilities for profiling MinerU OCR pipeline.

Usage:
    from mineru.utils.timing import StageTimer

    timer = StageTimer()
    with timer("layout"):
        layout_model.predict(images)
    with timer("ocr_det"):
        ocr_model.detect(crops)
    with timer("ocr_rec"):
        results, rec_ms = vietocr(crops)

    # Print summary
    print(timer.summary())

    # Get dict for JSON output
    print(timer.to_dict())
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from time import perf_counter
from typing import Iterator


@dataclass
class StageTiming:
    """Timing data for a single stage."""

    stage: str
    started_at: float = 0.0
    elapsed_ms: float = 0.0
    count: int = 0

    def start(self) -> None:
        self.started_at = perf_counter()

    def stop(self) -> None:
        self.elapsed_ms += (perf_counter() - self.started_at) * 1000
        self.count += 1


@dataclass
class StageTimer:
    """Collects timing for multiple pipeline stages."""

    _timings: dict[str, StageTiming] = field(default_factory=dict)
    _stack: list[str] = field(default_factory=list)

    def start(self, stage: str) -> None:
        """Start timing a stage."""
        if stage not in self._timings:
            self._timings[stage] = StageTiming(stage=stage)
        self._timings[stage].start()

    def stop(self, stage: str) -> None:
        """Stop timing a stage."""
        if stage in self._timings:
            self._timings[stage].stop()

    @contextmanager
    def measure(self, stage: str) -> Iterator[None]:
        """Context manager for timing a stage.

        Usage:
            with timer.measure("layout"):
                layout_model.predict(images)
        """
        self.start(stage)
        try:
            yield
        finally:
            self.stop(stage)

    def get_ms(self, stage: str) -> float:
        """Get elapsed milliseconds for a stage."""
        return self._timings.get(stage, StageTiming(stage=stage)).elapsed_ms

    def get_count(self, stage: str) -> int:
        """Get call count for a stage."""
        return self._timings.get(stage, StageTiming(stage=stage)).count

    def total_ms(self) -> float:
        """Get total milliseconds across all stages."""
        return sum(t.elapsed_ms for t in self._timings.values())

    def to_dict(self) -> dict[str, float]:
        """Convert timings to dict with _ms suffix."""
        return {f"{stage}_ms": timing.elapsed_ms for stage, timing in self._timings.items()}

    def to_dict_detailed(self) -> dict[str, dict]:
        """Convert timings to detailed dict with counts."""
        return {
            stage: {"ms": timing.elapsed_ms, "count": timing.count}
            for stage, timing in self._timings.items()
        }

    def summary(self) -> str:
        """Format timings as human-readable string."""
        if not self._timings:
            return "No timings recorded"
        lines = [f"Stage timings (ms):"]
        for stage, timing in sorted(self._timings.items()):
            avg = timing.elapsed_ms / timing.count if timing.count > 0 else 0
            lines.append(f"  {stage}: {timing.elapsed_ms:.1f}ms ({timing.count} calls, avg {avg:.1f}ms)")
        lines.append(f"  TOTAL: {self.total_ms():.1f}ms")
        return "\n".join(lines)

    def reset(self) -> None:
        """Clear all timings."""
        self._timings.clear()
        self._stack.clear()


# Global timer instance for easy access
_global_timer: StageTimer | None = None


def get_timer() -> StageTimer:
    """Get or create the global timer instance."""
    global _global_timer
    if _global_timer is None:
        _global_timer = StageTimer()
    return _global_timer


def reset_timer() -> None:
    """Reset the global timer."""
    global _global_timer
    if _global_timer is not None:
        _global_timer.reset()


@contextmanager
def measure_stage(stage: str, timer: StageTimer | None = None) -> Iterator[None]:
    """Context manager that measures a stage with optional custom timer.

    Usage:
        with measure_stage("layout"):
            layout_model.predict(images)
    """
    t = timer or get_timer()
    with t.measure(stage):
        yield

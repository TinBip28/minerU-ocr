"""Tests for timing utilities."""

import time

from mineru.utils.timing import StageTimer, get_timer, measure_stage, reset_timer


class TestStageTimer:
    """Test StageTimer functionality."""

    def test_start_stop(self):
        """Basic start/stop timing."""
        timer = StageTimer()
        timer.start("test")
        time.sleep(0.01)  # 10ms
        timer.stop("test")

        assert timer.get_ms("test") >= 10
        assert timer.get_count("test") == 1

    def test_context_manager(self):
        """Context manager timing."""
        timer = StageTimer()
        with timer.measure("layout"):
            time.sleep(0.01)

        assert timer.get_ms("layout") >= 10
        assert timer.get_count("layout") == 1

    def test_multiple_stages(self):
        """Multiple stages timing."""
        timer = StageTimer()
        with timer.measure("stage1"):
            time.sleep(0.01)
        with timer.measure("stage2"):
            time.sleep(0.02)
        with timer.measure("stage1"):
            time.sleep(0.01)

        assert timer.get_ms("stage1") >= 20
        assert timer.get_count("stage1") == 2
        assert timer.get_ms("stage2") >= 20
        assert timer.get_count("stage2") == 1

    def test_to_dict(self):
        """Convert to dict."""
        timer = StageTimer()
        with timer.measure("layout"):
            time.sleep(0.01)

        d = timer.to_dict()
        assert "layout_ms" in d
        assert d["layout_ms"] >= 10

    def test_to_dict_detailed(self):
        """Convert to detailed dict with counts."""
        timer = StageTimer()
        with timer.measure("test"):
            time.sleep(0.001)  # Ensure measurable
        with timer.measure("test"):
            time.sleep(0.001)

        d = timer.to_dict_detailed()
        assert d["test"]["ms"] >= 1  # At least 1ms
        assert d["test"]["count"] == 2

    def test_total_ms(self):
        """Total milliseconds."""
        timer = StageTimer()
        with timer.measure("a"):
            time.sleep(0.01)
        with timer.measure("b"):
            time.sleep(0.01)

        total = timer.total_ms()
        assert total >= 20

    def test_summary(self):
        """Summary formatting."""
        timer = StageTimer()
        with timer.measure("layout"):
            time.sleep(0.01)

        summary = timer.summary()
        assert "layout" in summary
        assert "TOTAL" in summary

    def test_reset(self):
        """Reset clears timings."""
        timer = StageTimer()
        with timer.measure("test"):
            pass
        timer.reset()

        assert timer.get_ms("test") == 0
        assert timer.get_count("test") == 0


class TestGlobalTimer:
    """Test global timer singleton."""

    def test_get_timer(self):
        """Get global timer."""
        reset_timer()
        t1 = get_timer()
        t2 = get_timer()
        assert t1 is t2

    def test_reset_timer(self):
        """Reset global timer."""
        reset_timer()
        timer = get_timer()
        with timer.measure("test"):
            pass
        reset_timer()
        assert timer.get_ms("test") == 0


class TestMeasureStageDecorator:
    """Test measure_stage context manager."""

    def test_measure_stage(self):
        """measure_stage context manager."""
        timer = StageTimer()
        with measure_stage("layout", timer):
            time.sleep(0.01)

        assert timer.get_ms("layout") >= 10

    def test_measure_stage_default_timer(self):
        """measure_stage with default timer."""
        reset_timer()
        with measure_stage("test"):
            time.sleep(0.01)

        assert get_timer().get_ms("test") >= 10

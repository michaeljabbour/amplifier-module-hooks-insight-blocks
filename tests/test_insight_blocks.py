"""Tests for the insight blocks hook module."""

from pathlib import Path

import pytest
import yaml

from amplifier_core import HookResult


def test_bundle_declares_insight_blocks_git_source() -> None:
    """The bundle locates its hook without relying on a preinstalled module."""
    bundle_path = Path(__file__).resolve().parents[1] / "bundle.md"
    text = bundle_path.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    _, header, _ = text.split("---", 2)
    manifest = yaml.safe_load(header)
    hooks = [
        hook for hook in manifest["hooks"] if hook["module"] == "hooks-insight-blocks"
    ]

    assert len(hooks) == 1
    assert hooks[0].get("source") == (
        "git+https://github.com/michaeljabbour/amplifier-module-hooks-insight-blocks@main"
    )
    assert hooks[0]["config"] == {"mode": "explanatory", "enabled": True}


class MockHookRegistry:
    """Mock hook registry for testing."""

    def __init__(self):
        self.registered_handlers = []

    def register(self, event: str, handler, priority: int = 0, name: str | None = None):
        self.registered_handlers.append({
            "event": event,
            "handler": handler,
            "priority": priority,
            "name": name,
        })


class MockCoordinator:
    """Mock module coordinator for testing."""

    def __init__(self):
        self.hooks = MockHookRegistry()


@pytest.mark.asyncio
async def test_mount_registers_session_start_handler():
    """Test that mount() registers a handler for session:start."""
    from amplifier_module_hooks_insight_blocks import mount

    coordinator = MockCoordinator()
    await mount(coordinator, {})

    assert len(coordinator.hooks.registered_handlers) == 1
    handler_info = coordinator.hooks.registered_handlers[0]
    assert handler_info["event"] == "session:start"
    assert handler_info["name"] == "hooks-insight-blocks"


@pytest.mark.asyncio
async def test_mount_with_disabled_config():
    """Test that mount() does nothing when disabled."""
    from amplifier_module_hooks_insight_blocks import mount

    coordinator = MockCoordinator()
    await mount(coordinator, {"enabled": False})

    assert len(coordinator.hooks.registered_handlers) == 0


@pytest.mark.asyncio
async def test_handler_returns_inject_context():
    """Test that the handler returns inject_context action."""
    from amplifier_module_hooks_insight_blocks import mount

    coordinator = MockCoordinator()
    await mount(coordinator, {"mode": "explanatory"})

    handler = coordinator.hooks.registered_handlers[0]["handler"]
    result = await handler("session:start", {})

    assert isinstance(result, HookResult)
    assert result.action == "inject_context"
    assert result.context_injection is not None
    assert "★ Insight" in result.context_injection
    assert result.context_injection_role == "system"


@pytest.mark.asyncio
async def test_explanatory_mode_content():
    """Test explanatory mode includes correct instructions."""
    from amplifier_module_hooks_insight_blocks import mount

    coordinator = MockCoordinator()
    await mount(coordinator, {"mode": "explanatory"})

    handler = coordinator.hooks.registered_handlers[0]["handler"]
    result = await handler("session:start", {})

    assert "explanatory" in result.context_injection.lower()
    assert "★ Insight" in result.context_injection


@pytest.mark.asyncio
async def test_learning_mode_content():
    """Test learning mode includes correct instructions."""
    from amplifier_module_hooks_insight_blocks import mount

    coordinator = MockCoordinator()
    await mount(coordinator, {"mode": "learning"})

    handler = coordinator.hooks.registered_handlers[0]["handler"]
    result = await handler("session:start", {})

    assert "learning" in result.context_injection.lower()
    assert "5-10 lines" in result.context_injection


@pytest.mark.asyncio
async def test_combined_mode_content():
    """Test combined mode includes both explanatory and learning instructions."""
    from amplifier_module_hooks_insight_blocks import mount

    coordinator = MockCoordinator()
    await mount(coordinator, {"mode": "combined"})

    handler = coordinator.hooks.registered_handlers[0]["handler"]
    result = await handler("session:start", {})

    assert "learning" in result.context_injection.lower()
    assert "★ Insight" in result.context_injection


@pytest.mark.asyncio
async def test_custom_priority():
    """Test that custom priority is respected."""
    from amplifier_module_hooks_insight_blocks import mount

    coordinator = MockCoordinator()
    await mount(coordinator, {"priority": 100})

    handler_info = coordinator.hooks.registered_handlers[0]
    assert handler_info["priority"] == 100


def test_get_instructions_default():
    """Test get_instructions returns explanatory for unknown mode."""
    from amplifier_module_hooks_insight_blocks import get_instructions

    result = get_instructions("unknown_mode")
    assert "explanatory" in result.lower()


# ---------------------------------------------------------------------------
# Insight Block Extraction Tests
# ---------------------------------------------------------------------------


class TestInsightBlockExtraction:
    """Test the formatting module's insight block extraction logic."""

    def test_extract_single_block(self):
        """Single insight block is extracted cleanly."""
        from amplifier_module_hooks_insight_blocks.formatting import extract_insight_blocks

        text = (
            "`★ Insight ─────────────────────────────────`\n"
            "Key point one\nKey point two\n"
            "`─────────────────────────────────────────────`"
        )
        insights, remaining = extract_insight_blocks(text)
        assert len(insights) == 1
        assert "Key point one" in insights[0]
        assert "Key point two" in insights[0]
        assert remaining == ""

    def test_extract_embedded_block(self):
        """Insight block surrounded by regular text returns both parts."""
        from amplifier_module_hooks_insight_blocks.formatting import extract_insight_blocks

        text = (
            "Some preamble text.\n\n"
            "`★ Insight ─────────────────────────────────`\n"
            "Educational content here\n"
            "`─────────────────────────────────────────────`\n\n"
            "Some trailing text."
        )
        insights, remaining = extract_insight_blocks(text)
        assert len(insights) == 1
        assert "Educational content" in insights[0]
        assert "preamble" in remaining
        assert "trailing" in remaining

    def test_extract_no_blocks(self):
        """Plain text with no insight delimiters passes through unchanged."""
        from amplifier_module_hooks_insight_blocks.formatting import extract_insight_blocks

        text = "Just regular output text with no special blocks."
        insights, remaining = extract_insight_blocks(text)
        assert insights == []
        assert remaining == text

    def test_extract_multiple_blocks(self):
        """Two insight blocks in one text chunk are both extracted."""
        from amplifier_module_hooks_insight_blocks.formatting import extract_insight_blocks

        text = (
            "`★ Insight ─────────────────────────────────`\n"
            "First insight\n"
            "`─────────────────────────────────────────────`\n"
            "Middle text\n"
            "`★ Insight ─────────────────────────────────`\n"
            "Second insight\n"
            "`─────────────────────────────────────────────`"
        )
        insights, remaining = extract_insight_blocks(text)
        assert len(insights) == 2
        assert "First insight" in insights[0]
        assert "Second insight" in insights[1]
        assert "Middle text" in remaining

    def test_unclosed_block_passes_through(self):
        """Opening delimiter without closing delimiter is not matched."""
        from amplifier_module_hooks_insight_blocks.formatting import extract_insight_blocks

        text = (
            "`★ Insight ─────────────────────────────────`\n"
            "Unclosed content here"
        )
        insights, remaining = extract_insight_blocks(text)
        assert insights == []
        assert remaining == text

    def test_variable_length_dashes(self):
        """Regex handles variable-length dash runs."""
        from amplifier_module_hooks_insight_blocks.formatting import extract_insight_blocks

        text = (
            "`★ Insight ──────────────────────────────────────────`\n"
            "Content with longer dashes\n"
            "`──────────────────────────────────────────────────────`"
        )
        insights, remaining = extract_insight_blocks(text)
        assert len(insights) == 1
        assert "Content with longer dashes" in insights[0]

    def test_quick_check_pattern(self):
        """INSIGHT_OPEN_PATTERN provides efficient quick-check."""
        from amplifier_module_hooks_insight_blocks.formatting import INSIGHT_OPEN_PATTERN

        assert INSIGHT_OPEN_PATTERN.search("Contains ★ Insight marker")
        assert not INSIGHT_OPEN_PATTERN.search("No special markers here")

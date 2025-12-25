"""Tests for the insight blocks hook module."""

import pytest

from amplifier_core import HookResult


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

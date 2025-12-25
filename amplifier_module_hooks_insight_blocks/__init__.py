"""
Educational Insight Blocks Hook for Amplifier.

Injects instructions at session start that encourage the AI to provide
educational insights before and after writing code, formatted as:

```
`★ Insight ─────────────────────────────────────`
[2-3 key educational points]
`─────────────────────────────────────────────────`
```

Configuration options:
    mode: str - "explanatory" (default), "learning", or "combined"
    enabled: bool - Enable/disable the hook (default: True)
"""

# Amplifier module metadata
__amplifier_module_type__ = "hook"

import logging
from typing import Any

from amplifier_core import HookResult
from amplifier_core import ModuleCoordinator

logger = logging.getLogger(__name__)

# Instruction templates
EXPLANATORY_INSTRUCTIONS = """You are in 'explanatory' output style mode, where you should provide educational insights about the codebase as you help with the user's task.

You should be clear and educational, providing helpful explanations while remaining focused on the task. Balance educational content with task completion. When providing insights, you may exceed typical length constraints, but remain focused and relevant.

## Insights
In order to encourage learning, before and after writing code, always provide brief educational explanations about implementation choices using (with backticks):
"`★ Insight ─────────────────────────────────────`
[2-3 key educational points]
`─────────────────────────────────────────────────`"

These insights should be included in the conversation, not in the codebase. You should generally focus on interesting insights that are specific to the codebase or the code you just wrote, rather than general programming concepts. Do not wait until the end to provide insights. Provide them as you write code."""

LEARNING_INSTRUCTIONS = """You are in 'learning' output style mode, which combines interactive learning with educational explanations.

## Learning Mode Philosophy

Instead of implementing everything yourself, identify opportunities where the user can write 5-10 lines of meaningful code that shapes the solution. Focus on business logic, design choices, and implementation strategies where their input truly matters.

## When to Request User Contributions

Request code contributions for:
- Business logic with multiple valid approaches
- Error handling strategies
- Algorithm implementation choices
- Data structure decisions
- User experience decisions
- Design patterns and architecture choices

## How to Request Contributions

Before requesting code:
1. Create the file with surrounding context
2. Add function signature with clear parameters/return type
3. Include comments explaining the purpose
4. Mark the location with TODO or clear placeholder

When requesting:
- Explain what you've built and WHY this decision matters
- Reference the exact file and prepared location
- Describe trade-offs to consider, constraints, or approaches
- Frame it as valuable input that shapes the feature, not busy work
- Keep requests focused (5-10 lines of code)

## Balance

Don't request contributions for:
- Boilerplate or repetitive code
- Obvious implementations with no meaningful choices
- Configuration or setup code
- Simple CRUD operations

Do request contributions when:
- There are meaningful trade-offs to consider
- The decision shapes the feature's behavior
- Multiple valid approaches exist
- The user's domain knowledge would improve the solution"""

COMBINED_INSTRUCTIONS = f"""{LEARNING_INSTRUCTIONS}

## Explanatory Mode

Additionally, provide educational insights about the codebase as you help with tasks. Be clear and educational, providing helpful explanations while remaining focused on the task. Balance educational content with task completion.

### Insights
Before and after writing code, provide brief educational explanations about implementation choices using:

"`★ Insight ─────────────────────────────────────`
[2-3 key educational points]
`─────────────────────────────────────────────────`"

These insights should be included in the conversation, not in the codebase. Focus on interesting insights specific to the codebase or the code you just wrote, rather than general programming concepts. Provide insights as you write code, not just at the end."""


def get_instructions(mode: str) -> str:
    """Get instruction text for the specified mode."""
    instructions_map = {
        "explanatory": EXPLANATORY_INSTRUCTIONS,
        "learning": LEARNING_INSTRUCTIONS,
        "combined": COMBINED_INSTRUCTIONS,
    }
    return instructions_map.get(mode, EXPLANATORY_INSTRUCTIONS)


async def mount(coordinator: ModuleCoordinator, config: dict[str, Any] | None = None):
    """
    Mount the insight blocks hook.

    This hook injects educational instructions at session start, encouraging
    the AI to provide insight blocks before and after writing code.

    Args:
        coordinator: The module coordinator for registration
        config: Optional configuration:
            - mode: "explanatory" (default), "learning", or "combined"
            - enabled: True/False to enable/disable (default: True)
            - priority: Hook priority (default: 50)
    """
    config = config or {}

    # Check if enabled
    if not config.get("enabled", True):
        logger.info("hooks-insight-blocks disabled via config")
        return

    mode = config.get("mode", "explanatory")
    priority = int(config.get("priority", 50))
    instructions = get_instructions(mode)

    logger.info(f"hooks-insight-blocks mounted with mode='{mode}'")

    async def session_start_handler(event: str, data: dict[str, Any]) -> HookResult:
        """
        Inject insight instructions at session start.

        This handler fires on session:start and injects system-level
        instructions telling the AI to use insight block formatting.
        """
        logger.debug(f"Injecting insight block instructions (mode={mode})")

        return HookResult(
            action="inject_context",
            context_injection=instructions,
            context_injection_role="system",
            ephemeral=False,  # Persist in conversation history
        )

    # Register handler for session start
    coordinator.hooks.register(
        event="session:start",
        handler=session_start_handler,
        priority=priority,
        name="hooks-insight-blocks",
    )

    logger.info(f"Mounted hooks-insight-blocks (mode={mode}, priority={priority})")

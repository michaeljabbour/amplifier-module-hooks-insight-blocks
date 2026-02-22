# Amplifier Module: Insight Blocks Hook

Educational insight blocks hook that injects instructions for the AI to provide learning-focused insights before and after writing code.

## Overview

This module uses the Amplifier hooks system to inject instructions at session start, encouraging the AI to display educational insights in a distinctive format:

```
`★ Insight ─────────────────────────────────────`
[2-3 key educational points about the code]
`─────────────────────────────────────────────────`
```

## Integration with hooks-streaming-ui

This module's functionality is also available as a built-in feature of
[amplifier-module-hooks-streaming-ui](https://github.com/michaeljabbour/amplifier-module-hooks-streaming-ui)
(on the `feature/session-indicator` branch). If you're already using the streaming UI module,
you can enable insight blocks there instead of mounting this as a separate hook:

```yaml
hooks:
  - module: hooks-streaming-ui
    config:
      ui:
        insight_mode: explanatory  # or "learning" or "combined"
```

Use this standalone module when you want insight injection **without** the streaming UI,
or when you need independent configuration (e.g., different priority).

## Installation

Add to your bundle:

```yaml
hooks:
  - module: hooks-insight-blocks
    source: git+https://github.com/michaeljabbour/amplifier-module-hooks-insight-blocks@main
    config:
      mode: explanatory  # or "learning" or "combined"
```

Or for local development:

```bash
export AMPLIFIER_MODULE_HOOKS_INSIGHT_BLOCKS=~/dev/amplifier-module-hooks-insight-blocks
```

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `mode` | string | `"explanatory"` | Insight mode: `explanatory`, `learning`, or `combined` |
| `enabled` | bool | `true` | Enable/disable the hook |
| `priority` | int | `50` | Hook execution priority (lower = earlier) |

### Modes

**`explanatory`** (default)
- Provides brief educational insights before and after writing code
- Focuses on codebase-specific patterns and conventions
- Uses the `★ Insight` block format

**`learning`**
- Interactive learning mode that requests user code contributions
- Identifies meaningful decision points (5-10 lines of code)
- Focuses on trade-offs and design choices

**`combined`**
- Combines both explanatory and learning modes
- Provides insight blocks AND requests user contributions
- Most comprehensive educational experience

## How It Works

The module uses Amplifier's hook system:

1. **Event**: Registers on `session:start`
2. **Action**: Returns `HookResult(action="inject_context", ...)`
3. **Effect**: Instructions are injected into the AI's system context

## Example Usage

With the hook enabled, the AI will automatically format educational content:

```
★ Insight ─────────────────────────────────────
This code uses the Repository pattern to abstract database access.
The benefit is testability - you can mock the repository in unit tests.
─────────────────────────────────────────────────

[AI continues with the actual code implementation]
```

## Development

```bash
# Clone
git clone https://github.com/michaeljabbour/amplifier-module-hooks-insight-blocks
cd amplifier-module-hooks-insight-blocks

# Install deps
uv sync

# Run tests
uv run pytest

# Test locally
export AMPLIFIER_MODULE_HOOKS_INSIGHT_BLOCKS=$(pwd)
amplifier run "test insight blocks"
```

## Related

- [Amplifier hooks-logging](https://github.com/microsoft/amplifier-module-hooks-logging) - Reference hook implementation
- [Amplifier Hooks API](https://github.com/microsoft/amplifier-core/blob/main/docs/HOOKS_API.md) - Hook system documentation

## License

MIT

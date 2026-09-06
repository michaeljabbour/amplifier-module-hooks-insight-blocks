# Agent Instructions

**This module is being retired. Do not add features here.**

The insight (★) callout now ships from
[`amplifier-bundle-mj`](https://github.com/michaeljabbour/amplifier-bundle-mj) as
`modules/hooks-inline-blocks`, which consolidates the insight, machete (✂), and
MJ-lens (🔪) blocks into one parametrized module. It is wired in
`behaviors/mj.yaml` as `blocks: [{use: insight}, {use: machete}, {use: mj-lens}]`,
and `behaviors/insights.yaml` mounts the insight block on its own.

## Where to work instead

| Task | Location |
|---|---|
| Change insight block text, modes, or Sage hints | `amplifier-bundle-mj/modules/hooks-inline-blocks/` |
| Change how the block is mounted or configured | `amplifier-bundle-mj/behaviors/mj.yaml` (full bench) or `behaviors/insights.yaml` (insight only) |
| Session conventions, structure, workflows | `amplifier-bundle-mj/project-context/` |

## If you are here anyway

This repo is no longer in `~/.amplifier/settings.yaml` `bundle.app` — it was removed on
2026-09-06 because its cached `bundle.md` predated the `source:` fix in `b18d670`, so
every session and subagent spawn failed to load the hook. Re-adding it would also
double-inject the insight block alongside `hooks-inline-blocks`.

Tests still run: `uv run pytest`.

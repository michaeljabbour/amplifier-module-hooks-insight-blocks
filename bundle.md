---
bundle:
  name: insight-blocks
  version: 1.0.0
  description: Educational insight blocks before/after code

hooks:
  - module: hooks-insight-blocks
    source: git+https://github.com/michaeljabbour/amplifier-module-hooks-insight-blocks@main
    config:
      mode: explanatory
      enabled: true
---

# Insight Blocks

Educational insight blocks hook that displays learning-focused insights before and after writing code.

"""Insight block extraction utilities.

Pure logic layer -- no rendering dependencies, no ANSI, no Rich.
Provides regex patterns and extraction functions for detecting
and parsing insight blocks from LLM text output.

These utilities are used by the streaming-ui module for Rich rendering,
but are also available standalone for any consumer that needs to
detect insight blocks in text.
"""

import re

# Quick-check: does the text contain an insight opening delimiter?
INSIGHT_OPEN_PATTERN = re.compile(r"★ Insight")

# Full extraction: opening delimiter line → content → closing delimiter line.
# Uses [─]{10,} to tolerate variable-length dash runs from LLMs.
INSIGHT_BLOCK_PATTERN = re.compile(
    r"`[★]?\s*★ Insight\s*[─]{10,}`\n(.+?)\n`[─]{10,}`",
    re.DOTALL,
)


def extract_insight_blocks(text: str) -> tuple[list[str], str]:
    """Extract insight blocks from text, returning (insights, remaining_text).

    Each insight is the body text between the delimiters.
    remaining_text is the original text with all insight blocks removed.

    Examples:
        >>> text = '`★ Insight ─────────────────────`\\nKey point\\n`─────────────────────────────────`'
        >>> insights, remaining = extract_insight_blocks(text)
        >>> insights
        ['Key point']
        >>> remaining
        ''
    """
    insights: list[str] = []
    remaining = text

    for match in INSIGHT_BLOCK_PATTERN.finditer(text):
        insights.append(match.group(1).strip())

    if insights:
        remaining = INSIGHT_BLOCK_PATTERN.sub("", text).strip()

    return insights, remaining

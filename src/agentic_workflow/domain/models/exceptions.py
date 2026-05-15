"""Domain Exceptions.

Traceable to: FR-034
"""

class TokenLimitExceededError(Exception):
    """Raised when an LLM response exceeds the maximum token limit."""

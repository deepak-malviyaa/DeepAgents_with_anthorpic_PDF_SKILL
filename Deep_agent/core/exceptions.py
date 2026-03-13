"""
Custom exceptions for the skill system.
"""


class SkillError(Exception):
    """Base exception for skill-related errors."""
    pass


class SkillNotFoundError(SkillError):
    """Raised when a requested skill cannot be found."""
    pass


class SkillLoadError(SkillError):
    """Raised when a skill fails to load or parse."""
    pass


class SkillExecutionError(SkillError):
    """Raised when a skill fails during execution."""
    pass


class SkillValidationError(SkillError):
    """Raised when skill metadata fails validation."""
    pass

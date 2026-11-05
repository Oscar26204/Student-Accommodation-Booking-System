"""Shared exceptions so every feature reports problems in the same way."""


class SabsError(Exception):
    """Base class for all SABS errors."""


class ValidationError(SabsError):
    """Input is missing or invalid."""


class DuplicateUserError(SabsError):
    """An account with this email already exists."""


class AuthenticationError(SabsError):
    """Email or password is wrong."""


class PermissionDenied(SabsError):
    """The user's role is not allowed to do this."""

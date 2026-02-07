"""
Custom exceptions for blockchain operations.
"""


class ChainLengthException(Exception):
    """
    Raised when attempting to replace a chain with one that is not longer.
    """
    pass


class ChainValidationException(Exception):
    """
    Raised when chain validation fails.
    """
    pass

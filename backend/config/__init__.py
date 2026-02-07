"""

Configuration package for the blockchain application.
Exports constants and environment-based configuration.
"""
from backend.config.constants import (
    NANOSECONDS,
    MICROSECONDS,
    MILLISECONDS,
    SECONDS,
    MINE_RATE,
    STARTING_BALANCE,
    MINING_REWARD,
    MINING_REWARD_INPUT,
)

from backend.config.env import AppConfig

__all__ = [
    # Time constants
    "NANOSECONDS",
    "MICROSECONDS",
    "MILLISECONDS",
    "SECONDS",
    # Blockchain constants
    "MINE_RATE",
    # Wallet constants
    "STARTING_BALANCE",
    # Mining constants
    "MINING_REWARD",
    "MINING_REWARD_INPUT",
    # Environment configuration
    "AppConfig",
]


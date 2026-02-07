"""
Environment-based configuration management.
Loads and validates environment variables for the application.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

class AppConfig:
    """
    Application configuration loaded from environment variables.
    """

    ROOT_PORT = int(os.environ.get("ROOT_PORT", "5050"))
    ROOT_HOST = os.environ.get("ROOT_HOST", "localhost")
    IS_PEER = os.environ.get("PEER") == "True"
    POLL_ROOT = os.environ.get("POLL_ROOT") == "True"
    POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "15"))
    SEED_DATA = os.environ.get("SEED_DATA") == "True"
    
    @classmethod
    def get_port(cls):
        """
        Get the port for this instance.
        Peers get a random port, root gets ROOT_PORT.
        """
        if cls.IS_PEER:
            import random
            return random.randint(5051, 6000)
        return cls.ROOT_PORT
    
    @classmethod
    def to_dict(cls):
        """Return configuration as a dictionary for debugging."""
        return {
            "ROOT_PORT": cls.ROOT_PORT,
            "ROOT_HOST": cls.ROOT_HOST,
            "IS_PEER": cls.IS_PEER,
            "POLL_ROOT": cls.POLL_ROOT,
            "POLL_INTERVAL": cls.POLL_INTERVAL,
            "SEED_DATA": cls.SEED_DATA,
        }


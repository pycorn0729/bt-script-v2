import os
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from app.constants import ROUND_TABLE_HOTKEY

# Load environment variables from .env file
load_dotenv()


class Settings(BaseModel):
    VERSION: str = "0.1.0"
    NETWORK: str = "wss://entrypoint-finney.opentensor.ai:443"
    # WALLET_NAMES: List[str] = []
    # DELEGATORS: List[str] = []
    DEFAULT_RATE_TOLERANCE: float = 0.005
    DEFAULT_MIN_TOLERANCE: bool = False
    DEFAULT_RETRIES: int = 1
    DEFAULT_DEST_HOTKEY: str = ROUND_TABLE_HOTKEY
    
    # Load wallet names from environment variable, fallback to default
    WALLET_NAMES: List[str] = os.getenv("WALLET_NAMES", "").split(",")
    
    # Load delegators from environment variable, fallback to default
    DELEGATORS: List[str] = os.getenv("DELEGATORS", "").split(",")

settings = Settings()
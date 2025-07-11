import os
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from app.constants import ROUND_TABLE_HOTKEY

# Load environment variables from .env file
load_dotenv(".env")


class Settings(BaseModel):
    VERSION: str = "0.1.0"
    NETWORK: str = "wss://entrypoint-finney.opentensor.ai:443"
    # WALLET_NAMES: List[str] = []
    # DELEGATORS: List[str] = []
    DEFAULT_RATE_TOLERANCE: float = 0.005
    DEFAULT_MIN_TOLERANCE: bool = False
    DEFAULT_RETRIES: int = 1
    DEFAULT_DEST_HOTKEY: str = ROUND_TABLE_HOTKEY
    
    # WALLET_NAMES: List[str] = os.getenv("WALLET_NAMES", "").split(",")
    # DELEGATORS: List[str] = os.getenv("DELEGATORS", "").split(",")
    WALLET_NAMES: List[str] = ["black", "green"]
    DELEGATORS: List[str] = ["5F5WLLEzDBXQDdTzDYgbQ3d3JKbM15HhPdFuLMmuzcUW5xG2","5HX2u5S2uEgPxKejfF8UzEYkRcRS2xqADnk8P41c2gM6UQg3"]
    
    ADMIN_HASH: str = os.getenv("ADMIN_HASH", "")

settings = Settings()

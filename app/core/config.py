from pydantic import BaseModel
from typing import List
from app.constants import ROUND_TABLE_HOTKEY


class Settings(BaseModel):
    VERSION: str = "0.1.0"
    NETWORK: str = "finney"
    WALLET_NAMES: List[str] = []
    DELEGATORS: List[str] = []
    DEFAULT_RATE_TOLERANCE: float = 0.005
    DEFAULT_MIN_TOLERANCE: bool = False
    DEFAULT_RETRIES: int = 1
    DEFAULT_DEST_HOTKEY: str = ROUND_TABLE_HOTKEY
    
    # WALLET_NAMES: List[str] = ["black", "white"]
    # DELEGATORS: List[str] = ["5F5WLLEzDBXQDdTzDYgbQ3d3JKbM15HhPdFuLMmuzcUW5xG2", "5F99Qc6hZ67Jd6fW9jXgD3h9Jg4K5pQ9jXgD3h9Jg4K5p"]

settings = Settings()
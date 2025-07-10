from pydantic import BaseModel
from typing import List


class Settings(BaseModel):
    VERSION: str = "0.1.0"
    NETWORK: str = "finney"
    WALLET_NAMES: List[str] = ["black", "white"]
    DELEGATORS: List[str] = ["5F5WLLEzDBXQDdTzDYgbQ3d3JKbM15HhPdFuLMmuzcUW5xG2", "5F99Qc6hZ67Jd6fW9jXgD3h9Jg4K5pQ9jXgD3h9Jg4K5p"]


settings = Settings()
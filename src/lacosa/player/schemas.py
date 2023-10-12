from pydantic import BaseModel
from typing import List
from schemas.schemas import CardInfo

class PlayerResponse(BaseModel):
    hand: List[CardInfo]
    role: str
    is_alive: bool

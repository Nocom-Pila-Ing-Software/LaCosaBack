from pydantic import BaseModel
from typing import List

class PlayerName(BaseModel):
    playerName: str

class PlayerID(BaseModel):
    playerID: int

from pydantic import BaseModel
from typing import List


class PlayerName(BaseModel):
    playerName: str


class PlayerID(BaseModel):
    playerID: int


class CardID(BaseModel):
    cardID: int


class CardData(BaseModel):
    id: int
    name: str
    description: str


class PlayerResponse(BaseModel):
    hand: List[CardData]
    role: str
    is_alive: bool

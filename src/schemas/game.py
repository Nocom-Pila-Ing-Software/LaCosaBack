from pydantic import BaseModel
from typing import List


class PlayerID(BaseModel):
    playerID: int


class GameID(BaseModel):
    gameID: int


class GameCreationRequest(BaseModel):
    roomID: int
    players: List[PlayerID]

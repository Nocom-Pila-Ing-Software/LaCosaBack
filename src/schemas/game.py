from pydantic import BaseModel
from typing import List


class PlayerID(BaseModel):
    playerID: int


class GameID(BaseModel):
    gameID: int


class GameCreationRequest(BaseModel):
    roomID: int
    players: List[PlayerID]


class CardInfo(BaseModel):
    cardID: int
    name: str
    description: str


class PublicPlayerInfo(BaseModel):
    playerID: int
    username: str
    is_host: bool
    is_alive: bool


class GameStatus(BaseModel):
    gameID: int
    players: List[PublicPlayerInfo]
    lastPlayedCard: CardInfo

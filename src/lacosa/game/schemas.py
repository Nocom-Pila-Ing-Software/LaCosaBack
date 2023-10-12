from pydantic import BaseModel
from typing import List
from schemas.schemas import PlayerID, CardInfo

class GameCreationRequest(BaseModel):
    roomID: int


class PlayCardRequest(BaseModel):
    playerID: int
    targetPlayerID: int
    cardID: int


class PublicPlayerInfo(BaseModel):
    playerID: int
    username: str
    is_host: bool
    is_alive: bool


class GameStatus(BaseModel):
    gameID: int
    playerPlayingTurn: PlayerID
    players: List[PublicPlayerInfo]
    deadPlayers: List[PublicPlayerInfo]
    lastPlayedCard: CardInfo
    isGameOver: bool

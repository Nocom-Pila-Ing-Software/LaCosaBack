from enum import Enum
from pydantic import BaseModel
from typing import List
from lacosa.schemas import PlayerID, CardInfo


class Actions(str, Enum):
    draw = "draw"
    action = "action"
    defense = "defense"
    trade = "trade"


class EventTypes(str, Enum):
    action = "action"
    trade = "trade"


class GameCreationRequest(BaseModel):
    roomID: int



class GenericCardRequest(BaseModel):
    playerID: int
    cardID: int


class PlayCardRequest(BaseModel):
    playerID: int
    targetPlayerID: int
    cardID: int


class PublicPlayerInfo(BaseModel):
    playerID: int
    username: str
    is_host: bool
    is_alive: bool


class GameEvent(BaseModel):
    eventID: int
    type: EventTypes
    player: PublicPlayerInfo
    targetPlayer: PublicPlayerInfo | None
    card: CardInfo
    defenseCard: CardInfo | None
    isCompleted: bool
    isSuccessful: bool


class GameResult(BaseModel):
    isGameOver: bool
    humansWin: bool
    winners: List[PublicPlayerInfo]


class GameStatus(BaseModel):
    gameID: int
    playerPlayingTurn: PlayerID
    currentAction: Actions
    players: List[PublicPlayerInfo]
    deadPlayers: List[PublicPlayerInfo]
    lastPlayedCard: CardInfo
    result: GameResult
    events: List[GameEvent]

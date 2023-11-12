from enum import Enum
from pydantic import BaseModel
from typing import List
from lacosa.schemas import PlayerID, CardInfo


class Action(str, Enum):
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


class ShowCardsRequest(BaseModel):
    playerID: int
    cards: List[CardInfo]


class PublicPlayerInfo(BaseModel):
    playerID: int
    username: str
    is_host: bool
    is_alive: bool


class GameEvent(BaseModel):
    """Represents an event that occurred during the game"""
    eventID: int
    type: EventTypes
    player1: PublicPlayerInfo
    player2: PublicPlayerInfo | None
    card1: CardInfo
    card2: CardInfo | None
    isCompleted: bool
    isSuccessful: bool


class EventCreationRequest(BaseModel):
    gameID: int
    playerID: int
    targetPlayerID: int
    cardID: int | None
    targetCardID: int | None
    type: EventTypes
    isCompleted: bool
    isSuccessful: bool


class GameResult(BaseModel):
    isGameOver: bool
    humansWin: bool
    winners: List[PublicPlayerInfo]


class GameStatus(BaseModel):
    gameID: int
    playerPlayingTurn: PlayerID
    currentAction: Action
    players: List[PublicPlayerInfo]
    deadPlayers: List[PublicPlayerInfo]
    lastPlayedCard: CardInfo
    result: GameResult
    events: List[str]

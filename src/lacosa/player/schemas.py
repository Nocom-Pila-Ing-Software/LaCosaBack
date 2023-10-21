from pydantic import BaseModel
from typing import List
from lacosa.schemas import CardInfo

class PlayerResponse(BaseModel):
    """Represents a player in the game (all the info that is private only to the player)"""
    hand: List[CardInfo]
    role: str
    is_alive: bool


class UsabilityActionInfoCard(BaseModel):
    """Represents a card in the player's hand with additional info about its usability during the action phase of the turn"""
    cardID: int
    name: str
    description: str
    playable: bool
    discardable: bool


class UsabilityActionResponse(BaseModel):
    """Represents the usability of all the cards in the player's hand during the action phase of the turn"""
    cards: List[UsabilityActionInfoCard]

class UsabilityInfoCard(BaseModel):
    """Represents a card in the player's hand with additional info about its usability during the defense/trade phase of the turn"""
    cardID: int
    name: str
    description: str
    usable: bool

class UsabilityResponse(BaseModel):
    """Represents the usability of all the cards in the player's hand during the defense/trade phase of the turn"""
    cards: List[UsabilityInfoCard]

class TargetsInfo(BaseModel):
    """Represents a player that can be targeted by a card"""
    playerID: int
    name: str

class TargetsResponse(BaseModel):
    """Represents the targets that can be targeted by a card"""
    targets: List[TargetsInfo]

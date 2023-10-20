from pydantic import BaseModel
from typing import List
from lacosa.schemas import CardInfo

class PlayerResponse(BaseModel):
    hand: List[CardInfo]
    role: str
    is_alive: bool


class UsabilityActionInfoCard(BaseModel):
    cardID: int
    name: str
    description: str
    playable: bool
    discardable: bool


class UsabilityActionResponse(BaseModel):
    cards: List[UsabilityActionInfoCard]

class UsabilityInfoCard(BaseModel):
    cardID: int
    name: str
    description: str
    usable: bool

class UsabilityResponse(BaseModel):
    cards: List[UsabilityInfoCard]

class TargetsInfo(BaseModel):
    playerID: int
    name: str

class TargetsResponse(BaseModel):
    targets: List[TargetsInfo]

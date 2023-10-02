from pydantic import BaseModel


class PlayerID(BaseModel):
    playerID: int


class CardID(BaseModel):
    cardID: int


class CardData(BaseModel):
    id: int
    name: str
    description: str


class PlayerResponse(BaseModel):
    hand: list[CardData]
    role: str
    is_alive: bool


class PlayerName(BaseModel):
    playerName: str

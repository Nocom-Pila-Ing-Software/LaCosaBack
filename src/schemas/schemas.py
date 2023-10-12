from pydantic import BaseModel

class RoomID(BaseModel):
    roomID: int

class RoomName(BaseModel):
    roomName: str

class PlayerID(BaseModel):
    playerID: int

class PlayerName(BaseModel):
    playerName: str

class GameID(BaseModel):
    gameID: int

class CardID(BaseModel):
    cardID: int

class CardInfo(BaseModel):
    cardID: int
    name: str
    description: str
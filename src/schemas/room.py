from pydantic import BaseModel
from typing import List


class RoomName(BaseModel):
    roomName: str


class PlayerName(BaseModel):
    playerName: str


class RoomID(BaseModel):
    roomID: int


class PlayerID(BaseModel):
    playerID: int


class RoomCreationRequest(BaseModel):
    roomName: str
    hostName: str


class RoomCreationResponse(BaseModel):
    roomID: int
    playerID: int


class RoomDataResponse(BaseModel):
    CountPlayers: int
    Players: List[PlayerName]

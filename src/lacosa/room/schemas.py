from pydantic import BaseModel
from typing import List
from lacosa.schemas import PlayerName

class RoomCreationRequest(BaseModel):
    roomName: str
    hostName: str


class RoomCreationResponse(BaseModel):
    roomID: int
    playerID: int


class RoomDataResponse(BaseModel):
    CountPlayers: int
    Players: List[PlayerName]
    hasStarted: bool

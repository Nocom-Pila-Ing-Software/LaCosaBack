from pydantic import BaseModel
from typing import List
from lacosa.schemas import PlayerName


class RoomCreationRequest(BaseModel):
    roomName: str
    hostName: str
    minPlayers: int
    maxPlayers: int


class RoomAddPlayerRequest(BaseModel):
    playerName: str


class RoomCreationResponse(BaseModel):
    roomID: int
    playerID: int


class RoomDataResponse(BaseModel):
    CountPlayers: int
    Players: List[PlayerName]
    hasStarted: bool
    minPlayers: int
    maxPlayers: int


class RoomListing(BaseModel):
    id: int
    name: str
    playerAmount: int
    minPlayers: int
    maxPlayers: int


class RoomListingList(BaseModel):
    rooms: List[RoomListing]

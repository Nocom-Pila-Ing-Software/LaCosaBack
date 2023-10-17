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


class RoomListing(BaseModel):
    id: int
    name: str
    player_amount: int
    min_players: int
    max_players: int


class RoomListingList(BaseModel):
    rooms: List[RoomListing]

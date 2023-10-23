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


# FIXME move this to another place
# I didn't use playerID or playerName because we should change those in the future.
# Also, it produces stuttering in the code.
# For example, player.playerName instead of just doing player.name
class PlayerSchema(BaseModel):
    id: int
    name: str


class RoomDataResponse(BaseModel):
    CountPlayers: int
    Players: List[PlayerName]
    hasStarted: bool
    minPlayers: int
    maxPlayers: int
    host: PlayerSchema


class RoomListing(BaseModel):
    id: int
    name: str
    playerAmount: int
    minPlayers: int
    maxPlayers: int


class RoomListingList(BaseModel):
    rooms: List[RoomListing]

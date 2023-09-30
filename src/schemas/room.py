from pydantic import BaseModel


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

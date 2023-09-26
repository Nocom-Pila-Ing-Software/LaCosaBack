from pydantic import BaseModel
from typing import List


class PlayerID(BaseModel):
    playerID: int


class RoomID(BaseModel):
    roomID: int
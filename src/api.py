"""Defines the API.
If you create a new router add it here."""

from fastapi import APIRouter
from game.router import game_router
from room.router import room_router
from routers.player import player_router

api_router = APIRouter()
api_router.include_router(game_router, prefix="/game", tags=["game"])
api_router.include_router(room_router, prefix="/room", tags=["room"])
api_router.include_router(player_router, prefix="/player", tags=["player"])
# api_router.include_router(
#    contacts_router, prefix="/contacts", tags=["contacts"]
# )
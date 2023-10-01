"""Defines the API.
If you create a new router add it here."""

from fastapi import APIRouter
from routers.game import game_router
from routers.room import room_router

api_router = APIRouter()
api_router.include_router(game_router, prefix="/game")
api_router.include_router(room_router, prefix="/room")
# api_router.include_router(
#    contacts_router, prefix="/contacts", tags=["contacts"]
# )

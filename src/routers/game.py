"""Defines 'game' endpoints
"""

from fastapi import APIRouter, status
from schemas.game import GameCreationRequest, GameID
from pony.orm import db_session
from models import Game, Card

game_router = APIRouter()


@game_router.post(path="", status_code=status.HTTP_201_CREATED)
async def create_game(creation_request: GameCreationRequest) -> GameID:
    res = GameID(gameID=1)
    with db_session:
        pass
        # TODO: create game deck
        # TODO: create Game on DB
        # TODO: assign player roles
        # TODO: assign cards to players
    return res

"""Defines 'game' endpoints
"""

from fastapi import APIRouter, status
from schemas.game import GameCreationRequest, GameID
from pony.orm import db_session
from services.game import (
    create_game_on_db, create_deck,
    assign_thing_role, deal_cards_to_thing, deal_cards_to_players,
    handle_errors
)

game_router = APIRouter()


@game_router.post(path="", status_code=status.HTTP_201_CREATED)
async def create_game(creation_request: GameCreationRequest) -> GameID:
    with db_session:
        handle_errors(creation_request)
        game = create_game_on_db(creation_request)
        create_deck(game)
        the_thing = assign_thing_role(game)
        deal_cards_to_thing(the_thing)
        deal_cards_to_players(game)
        response = GameID(gameID=game.id)

    return response

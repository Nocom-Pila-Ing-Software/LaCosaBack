"""Defines 'game' endpoints
"""

from fastapi import APIRouter, status
from schemas.game import GameCreationRequest, GameID
from pony.orm import db_session
import services.game_creator as game_creator

game_router = APIRouter()


@game_router.post(path="", status_code=status.HTTP_201_CREATED)
async def create_game(creation_request: GameCreationRequest) -> GameID:
    with db_session:
        game_creator.handle_errors(creation_request)
        game = game_creator.create_game_on_db(creation_request)
        game_creator.create_deck(game)
        the_thing = game_creator.assign_thing_role(game)
        game_creator.deal_cards_to_thing(the_thing)
        game_creator.deal_cards_to_players(game)
        response = GameID(gameID=game.id)

    return response

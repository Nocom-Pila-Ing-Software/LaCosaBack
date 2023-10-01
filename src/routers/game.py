"""Defines 'game' endpoints
"""

from fastapi import APIRouter, status
from schemas.game import GameCreationRequest, GameID, PlayerID
from pony.orm import db_session
import services.game_creator as game_creator
import services.game_draw_card as game_draw_card

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

@game_router.put(path="/{game_id}/deal-card", status_code=status.HTTP_200_OK)
async def draw_card(game_id: int, player_id: PlayerID) -> None:
    with db_session:
        game_draw_card.check_pre_conditions_draw_cards(game_id, player_id)
        game_draw_card.draw_card(game_id, player_id)
        response = None
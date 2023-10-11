"""Defines 'game' endpoints
"""

from fastapi import APIRouter, status
from pony.orm import db_session
from lacosa.game.schemas import GameCreationRequest, GameStatus, PlayCardRequest
from schemas.schemas import PlayerID, GameID
from lacosa.game.utils.game_creator import GameCreator
from .utils.deck import Deck
from lacosa.game.utils.game_status import GameStatusHandler
from lacosa.game.utils.game_actions import CardHandler

game_router = APIRouter()


@game_router.post(path="", status_code=status.HTTP_201_CREATED)
async def create_game(creation_request: GameCreationRequest) -> GameID:
    with db_session:
        game_creator = GameCreator(creation_request)
        game_creator.create()
        response = game_creator.get_response()

    return response


@game_router.put(path="/{room_id}/deal-card", status_code=status.HTTP_200_OK)
async def draw_card(room_id: int, player_id: PlayerID) -> None:
    with db_session:
        Deck.draw_card(room_id, player_id.playerID)


@game_router.get(path="/{room_id}", status_code=status.HTTP_200_OK)
async def get_game_info(room_id) -> GameStatus:
    with db_session:
        status_handler = GameStatusHandler(room_id)
        response = status_handler.get_response()

    return response


@game_router.put(path="/{room_id}/play-card", status_code=status.HTTP_200_OK)
async def play_card(play_request: PlayCardRequest, room_id: int) -> None:
    with db_session:
        card_handler = CardHandler(play_request, room_id)
        card_handler.play_card()

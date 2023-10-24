"""Defines 'game' endpoints
"""

from fastapi import APIRouter, status
from lacosa import utils
from pony.orm import db_session
from pony.orm import db_session
from lacosa.game.schemas import GameCreationRequest, GameStatus, GenericCardRequest, PlayCardRequest
from lacosa.schemas import PlayerID, GameID
from lacosa.game.utils.game_creator import GameCreator
from .utils.deck import Deck
from lacosa.game.utils.game_status import GameStatusHandler
from lacosa.game.utils.game_actions import CardDefender, CardPlayer, CardTrader
from lacosa.game.utils.game_actions import CardPlayer
from lacosa.game.utils.discard_card import discard_card_util
from lacosa.game.utils.error_responses import error_responses
from lacosa.game.utils.game_ender import end_game_if_conditions_are_met

game_router = APIRouter()


@game_router.get(path="/{room_id}", status_code=status.HTTP_200_OK,
                 responses=error_responses["404"])
async def get_game_info(room_id) -> GameStatus:
    """Returns the current status/information of the game"""
    with db_session:
        status_handler = GameStatusHandler(room_id)
        end_game_if_conditions_are_met(status_handler.game)
        response = status_handler.get_response()

    return response


@game_router.post(path="", status_code=status.HTTP_201_CREATED,
                  responses=error_responses["400&403"])
async def create_game(creation_request: GameCreationRequest) -> GameID:
    """Creates a new game"""
    with db_session:
        game_creator = GameCreator(creation_request)
        game_creator.create()
        response = game_creator.get_response()

    return response


@game_router.put(path="/{room_id}/deal-card", status_code=status.HTTP_200_OK,
                 responses=error_responses["400&403&404"])
async def draw_card(room_id: int, player_id: PlayerID) -> None:
    """Deals a card to a player"""
    with db_session:
        Deck.draw_card(room_id, player_id.playerID)
        game = utils.find_game(room_id)
        game.current_action = "action"


@game_router.put(path="/{room_id}/discard-card", status_code=status.HTTP_200_OK,
                 responses=error_responses["400&403&404"])
async def discard_card(discard_request: GenericCardRequest, room_id: int) -> None:
    """Discards a card from a player's hand"""
    with db_session:
        discard_card_util(discard_request, room_id)



@game_router.put(path="/{room_id}/play-card", status_code=status.HTTP_200_OK,
                 responses=error_responses["400&403&404"])
async def play_card(play_request: PlayCardRequest, room_id: int) -> None:
    """
    Try to play a card from a player's hand

    The effect of the card may not apply if the target player plays a defense card
    """
    with db_session:
        card_handler = CardPlayer(play_request, room_id)
        card_handler.execute_action()


@game_router.put(path="/{room_id}/defend-card", status_code=status.HTTP_200_OK,
                 responses=error_responses["400&403&404"])
async def defend_card(defend_request: GenericCardRequest, room_id: int) -> None:
    """
    Use a defense card to prevent the effect of an attack card

    If the defense card id is -1, the player is not using a defense card
    """
    with db_session:
        defend_handler = CardDefender(defend_request, room_id)
        defend_handler.execute_action()


@game_router.put(path="/{room_id}/trade-card", status_code=status.HTTP_200_OK,
                 responses=error_responses["400&403&404"])
async def trade_card(trade_request: GenericCardRequest, room_id: int) -> None:
    """Trade a card with another player"""
    with db_session:
        trade_handler = CardTrader(trade_request, room_id)
        trade_handler.execute_action()

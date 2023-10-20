from fastapi import APIRouter, status
from lacosa.player.schemas import PlayerResponse, UsabilityResponse, UsabilityActionResponse, TargetsResponse
from pony.orm import db_session
import lacosa.player.utils.player_status as player_stat

player_router = APIRouter()


@player_router.get(path="/{player_id}", status_code=status.HTTP_200_OK,
                   responses={status.HTTP_404_NOT_FOUND: {"description": "Player not found"},
                              status.HTTP_403_FORBIDDEN: {"description": "Player is not in a game"}})
async def get_player_info(player_id: int) -> PlayerResponse:
    with db_session:
        response = player_stat.get_player_info(player_id)
    return response


@player_router.get(path="/{player_id}/cards-usability", status_code=status.HTTP_200_OK,
                   responses={status.HTTP_404_NOT_FOUND: {"description": "Player not found"},
                              status.HTTP_403_FORBIDDEN: {"description": "Player is not in a game"}})
async def get_cards_usability(player_id: int) -> UsabilityActionResponse:
    """Returns the information of which cards can be played or discarded by the player"""
    with db_session:
        pass


@player_router.get(path="/{player_id}/targets/{card_id}", status_code=status.HTTP_200_OK,
                   responses={status.HTTP_404_NOT_FOUND: {"description": "Player not found"},
                              status.HTTP_403_FORBIDDEN: {"description": "Player is not in a game"},
                              status.HTTP_400_BAD_REQUEST: {"description": "Player does not have the card"}})
async def get_possible_targets(player_id: int, card_id: int) -> TargetsResponse:
    """Returns the information of which players can be targeted/attacked with the card"""
    with db_session:
        pass


@player_router.get(path="/{player_id}/cards-defend/{card_id}", status_code=status.HTTP_200_OK,
                   responses={status.HTTP_404_NOT_FOUND: {"description": "Player not found"},
                              status.HTTP_403_FORBIDDEN: {"description": "Player is not in a game"},
                              status.HTTP_400_BAD_REQUEST: {"description": "Player does not have the card"}})
async def get_cards_defend(player_id: int, card_id: int) -> UsabilityResponse:
    """Returns the information of which cards can be used to defend against the card played by the attacker"""
    with db_session:
        pass


@player_router.get(path="/{player_id}/cards-trade", status_code=status.HTTP_200_OK,
                        responses={status.HTTP_404_NOT_FOUND: {"description": "Player not found"},
                                   status.HTTP_403_FORBIDDEN: {"description": "Player is not in a game"}})
async def get_cards_trade(player_id: int) -> UsabilityResponse:
    """Returns the information of which cards can be traded with the player"""
    with db_session:
        pass

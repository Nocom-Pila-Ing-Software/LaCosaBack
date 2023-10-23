from fastapi import APIRouter, status
from lacosa.player.schemas import PlayerResponse, UsabilityResponse, UsabilityActionResponse, TargetsResponse
from pony.orm import db_session
import lacosa.player.utils.player_status as player_stat
from lacosa.player.utils.error_responses import error_responses
from lacosa.game.utils import card_info

player_router = APIRouter()


@player_router.get(path="/{player_id}", status_code=status.HTTP_200_OK,
                   responses=error_responses["403&404"])
async def get_player_info(player_id: int) -> PlayerResponse:
    with db_session:
        response = player_stat.get_player_info(player_id)
    return response


@player_router.get(path="/{player_id}/cards-usability", status_code=status.HTTP_200_OK,
                   responses=error_responses["403&404"])
async def get_cards_usability(player_id: int) -> UsabilityActionResponse:
    """Returns the information of which cards can be played or discarded by the player"""
    with db_session:
        card_usability_handler = card_info.CardUsabilityInformer(player_id)
        response = card_usability_handler.get_response()
    return response



@player_router.get(path="/{player_id}/targets/{card_id}", status_code=status.HTTP_200_OK,
                   responses=error_responses["400&403&404"])
async def get_possible_targets(player_id: int, card_id: int) -> TargetsResponse:
    """Returns the information of which players can be targeted/attacked with the card"""
    with db_session:
        card_targets_handler = card_info.CardTargetsInformer(player_id, card_id)
        response = card_targets_handler.get_response()
    return response


@player_router.get(path="/{player_id}/cards-defend/{card_id}", status_code=status.HTTP_200_OK,
                   responses=error_responses["400&403&404"])
async def get_cards_defend(player_id: int, card_id: int) -> UsabilityResponse:
    """Returns the information of which cards can be used to defend against the card played by the attacker"""
    with db_session:
        card_defense_info_handler = card_info.CardDefenseInformer(player_id, card_id)
        response = card_defense_info_handler.get_response()
    return response


@player_router.get(path="/{player_id}/cards-trade", status_code=status.HTTP_200_OK,
                        responses=error_responses["403&404"])
async def get_cards_trade(player_id: int) -> UsabilityResponse:
    """Returns the information of which cards can be traded with the player"""
    with db_session:
        card_trade_info_handler = card_info.CardTradeInformer(player_id)
        response = card_trade_info_handler.get_response()
    return response

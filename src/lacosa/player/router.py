from fastapi import APIRouter, status
from lacosa.player.schemas import PlayerResponse, UsabilityResponse, UsabilityActionResponse, TargetsResponse
from pony.orm import db_session
import lacosa.player.utils.player_status as player_stat
from lacosa.player.utils.error_responses import error_responses
from lacosa.game.utils.card.playability_informer import CardUsabilityInformer
from lacosa.game.utils.card.defense_informer import CardDefenseInformer
from lacosa.game.utils.card.targets_informer import CardTargetsInformer
from lacosa.game.utils.card.trade_informer import CardTradeInformer

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
        card_usability_handler = CardUsabilityInformer(player_id)
        response = card_usability_handler.get_response()
    return response


@player_router.get(path="/{player_id}/targets/{card_id}", status_code=status.HTTP_200_OK,
                   responses=error_responses["400&403&404"])
async def get_possible_targets(player_id: int, card_id: int) -> TargetsResponse:
    """Returns the information of which players can be targeted/attacked with the card"""
    with db_session:
        card_targets_handler = CardTargetsInformer(
            player_id, card_id)
        response = card_targets_handler.get_response()
    return response


@player_router.get(path="/{player_id}/cards-defend/{card_id}", status_code=status.HTTP_200_OK,
                   responses=error_responses["400&403&404"])
async def get_cards_defend(player_id: int, card_id: int) -> UsabilityResponse:
    """Returns the information of which cards can be used to defend against the card played by the attacker

    Use -1 as card_id to get the information of which cards can be used to defend against a trade"""
    with db_session:
        card_defense_info_handler = CardDefenseInformer(
            player_id, card_id)
        response = card_defense_info_handler.get_response()
    return response


@player_router.get(path="/{player_id}/cards-trade", status_code=status.HTTP_200_OK,
                        responses=error_responses["403&404"])
async def get_cards_trade(player_id: int) -> UsabilityResponse:
    """Returns the information of which cards can be traded with the player"""
    with db_session:
        card_trade_info_handler = CardTradeInformer(player_id)
        response = card_trade_info_handler.get_response()
    return response

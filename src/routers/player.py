from fastapi import APIRouter, status
from schemas.player import PlayerResponse
from pony.orm import db_session
import services.player_status as player_stat

player_router = APIRouter()

@player_router.get(path="/{player_id}", status_code=status.HTTP_200_OK)
async def get_player_info(player_id : int) -> PlayerResponse:
    with db_session:
        response = player_stat.get_player_info(player_id)
    return response
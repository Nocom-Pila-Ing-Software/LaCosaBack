from fastapi import HTTPException
from pony.orm import select
from models import Game
from schemas.game import GameStatus, PublicPlayerInfo, CardInfo


def handle_errors(game: Game) -> None:
    """
    Checks for errors in creation_request and raises HTTPException if needed

    Args:
    creation_request (GameCreationRequest): Input data to validate

    Raises:
    HTTPException(status_code=404): If the room ID doesn't exist in database
    """
    if game is None:
        raise HTTPException(
            status_code=404, detail="Game ID doesn't exist"
        )


def get_response(game: Game) -> None:
    players = []
    last_card = CardInfo(
        cardID=game.last_played_card.id,
        name=game.last_played_card.name,
        description=game.last_played_card.description,
    )
    for player in game.players.sort_by(lambda x: x.id):
        player_info = PublicPlayerInfo(
            playerID=player.id,
            username=player.username,
            is_host=player.is_host,
            is_alive=player.is_alive
        )
        players.append(player_info)

    response = GameStatus(
        gameID=game.id,
        players=players,
        lastPlayedCard=last_card,
    )
    return response

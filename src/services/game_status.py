from fastapi import HTTPException
from models import Game, Player
from schemas.game import GameStatus, PublicPlayerInfo, CardInfo, PlayerID


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
    last_card = CardInfo(cardID=-1, name="", description="")
    if game.last_played_card:
        last_card = CardInfo(
            cardID=game.last_played_card.id,
            name=game.last_played_card.name,
            description=game.last_played_card.description,
        )
    
    # ordenar por player.position de menor a mayor
    for player in game.players.order_by(Player.position):
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
        playerPlayingTurn=PlayerID(playerID=game.current_player)
    )
    return response

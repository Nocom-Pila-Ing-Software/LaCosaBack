from models import Game, WaitingRoom, Player, Card, db
from pony.orm import db_session
from schemas.game import PublicPlayerInfo, CardInfo, GameStatus, PlayerID
import pytest
from typing import List, Dict


@pytest.fixture(scope="module")
def db_game_creation():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()

    with db_session:
        # Create a waiting room with players for testing
        room = WaitingRoom(id=0, room_name="Test room")
        room.players.create(username="Player1")
        room.players.create(username="Player2")


def get_player_data() -> List[Dict]:
    player_data = [
        {"username": "pepito", "is_host": True, "is_alive": True},
        {"username": "fulanito", "is_host": False, "is_alive": True},
        {"username": "menganito", "is_host": False, "is_alive": False}
    ]
    return player_data


@db_session
def setup_db_game_status(game_data: Dict) -> None:
    room1 = WaitingRoom(room_name="test room")

    db_players = [
        Player(id=index, room=room1, **player_data)
        for index, player_data in enumerate(game_data["players"], start=1)
    ]
    card = Card(id=1, **game_data["card"])
    # Create a Game instance
    Game(
        id=game_data["game_id"], waiting_room=room1, players=db_players,
        last_played_card=card
    )


def get_game_status_response(game_data: Dict) -> GameStatus:
    schema_players = [
        PublicPlayerInfo(playerID=index, **player_data)
        for index, player_data in enumerate(game_data["players"], start=1)
    ]
    card = CardInfo(cardID=1, **game_data["card"])
    # Create a Game instance
    response = GameStatus(
        gameID=game_data["game_id"], players=schema_players,
        lastPlayedCard=card,
        playerPlayingTurn=PlayerID(playerID=0)
    )
    return response


@pytest.fixture(scope="module")
def db_game_status():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()

    game_data = {
        "players": get_player_data(),
        "card": {"name": "Lanzallamas", "description": "está que arde"},
        "game_id": 1
    }

    setup_db_game_status(game_data)
    response = get_game_status_response(game_data)
    return response

from main import app
from fastapi.testclient import TestClient
from models import Game, WaitingRoom, Player, Card, db
from pony.orm import db_session, select
from schemas.game import GameCreationRequest, PlayerID, GameID, PublicPlayerInfo, CardInfo, GameStatus
import pytest

client = TestClient(app)


@pytest.fixture(scope="module")
def db_game_creation():
    with db_session:
        # Create a waiting room with players for testing
        room = WaitingRoom(id=0, room_name="Test room")
        room.players.create(username="Player1")
        room.players.create(username="Player2")


@pytest.fixture(scope="module")
def db_game_status():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()

    player1_data = {"username": "pepito",
                    "is_host": True, "is_alive": True}
    player2_data = {"username": "fulanito",
                    "is_host": False, "is_alive": True}
    player3_data = {"username": "menganito",
                    "is_host": False, "is_alive": False}

    card_data = {"name": "Lanzallamas",
                 "description": "está que arde"}
    game_id = 1
    with db_session:
        room1 = WaitingRoom(room_name="test room")
        player1 = Player(id=1, room=room1, **player1_data)
        player2 = Player(id=2, room=room1, **player2_data)
        player3 = Player(id=3, room=room1, **player3_data)
        card = Card(id=1, **card_data)
        # Create a Game instance
        Game(
            id=game_id, waiting_room=room1, players=[
                player1, player2, player3],
            last_played_card=card
        )

    player1 = PublicPlayerInfo(playerID=1, **player1_data)
    player2 = PublicPlayerInfo(playerID=2, **player2_data)
    player3 = PublicPlayerInfo(playerID=3, **player3_data)

    card = CardInfo(cardID=1, **card_data)
    # Create a Game instance
    response = GameStatus(
        gameID=game_id, players=[
            player1, player2, player3],
        lastPlayedCard=card
    )
    return response


def test_create_game_success(db_game_creation):
    mock_creation_request = GameCreationRequest(
        roomID=0,
        players=[
            PlayerID(playerID=1),
            PlayerID(playerID=2),
        ]
    ).model_dump()

    creation_response = GameID(gameID=1).model_dump()

    response = client.post("/game", json=mock_creation_request)
    data = response.json()

    with db_session:
        game_record = select(g for g in Game if g.id ==
                             int(data["gameID"])).get()
        the_thing = select(p for p in game_record.players if p.role == "thing")
        current_players = list(select(
            p for p in game_record.players if p.role == "thing"
        ))

        # Game was created
        assert game_record is not None

        # Deck was created
        assert len(game_record.cards) > 0

        # Players were created
        assert len(game_record.players) > 0

        # The thing role was assigned
        assert the_thing.exists()

        # The thing has 'La Cosa' card
        assert (
            the_thing.get().cards
            .select(lambda c: c.name == "La Cosa")
            .exists()
        )

        # all players have 4 cards
        assert all(p.cards.count() == 4 for p in current_players)

    assert response.status_code == 201
    assert data == creation_response


def test_invalid_room_id(db_game_creation):
    mock_creation_request = GameCreationRequest(
        roomID=666,
        players=[
            PlayerID(playerID=1),
            PlayerID(playerID=2),
        ]
    ).model_dump()
    response = client.post("/game", json=mock_creation_request)
    assert response.status_code == 404
    assert response.json() == {"detail": "Room ID doesn't exist"}


def test_invalid_player_id(db_game_creation):
    mock_creation_request = GameCreationRequest(
        roomID=0,
        players=[
            PlayerID(playerID=666),
            PlayerID(playerID=2),
        ]
    ).model_dump()
    response = client.post("/game", json=mock_creation_request)
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid player ID"}


def test_get_game_status(db_game_status):
    expected_response = db_game_status.model_dump()
    response = client.get("/game/1")
    assert response.status_code == 200
    assert response.json() == expected_response


def test_get_game_status_invalid_id():
    response = client.get("/game/666")
    assert response.status_code == 404

from main import app
from fastapi.testclient import TestClient
from models import Game, WaitingRoom
from pony.orm import db_session, select
from schemas.game import GameCreationRequest, PlayerID, GameID
from .util import setup_test_db
import pytest

client = TestClient(app)


def setup_database():
    with db_session:
        # Create a waiting room with players for testing
        room = WaitingRoom(id=0, room_name="Test room")
        room.players.create(username="Player1")
        room.players.create(username="Player2")


@pytest.fixture(scope="module")
def setup_test_environment():
    setup_test_db()
    setup_database()


def test_create_game_success(setup_test_environment):
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


def test_invalid_room_id(setup_test_environment):
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


def test_invalid_player_id(setup_test_environment):
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

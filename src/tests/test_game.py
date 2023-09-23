from main import app
from fastapi.testclient import TestClient
from models import Card, Game, WaitingRoom, db
from pony.orm import db_session, select
from schemas.game import GameCreationRequest, PlayerID, GameID
from .util import setup_test_db
import pytest

# Create a TestClient instance for the FastAPI app
client = TestClient(app)

# Define a fixture for setting up the test database


def setup_database():
    with db_session:
        # Create a waiting room with players for testing
        room = WaitingRoom(id=0, room_name="Test room")
        room.players.create(username="Player1")
        room.players.create(username="Player2")

# Use a fixture to setup the test database


@pytest.fixture
def setup_test_environment():
    setup_test_db()
    setup_database()

# Define the test function


def test_create_game_success(setup_test_environment):
    # Mocked GameCreationRequest data for testing
    mock_creation_request = GameCreationRequest(
        roomID=0,
        players=[
            PlayerID(playerID=0),
            PlayerID(playerID=1),
        ]
    ).model_dump()
    creation_response = GameID(gameID=1).model_dump()

    response = client.post("/game", json=mock_creation_request)
    data = response.json()

    with db_session:
        game_record = select(g for g in Game if g.id == int(data["gameID"]))
        assert game_record

    assert response.status_code == 201
    assert data == creation_response

from main import app
from fastapi.testclient import TestClient
from models import WaitingRoom
from pony.orm import db_session, select
from schemas.room import RoomCreationRequest, RoomID, PlayerID
from .util import setup_test_db
import pytest

client = TestClient(app)


def setup_database():
    with db_session:
        # Create a waiting room with players for testing
        room = WaitingRoom(id=5, room_name="Test room2")
        room.players.create(username="Player1", is_host=True)


@pytest.fixture(scope="module")
def setup_test_environment():
    setup_test_db()
    setup_database()


def test_create_room_success(setup_test_environment):
    mock_creation_request = RoomCreationRequest(
        roomName="Test room",
        hostName="Player1",
    ).model_dump()

    creation_response = (RoomID(roomID=1), PlayerID(playerID=1))

    response = client.post("/room", json=mock_creation_request)
    data = response.json()

    with db_session:
        room_record = select(r for r in WaitingRoom if r.id ==
                             int(data["roomID"])).get()

        # Room was created
        assert room_record is not None

        # Host was created
        assert len(room_record.players) > 0

        # Host was assigned to the room
        assert room_record.players[0].username == "Player1"


def test_repeated_room_name(setup_test_environment):
    mock_creation_request = RoomCreationRequest(
        roomName="Test room2",
        hostName="Player1",
    ).model_dump()

    response = client.post("/room", json=mock_creation_request)

    # Room was not created
    assert response.status_code == 400

from main import app
from fastapi.testclient import TestClient
from models import WaitingRoom
from pony.orm import db_session, select
from lacosa.room.schemas import RoomCreationRequest, RoomCreationResponse
from .room_fixtures import db_room_creation

client = TestClient(app)


def test_create_room_success(db_room_creation):
    mock_creation_request = RoomCreationRequest(
        roomName="Test Room",
        hostName="Test Host"
    ).model_dump()

    creation_response = RoomCreationResponse(
        roomID=1,
        playerID=2
    ).model_dump()

    response = client.post("/room", json=mock_creation_request)
    data = response.json()

    assert response.status_code == 201
    assert data == creation_response

    with db_session:
        room_record = select(r for r in WaitingRoom if r.id ==
                             int(data["roomID"])).get()

        # Room was created
        assert room_record is not None

        # Host was created
        assert len(room_record.players) == 1

        # Host is host
        player_list = list(room_record.players)
        assert player_list[0].is_host


def test_create_room_duplicate_name(db_room_creation):
    mock_creation_request = RoomCreationRequest(
        roomName="Test Room2",
        hostName="Test Host"
    ).model_dump()

    response = client.post("/room", json=mock_creation_request)
    data = response.json()

    assert response.status_code == 400
    assert data["detail"] == "Room name already exists"

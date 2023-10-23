from main import app
from fastapi.testclient import TestClient
from models import WaitingRoom, Player, db
from pony.orm import db_session
from lacosa.room.schemas import RoomDataResponse, PlayerName, PlayerSchema
import pytest
from .room_fixtures import db_room_creation_with_players

client = TestClient(app)


def test_get_room_data_success(db_room_creation_with_players):
    mock_room_data = RoomDataResponse(
        CountPlayers=3,
        Players=[
            PlayerName(playerName="Test_player"),
            PlayerName(playerName="Test_player2"),
            PlayerName(playerName="Test_player3"),
        ],
        hasStarted=False,
        maxPlayers=8,
        minPlayers=2,
        host=PlayerSchema(id=1, name="Test_player"),
    ).model_dump()

    response = client.get("/room/0")
    data = response.json()

    # ordenar
    data["Players"].sort(key=lambda x: x["playerName"])

    assert response.status_code == 200
    assert data == mock_room_data


def test_get_room_data_room_not_found(db_room_creation_with_players):
    mock_error = {
        "detail": "Room not found"
    }

    response = client.get("/room/1")
    data = response.json()

    assert response.status_code == 404
    assert data == mock_error

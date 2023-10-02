from main import app
from fastapi.testclient import TestClient
from models import WaitingRoom, Player, db
from pony.orm import db_session
from schemas.room import RoomDataResponse, PlayerName
import pytest

client = TestClient(app)

@pytest.fixture(scope="module")
def db_room_creation():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()
    with db_session:
        room = WaitingRoom(id=0, room_name="Test Room")
        for i in range(3):
            player = Player(id=i, username=f"Player{i}", room=room)
            room.players.add(player)

def test_get_room_data_success(db_room_creation):
    mock_room_data = RoomDataResponse(
        CountPlayers=3,
        Players=[
            PlayerName(playerName="Player0"),
            PlayerName(playerName="Player1"),
            PlayerName(playerName="Player2"),
        ]
    ).model_dump()
    
    response = client.get("/room/0")
    data = response.json()

    data['Players'] = sorted(data['Players'], key=lambda x: x['playerName'])

    assert response.status_code == 200
    assert data == mock_room_data

def test_get_room_data_room_not_found(db_room_creation):
    mock_error = {
        "detail": "Room not found"
    }

    response = client.get("/room/1")
    data = response.json()

    assert response.status_code == 404
    assert data == mock_error
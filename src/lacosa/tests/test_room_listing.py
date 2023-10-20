from main import app
from fastapi.testclient import TestClient
from .room_fixtures import create_rooms_and_return_expected

client = TestClient(app)


def test_get_room_listing(create_rooms_and_return_expected):
    room1_response, room2_response = create_rooms_and_return_expected
    response = client.get("/room/rooms")
    assert response.status_code == 200

    response_data = response.json()
    expected_data = {
        "rooms": [room1_response, room2_response]
    }
    assert response_data == expected_data

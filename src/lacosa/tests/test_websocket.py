from main import app  # Import your FastAPI app instance
from fastapi.testclient import TestClient
from .room_fixtures import db_room_creation_with_players

client = TestClient(app)


def test_websocket_endpoint(db_room_creation_with_players):
    with client.websocket_connect("/room/ws/1") as websocket:
        # Send a message
        websocket.send_json({"username": "capo", "msg": "This is a test"})

        # Receive the response
        response = websocket.receive_json()

        # Assert the response
        # Replace "TestPlayer" with the expected player username
        assert response["username"] == "capo"
        assert response["msg"] == "This is a test"


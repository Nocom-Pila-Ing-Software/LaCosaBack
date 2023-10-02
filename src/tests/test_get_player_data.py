from main import app
from fastapi.testclient import TestClient
from pony.orm import db_session
from .game_fixtures import db_game_creation_with_cards, db_game_creation_without_cards

client = TestClient(app)

def test_get_player_sucesfully(db_game_creation_with_cards):
    with db_session:
        response = client.get("/player/1")
        assert response.status_code == 200
        #convertir la list de response.json en set

        assert response.json() == {
            "hand": sorted([
                {
                    "id": 1,
                    "name": "Carta_test",
                    "description": "Carta test"
                },
                {
                    "id": 2,
                    "name": "Carta_test",
                    "description": "Carta test"
                },
                {
                    "id": 3,
                    "name": "Carta_test",
                    "description": "Carta test"
                },
                {
                    "id": 4,
                    "name": "Carta_test",
                    "description": "Carta test"
                },
                {
                    "id": 5,
                    "name": "Carta_test",
                    "description": "Carta test"
                }
            ], key=lambda x: x["id"]),
            "role": "human",
            "is_alive": True
        }

def test_get_player_not_found(db_game_creation_with_cards):
    with db_session:
        response = client.get("/player/100")
        assert response.status_code == 404
        assert response.json() == {
            "detail": "Player ID doesn't exist"
        }

def test_get_card_not_found(db_game_creation_without_cards):
    with db_session:
        response = client.get("/player/1")
        assert response.status_code == 200
        assert response.json() == {
            "hand": [],
            "role": "human",
            "is_alive": True
        }
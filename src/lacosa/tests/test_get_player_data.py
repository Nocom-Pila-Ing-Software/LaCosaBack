from main import app
from fastapi.testclient import TestClient
from pony.orm import db_session, commit
from .game_fixtures import (
    db_game_creation_with_cards_player_data,
    db_game_creation_without_cards,
    discard_card_game_creation
)
from models import Player

client = TestClient(app)


def test_get_player_sucesfully(db_game_creation_with_cards_player_data):
    with db_session:
        response = client.get("/player/1")
        assert response.status_code == 200
        # convertir la list de response.json en set

        assert response.json() == {
            "hand": sorted([
                {
                    "cardID": 1,
                    "name": "Carta_test",
                    "description": "Carta test"
                },
                {
                    "cardID": 2,
                    "name": "Carta_test",
                    "description": "Carta test"
                },
                {
                    "cardID": 3,
                    "name": "Carta_test",
                    "description": "Carta test"
                },
                {
                    "cardID": 4,
                    "name": "Carta_test",
                    "description": "Carta test"
                },
                {
                    "cardID": 5,
                    "name": "Carta_test",
                    "description": "Carta test"
                }
            ], key=lambda x: x["cardID"]),
            "role": "human",
            "is_alive": True,
            "shownCards": [],
        }


def test_get_player_not_found(db_game_creation_with_cards_player_data):
    with db_session:
        response = client.get("/player/100")
        assert response.status_code == 404
        assert response.json() == {
            "detail": "Player not found"
        }


def test_get_card_not_found(db_game_creation_without_cards):
    with db_session:
        response = client.get("/player/1")
        assert response.status_code == 200
        assert response.json() == {
            "hand": [],
            "role": "human",
            "is_alive": True,
            "shownCards": [],
        }


def test_show_cards(discard_card_game_creation):
    data = discard_card_game_creation
    player_id = data["players"][0]["id"]
    player2_id = data["players"][1]["id"]
    with db_session:
        player1 = Player.get(id=player_id)
        player2 = Player.get(id=player2_id)
        card = player2.cards.filter().sort_by(lambda x: x.id).first()
        player1.shown_cards.add(card)
        commit()
        response = client.get(f"/player/{player_id}")
        response_json = response.json()
        assert response.status_code == 200
        assert response_json["hand"] == [
            {'cardID': 1, 'name': 'card1', 'description': 'Generic card description'},
            {'cardID': 2, 'name': 'card2', 'description': 'Generic card description'},
            {'cardID': 3, 'name': 'card3', 'description': 'Generic card description'},
            {'cardID': 4, 'name': 'card4', 'description': 'Generic card description'}
        ]
        assert response_json["role"] == "human"
        assert response_json["is_alive"] is True
        assert response_json["shownCards"] == [
            {'cardID': 5, 'name': 'card5', 'description': 'Generic card description'}
        ]

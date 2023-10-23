from main import app
from fastapi.testclient import TestClient
from pony.orm import db_session
from .game_fixtures import db_game_creation_with_cards_player_data, db_game_creation_without_cards_dead_players, get_info_card_game_creation
from .room_fixtures import db_room_creation_with_players

client = TestClient(app)


def test_get_card_usability_sucesfully(get_info_card_game_creation):
    # Review cards usability for player 1
    player_id = get_info_card_game_creation["player"][0]["id"]

    response = client.get(f"/player/{player_id}/cards-usability")

    assert response.status_code == 200

    assert response.json()["cards"][0]["cardID"] == 1
    assert response.json()["cards"][0]["name"] == "infectado"
    assert response.json()["cards"][0]["playable"] == False
    assert response.json()["cards"][0]["discardable"] == False

    assert response.json()["cards"][1]["cardID"] == 2
    assert response.json()["cards"][1]["name"] == "card2"
    assert response.json()["cards"][1]["playable"] == False
    assert response.json()["cards"][1]["discardable"] == False

    assert response.json()["cards"][2]["cardID"] == 3
    assert response.json()["cards"][2]["name"] == "card3"
    assert response.json()["cards"][2]["playable"] == False
    assert response.json()["cards"][2]["discardable"] == False

    assert response.json()["cards"][3]["cardID"] == 4
    assert response.json()["cards"][3]["name"] == "card4"
    assert response.json()["cards"][3]["playable"] == False
    assert response.json()["cards"][3]["discardable"] == False

    # Review cards usability for player 2
    player_id = get_info_card_game_creation["player"][1]["id"]

    response = client.get(f"/player/{player_id}/cards-usability")

    assert response.status_code == 200

    assert response.json()["cards"][0]["cardID"] == 5
    assert response.json()["cards"][0]["name"] == "infectado"
    assert response.json()["cards"][0]["playable"] == False
    assert response.json()["cards"][0]["discardable"] == True

    assert response.json()["cards"][1]["cardID"] == 6
    assert response.json()["cards"][1]["name"] == "La cosa"
    assert response.json()["cards"][1]["playable"] == False
    assert response.json()["cards"][1]["discardable"] == False

    assert response.json()["cards"][2]["cardID"] == 7
    assert response.json()["cards"][2]["name"] == "Lanzallamas"
    assert response.json()["cards"][2]["playable"] == True
    assert response.json()["cards"][2]["discardable"] == True

    assert response.json()["cards"][3]["cardID"] == 8
    assert response.json()["cards"][3]["name"] == "No gracias"
    assert response.json()["cards"][3]["playable"] == False
    assert response.json()["cards"][3]["discardable"] == True

    assert response.json()["cards"][4]["cardID"] == 19
    assert response.json()["cards"][4]["name"] == "Sospecha"
    assert response.json()["cards"][4]["playable"] == True
    assert response.json()["cards"][4]["discardable"] == True

    # Review cards usability for player 3
    player_id = get_info_card_game_creation["player"][2]["id"]

    response = client.get(f"/player/{player_id}/cards-usability")

    assert response.status_code == 200

    assert response.json()["cards"][0]["cardID"] == 9
    assert response.json()["cards"][0]["name"] == "infectado"
    assert response.json()["cards"][0]["playable"] == False
    assert response.json()["cards"][0]["discardable"] == True

    assert response.json()["cards"][1]["cardID"] == 10
    assert response.json()["cards"][1]["name"] == "Aterrador"
    assert response.json()["cards"][1]["playable"] == False
    assert response.json()["cards"][1]["discardable"] == True

    assert response.json()["cards"][2]["cardID"] == 11
    assert response.json()["cards"][2]["name"] == "infectado"
    assert response.json()["cards"][2]["playable"] == False
    assert response.json()["cards"][2]["discardable"] == True

    assert response.json()["cards"][3]["cardID"] == 12
    assert response.json()["cards"][3]["name"] == "Cambio de lugar"
    assert response.json()["cards"][3]["playable"] == True
    assert response.json()["cards"][3]["discardable"] == True

def get_card_usability_wrong_player_id():
    response = client.get(f"/player/809/cards-usability")

    assert response.status_code == 404
    assert response.json()["detail"] == "Player not found"

def get_card_usability_player_not_in_game(db_game_creation_without_cards):
    response = client.get(f"/player/1/cards-usability")

    assert response.status_code == 400
    assert response.json()["detail"] == "Player not in game"

def get_card_usability_player_dead(db_game_creation_without_cards_dead_players):
    response = client.get(f"/player/1/cards-usability")

    assert response.status_code == 400
    assert response.json()["detail"] == "Player is dead"


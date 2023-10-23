from main import app
from fastapi.testclient import TestClient
from pony.orm import db_session
from .game_fixtures import db_game_creation_with_cards_player_data, db_game_creation_without_cards_dead_players, get_info_card_game_creation
from .room_fixtures import db_room_creation_with_players

client = TestClient(app)


def test_get_card_usability_sucesfully(get_info_card_game_creation):
    # Review cards usability for player 1
    player_id = get_info_card_game_creation["players"][0]["id"]

    response = client.get(f"/player/{player_id}/cards-usability")

    assert response.status_code == 200

    for card in response.json()["cards"]:
        if card["cardID"] == 1:
            assert card["name"] == "infectado"
            assert card["playable"] == False
            assert card["discardable"] == False
        elif card["cardID"] == 2:
            assert card["name"] == "Lanzallamas"
            assert card["playable"] == True
            assert card["discardable"] == True
        elif card["cardID"] == 3:
            assert card["name"] == "Lanzallamas"
            assert card["playable"] == True
            assert card["discardable"] == True
        elif card["cardID"] == 4:
            assert card["name"] == "Lanzallamas"
            assert card["playable"] == True
            assert card["discardable"] == True

    # Review cards usability for player 2
    player_id = get_info_card_game_creation["players"][1]["id"]

    response = client.get(f"/player/{player_id}/cards-usability")

    assert response.status_code == 200

    for card in response.json()["cards"]:
        if card["cardID"] == 5:
            assert card["name"] == "infectado"
            assert card["playable"] == False
            assert card["discardable"] == True
        elif card["cardID"] == 6:
            assert card["name"] == "La cosa"
            assert card["playable"] == False
            assert card["discardable"] == False
        elif card["cardID"] == 7:
            assert card["name"] == "Lanzallamas"
            assert card["playable"] == True
            assert card["discardable"] == True
        elif card["cardID"] == 8:
            assert card["name"] == "No, gracias"
            assert card["playable"] == False
            assert card["discardable"] == True
        elif card["cardID"] == 19:
            assert card["name"] == "Sospecha"
            assert card["playable"] == True
            assert card["discardable"] == True

    # Review cards usability for player 3
    player_id = get_info_card_game_creation["players"][2]["id"]

    response = client.get(f"/player/{player_id}/cards-usability")

    assert response.status_code == 200

    for card in response.json()["cards"]:
        if card["cardID"] == 9:
            assert card["name"] == "infectado"
            assert card["playable"] == False
            assert card["discardable"] == True
        elif card["cardID"] == 10:
            assert card["name"] == "Aterrador"
            assert card["playable"] == False
            assert card["discardable"] == True
        elif card["cardID"] == 11:
            assert card["name"] == "infectado"
            assert card["playable"] == False
            assert card["discardable"] == True
        elif card["cardID"] == 12:
            assert card["name"] == "Cambio de lugar"
            assert card["playable"] == True
            assert card["discardable"] == True


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

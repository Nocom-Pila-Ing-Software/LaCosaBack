from main import app
from fastapi.testclient import TestClient
from models import Game, Player, Event
from pony.orm import db_session, select, delete
from .game_fixtures import db_game_creation_with_cards_player_data, db_game_creation_without_cards_dead_players, get_info_card_game_creation, get_defend_card_game_creation, get_tradeable_info_card_game_creation, get_info_card_game_creation_with_dead_players, db_game_creation_without_cards_dead_players_and_event
from .room_fixtures import db_room_creation_with_players

client = TestClient(app)


def test_get_card_usability_sucesfully(get_info_card_game_creation):
    # Review cards usability for player 1
    player_id = get_info_card_game_creation["players"][0]["id"]

    response = client.get(f"/player/{player_id}/cards-usability")

    assert response.status_code == 200

    for card in response.json()["cards"]:
        if card["cardID"] == 1:
            assert card["name"] == "Infeccion"
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
            assert card["name"] == "Infeccion"
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
            assert card["name"] == "No gracias"
            assert card["playable"] == False
            assert card["discardable"] == True
        elif card["cardID"] == 19:
            assert card["name"] == "Seduccion"
            assert card["playable"] == True
            assert card["discardable"] == True

    # Review cards usability for player 3
    player_id = get_info_card_game_creation["players"][2]["id"]

    response = client.get(f"/player/{player_id}/cards-usability")

    assert response.status_code == 200

    for card in response.json()["cards"]:
        if card["cardID"] == 9:
            assert card["name"] == "Infeccion"
            assert card["playable"] == False
            assert card["discardable"] == True
        elif card["cardID"] == 10:
            assert card["name"] == "Aterrador"
            assert card["playable"] == False
            assert card["discardable"] == True
        elif card["cardID"] == 11:
            assert card["name"] == "Infeccion"
            assert card["playable"] == False
            assert card["discardable"] == True
        elif card["cardID"] == 12:
            assert card["name"] == "Cambio de lugar"
            assert card["playable"] == True
            assert card["discardable"] == True


def test_get_card_usability_wrong_player_id():
    response = client.get(f"/player/809/cards-usability")

    assert response.status_code == 404
    assert response.json()["detail"] == "Player not found"


def test_get_card_usability_player_not_in_game(db_room_creation_with_players):
    response = client.get(f"/player/1/cards-usability")

    assert response.status_code == 400
    assert response.json()["detail"] == "Player not in game"


def test_get_card_usability_player_dead(db_game_creation_without_cards_dead_players):
    response = client.get(f"/player/1/cards-usability")

    assert response.status_code == 400
    assert response.json()["detail"] == "Player is dead"

def test_get_cards_defend(get_defend_card_game_creation):
    # Review cards defend for player 1
    player_id = get_defend_card_game_creation["players"][0]["id"]
    card_id = get_defend_card_game_creation["cards"][1][2]["id"]

    response = client.get(f"/player/{player_id}/cards-defend/{card_id}")

    assert response.status_code == 200

    for card in response.json()["cards"]:
        if card["cardID"] == 1:
            assert card["name"] == "Infeccion"
            assert card["usable"] == False
        elif card["cardID"] == 2:
            assert card["name"] == "Nada de Barbacoas"
            assert card["usable"] == True
        elif card["cardID"] == 3:
            assert card["name"] == "Nada de Barbacoas"
            assert card["usable"] == True
        elif card["cardID"] == 4:
            assert card["name"] == "Nada de Barbacoas"
            assert card["usable"] == True

    # Review cards defend for player 2
    player_id = get_defend_card_game_creation["players"][1]["id"]
    card_id = get_defend_card_game_creation["cards"][1][2]["id"]

    response = client.get(f"/player/{player_id}/cards-defend/{card_id}")

    assert response.status_code == 200

    for card in response.json()["cards"]:
        if card["cardID"] == 5:
            assert card["name"] == "Infeccion"
            assert card["usable"] == False
        elif card["cardID"] == 6:
            assert card["name"] == "La cosa"
            assert card["usable"] == False
        elif card["cardID"] == 7:
            assert card["name"] == "Lanzallamas"
            assert card["usable"] == False
        elif card["cardID"] == 8:
            assert card["name"] == "No gracias"
            assert card["usable"] == False
        elif card["cardID"] == 19:
            assert card["name"] == "Seduccion"
            assert card["usable"] == False

    # Review cards defend for player 3
    player_id = get_defend_card_game_creation["players"][2]["id"]
    card_id = get_defend_card_game_creation["cards"][1][2]["id"]

    response = client.get(f"/player/{player_id}/cards-defend/{card_id}")

    assert response.status_code == 200

    for card in response.json()["cards"]:
        if card["cardID"] == 9:
            assert card["name"] == "Infeccion"
            assert card["usable"] == False
        elif card["cardID"] == 10:
            assert card["name"] == "Aterrador"
            assert card["usable"] == False
        elif card["cardID"] == 11:
            assert card["name"] == "Nada de Barbacoas"
            assert card["usable"] == True
        elif card["cardID"] == 12:
            assert card["name"] == "Cambio de lugar"
            assert card["usable"] == False

def test_get_cards_defend_wrong_player_id():
    response = client.get(f"/player/809/cards-defend/1")

    assert response.status_code == 404
    assert response.json()["detail"] == "Player not found"

def test_get_cards_defend_wrong_card_id(get_defend_card_game_creation):
    player_id = get_defend_card_game_creation["players"][0]["id"]
    card_id = 809

    response = client.get(f"/player/{player_id}/cards-defend/{card_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Card not found"

#def test_get_cards_tradeable(get_tradeable_info_card_game_creation):
#    # Cards tradeable event infected -> human
#    with db_session:
#        game = get_tradeable_info_card_game_creation["game"]["id"]
#        game = select(g for g in Game if g.id == game).get()
#        players = (select(p for p in game.players)[:])
#        delete(p for p in Event)
#        game.events.create(type="trade", player1=players[0], player2=players[2])
#
#    player_id = get_tradeable_info_card_game_creation["players"][0]["id"]
#
#    response = client.get(f"/player/{player_id}/cards-trade")
#
#    assert response.status_code == 200
#
#    for card in response.json()["cards"]:
#        if card["cardID"] == 1:
#            assert card["name"] == "Infeccion"
#            assert card["usable"] == False
#        elif card["cardID"] == 2:
#            assert card["name"] == "Infeccion"
#            assert card["usable"] == False
#        elif card["cardID"] == 3:
#            assert card["name"] == "Lanzallamas"
#            assert card["usable"] == True
#        elif card["cardID"] == 4:
#            assert card["name"] == "Nada de Barbacoas"
#            assert card["usable"] == True
#
#    # Cards tradeable event human -> infected
#    with db_session:
#        game = get_tradeable_info_card_game_creation["game"]["id"]
#        game = select(g for g in Game if g.id == game).get()
#        players = (select(p for p in game.players)[:])
#        delete(p for p in Event)
#        game.events.create(type="trade", player1=players[2], player2=players[0])
#
#    player_id = get_tradeable_info_card_game_creation["players"][2]["id"]
#
#    response = client.get(f"/player/{player_id}/cards-trade")
#
#    assert response.status_code == 200
#
#    for card in response.json()["cards"]:
#        if card["cardID"] == 9:
#            assert card["name"] == "Infeccion"
#            assert card["usable"] == False
#        elif card["cardID"] == 10:
#            assert card["name"] == "Aterrador"
#            assert card["usable"] == True
#        elif card["cardID"] == 11:
#            assert card["name"] == "Infeccion"
#            assert card["usable"] == False
#        elif card["cardID"] == 12:
#            assert card["name"] == "Cambio de lugar"
#            assert card["usable"] == True
#
#    # Cards tradeable event infected -> thing with 2 cards infected
#    with db_session:
#        game = get_tradeable_info_card_game_creation["game"]["id"]
#        game = select(g for g in Game if g.id == game).get()
#        players = (select(p for p in game.players)[:])
#        delete(p for p in Event)
#        game.events.create(type="trade", player1=players[0], player2=players[1])
#
#    player_id = get_tradeable_info_card_game_creation["players"][0]["id"]
#
#    response = client.get(f"/player/{player_id}/cards-trade")
#
#    assert response.status_code == 200
#
#    for card in response.json()["cards"]:
#        if card["cardID"] == 1:
#            assert card["name"] == "Infeccion"
#            assert card["usable"] == True
#        elif card["cardID"] == 2:
#            assert card["name"] == "Infeccion"
#            assert card["usable"] == True
#        elif card["cardID"] == 3:
#            assert card["name"] == "Lanzallamas"
#            assert card["usable"] == True
#        elif card["cardID"] == 4:
#            assert card["name"] == "Nada de Barbacoas"
#            assert card["usable"] == True
#
#    # Cards tradeable event infected -> thing with 1 card infected
#    with db_session:
#        game = get_tradeable_info_card_game_creation["game"]["id"]
#        game = select(g for g in Game if g.id == game).get()
#        players = (select(p for p in game.players)[:])
#        delete(p for p in Event)
#        game.events.create(type="trade", player1=players[3], player2=players[1])
#
#    player_id = get_tradeable_info_card_game_creation["players"][3]["id"]
#
#    response = client.get(f"/player/{player_id}/cards-trade")
#
#    assert response.status_code == 200
#
#    for card in response.json()["cards"]:
#        if card["cardID"] == 13:
#            assert card["name"] == "Infeccion"
#            assert card["usable"] == False
#        elif card["cardID"] == 14:
#            assert card["name"] == "Aterrador"
#            assert card["usable"] == True
#        elif card["cardID"] == 15:
#            assert card["name"] == "Lanzallamas"
#            assert card["usable"] == True
#        elif card["cardID"] == 16:
#            assert card["name"] == "No gracias"
#            assert card["usable"] == True
#
#    # Cards tradeable event thing -> infected
#    with db_session:
#        game = get_tradeable_info_card_game_creation["game"]["id"]
#        game = select(g for g in Game if g.id == game).get()
#        players = (select(p for p in game.players)[:])
#        delete(p for p in Event)
#        game.events.create(type="trade", player1=players[1], player2=players[0])
#
#    player_id = get_tradeable_info_card_game_creation["players"][1]["id"]
#
#    response = client.get(f"/player/{player_id}/cards-trade")
#
#    assert response.status_code == 200
#
#    for card in response.json()["cards"]:
#        if card["cardID"] == 5:
#            assert card["name"] == "Infeccion"
#            assert card["usable"] == False
#        elif card["cardID"] == 6:
#            assert card["name"] == "La cosa"
#            assert card["usable"] == False
#        elif card["cardID"] == 7:
#            assert card["name"] == "Lanzallamas"
#            assert card["usable"] == True
#        elif card["cardID"] == 8:
#            assert card["name"] == "No gracias"
#            assert card["usable"] == True
#
#    # Cards tradeable event thing -> human
#    with db_session:
#        game = get_tradeable_info_card_game_creation["game"]["id"]
#        game = select(g for g in Game if g.id == game).get()
#        players = (select(p for p in game.players)[:])
#        delete(p for p in Event)
#        game.events.create(type="trade", player1=players[1], player2=players[2])
#
#    player_id = get_tradeable_info_card_game_creation["players"][1]["id"]
#
#    response = client.get(f"/player/{player_id}/cards-trade")
#
#    assert response.status_code == 200
#
#    for card in response.json()["cards"]:
#        if card["cardID"] == 5:
#            assert card["name"] == "Infeccion"
#            assert card["usable"] == True
#        elif card["cardID"] == 6:
#            assert card["name"] == "La cosa"
#            assert card["usable"] == False
#        elif card["cardID"] == 7:
#            assert card["name"] == "Lanzallamas"
#            assert card["usable"] == True
#        elif card["cardID"] == 8:
#            assert card["name"] == "No gracias"
#            assert card["usable"] == True

def test_get_cards_tradeable_wrong_player_id():
    response = client.get(f"/player/809/cards-trade")

    assert response.status_code == 404
    assert response.json()["detail"] == "Player not found"

def test_get_cards_tradeable_player_dead(db_game_creation_without_cards_dead_players_and_event):
    response = client.get(f"/player/1/cards-trade")

    assert response.status_code == 400
    assert response.json()["detail"] == "Player is dead"

def test_get_targets_card(get_info_card_game_creation_with_dead_players):
    # Player1 uses Lanzallamas
    player_id = get_info_card_game_creation_with_dead_players["players"][0]["id"]
    card_id = get_info_card_game_creation_with_dead_players["cards"][0][2]["id"]

    response = client.get(f"/player/{player_id}/targets/{card_id}")

    assert response.status_code == 200

    response = response.json()

    assert response == {
        "targets": [
            {
                "playerID": 2,
                "name": "Player2"
            },
            {
                "playerID": 5,
                "name": "Player5"
            }
        ]
    }

    # Player2 uses Lanzallamas
    player_id = get_info_card_game_creation_with_dead_players["players"][1]["id"]
    card_id = get_info_card_game_creation_with_dead_players["cards"][1][2]["id"]

    response = client.get(f"/player/{player_id}/targets/{card_id}")

    assert response.status_code == 200

    response = response.json()

    assert response == {
        "targets": [
            {
                "playerID": 1,
                "name": "Player1"
            },
            {
                "playerID": 4,
                "name": "Player4"
            }
        ]
    }

    # Player2 uses Seduccion
    player_id = get_info_card_game_creation_with_dead_players["players"][1]["id"]
    card_id = get_info_card_game_creation_with_dead_players["cards"][1][4]["id"]

    response = client.get(f"/player/{player_id}/targets/{card_id}")

    assert response.status_code == 200

    response = response.json()

    assert response == {
        "targets": [
            {
                "playerID": 1,
                "name": "Player1"
            },
            {
                "playerID": 4,
                "name": "Player4"
            },
            {
                "playerID": 5,
                "name": "Player5"
            }
        ]
    }

    # Player4 uses Cambio de lugar
    player_id = get_info_card_game_creation_with_dead_players["players"][3]["id"]
    card_id = get_info_card_game_creation_with_dead_players["cards"][3][3]["id"]

    response = client.get(f"/player/{player_id}/targets/{card_id}")

    assert response.status_code == 200

    response = response.json()

    assert response == {
        "targets": [
            {
                "playerID": 2,
                "name": "Player2"
            },
            {
                "playerID": 5,
                "name": "Player5"
            }
        ]
    }

def test_get_targets_card_wrong_player_id():
    response = client.get(f"/player/809/targets/1")

    assert response.status_code == 404
    assert response.json()["detail"] == "Player not found"

def test_get_targets_card_wrong_card_id(get_info_card_game_creation):
    player_id = get_info_card_game_creation["players"][0]["id"]
    card_id = 809

    response = client.get(f"/player/{player_id}/targets/{card_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Card not found"

def test_get_targets_card_not_in_player_hand(get_info_card_game_creation):
    player_id = get_info_card_game_creation["players"][0]["id"]
    card_id = get_info_card_game_creation["cards"][1][0]["id"]

    response = client.get(f"/player/{player_id}/targets/{card_id}")

    assert response.status_code == 403

def test_get_targets_card_without_targets(get_info_card_game_creation):
    player_id = get_info_card_game_creation["players"][0]["id"]
    card_id = get_info_card_game_creation["cards"][0][0]["id"]

    response = client.get(f"/player/{player_id}/targets/{card_id}")

    assert response.status_code == 403


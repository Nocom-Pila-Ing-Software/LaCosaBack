from .game_fixtures import revelations_setup
from lacosa.game.utils.card import effects
from models import Player, Game
from pony.orm import db_session
from main import app
from fastapi.testclient import TestClient
from lacosa.game.schemas import EventTypes

client = TestClient(app)


def test_revelations_effect_function(revelations_setup):
    data = revelations_setup
    with db_session:
        player = Player.get(id=data["game"]["current_player"])
        game = Game.get(id=data["game"]["id"])

        effects.apply_revelaciones_effect(player, None, game)

        event = game.events.filter().get()
        assert event.type == EventTypes.revelations_start
        assert game.current_action == "revelations"


def get_card_schema(card):
    return {"cardID": card["id"], "name": card["name"], "description": ""}


def test_revelations_round(revelations_setup):
    data = revelations_setup
    counter = 0
    game_id = data["game"]["id"]
    with db_session:
        game = Game.get(id=game_id)
        game.current_action = "revelations"

    for player, cards in zip(data["players"], data["cards"]):
        req = {
            "playerID": player["id"],
            "cardsToShow": "all" if counter % 2 == 0 else "none"
        }
        response = client.put(f"/game/{game_id}/revelations", json=req)

        assert response.status_code == 200

        with db_session:
            game = Game.get(id=game_id)
            assert game.current_action == "revelations"
            assert game.current_player != player["id"]

        counter += 1

    p1 = data["players"][0]["id"]
    req = {
        "playerID": p1,
        "cardsToShow": "infection"
    }
    response = client.put(f"/game/{game_id}/revelations", json=req)
    assert response.status_code == 200
    with db_session:
        game = Game.get(id=game_id)
        assert game.current_action == "draw"
        assert game.current_player != p1


def test_player_doesnt_have_infection(revelations_setup):
    data = revelations_setup
    game_id = data["game"]["id"]
    p4 = data["players"][3]["id"]
    with db_session:
        game = Game.get(id=game_id)
        game.current_action = "revelations"
        game.current_player = p4

    req = {
        "playerID": p4,
        "cardsToShow": "infection"
    }

    response = client.put(f"/game/{game_id}/revelations", json=req)

    assert response.status_code == 400


def test_player_invalid_turn(revelations_setup):
    data = revelations_setup
    game_id = data["game"]["id"]
    p2 = data["players"][1]["id"]
    with db_session:
        game = Game.get(id=game_id)
        game.current_action = "revelations"

    req = {
        "playerID": p2,
        "cardsToShow": "infection"
    }

    response = client.put(f"/game/{game_id}/revelations", json=req)

    assert response.status_code == 403

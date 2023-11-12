from .game_fixtures import revelations_setup
from lacosa.game.utils.card import effects
from models import Player, Game
from pony.orm import db_session, commit
from main import app
from fastapi.testclient import TestClient
from lacosa.game import schemas
import time

client = TestClient(app)


def test_revelations_effect_function(revelations_setup):
    data = revelations_setup
    with db_session:
        player = Player.get(id=data["game"]["current_player"])
        game = Game.get(id=data["game"]["id"])

        effects.apply_revelaciones_effect(player, None, game)

        event = game.events.filter().get()
        assert event.type == "revelations"
        assert game.current_action == "revelations"


def get_card_schema(card):
    return {"cardID": card["id"], "name": card["name"], "description": ""}


def test_revelations(revelations_setup):
    data = revelations_setup
    counter = 0
    with db_session:
        game = Game.get(id=data["game"]["id"])
        game.current_action = "revelations"

    for player, cards in zip(data["players"], data["cards"]):
        req = {
            "playerID": player["id"],
            "cards": [get_card_schema(card) for card in cards] if counter % 2 == 0 else []
        }
        response = client.put(f"/game/{game.id}/revelations", json=req)

        assert response.status_code == 200

        with db_session:
            game = Game.get(id=data["game"]["id"])
            assert game.current_action == "revelations"
            assert game.current_player != player["id"]

        counter += 1

    p1 = data["players"][0]["id"]
    req = {
        "playerID": p1,
        "cards": [get_card_schema(data["cards"][0][0])]
    }
    response = client.put(f"/game/{game.id}/revelations", json=req)
    with db_session:
        game = Game.get(id=data["game"]["id"])
        assert game.current_action == "draw"
        assert game.current_player != p1

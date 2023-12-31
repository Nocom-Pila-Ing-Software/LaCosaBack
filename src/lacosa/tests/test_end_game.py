from main import app
from fastapi.testclient import TestClient
from models import Game, WaitingRoom, db, Player, Card
from pony.orm import db_session
from lacosa.game.utils.game.ender import (
    _get_winner,
    _update_game_state,
    _are_all_humans_dead,
)
from lacosa.schemas import PlayerID


client = TestClient(app)


def create_game_with_custom_players(custom_players):
    db.drop_all_tables(with_all_data=True)
    db.create_tables()
    data = {
        "room": {"id": 1, "name": "Test room"},
        "players": custom_players,
        "game": {"id": 1, "current_player": 1},
    }

    # second half
    with db_session:
        room = WaitingRoom(**data["room"])
        for player_data in data["players"]:
            room.players.create(**player_data)

        game = Game(waiting_room=room, players=room.players, **data["game"])

    return game


def expect_winner_to_be(players, expected_winner):
    game = create_game_with_custom_players(players)
    with db_session:
        winner = _get_winner(game)
        assert winner == expected_winner


def test_game_where_no_one_wins():
    players = [
        {"id": 1, "username": "Player1", "is_alive": True, "role": "human"},
        {"id": 2, "username": "Player2", "is_alive": True, "role": "human"},
        {"id": 3, "username": "Player3", "is_alive": True, "role": "infected"},
        {"id": 4, "username": "Player4", "is_alive": True, "role": "thing"},
    ]
    expect_winner_to_be(players, None)


def test_the_thing_is_dead():
    players = [
        {"id": 1, "username": "Player1", "is_alive": True, "role": "human"},
        {"id": 2, "username": "Player2", "is_alive": True, "role": "human"},
        {"id": 3, "username": "Player3", "is_alive": True, "role": "infected"},
        {"id": 4, "username": "Player4", "is_alive": False, "role": "thing"},
    ]
    expect_winner_to_be(players, "human")


def test_no_humans_left():
    players = [
        {"id": 1, "username": "Player1", "is_alive": False, "role": "human"},
        {"id": 3, "username": "Player3", "is_alive": True, "role": "infected"},
        {"id": 4, "username": "Player4", "is_alive": True, "role": "infected"},
        {"id": 5, "username": "Player5", "is_alive": True, "role": "thing"},
    ]
    expect_winner_to_be(players, "thing")


def test_one_player_left_is_thing():
    players = [
        {"id": 1, "username": "Player1", "is_alive": False, "role": "human"},
        {"id": 2, "username": "Player2", "is_alive": False, "role": "human"},
        {"id": 3, "username": "Player3", "is_alive": False, "role": "infected"},
        {"id": 4, "username": "Player4", "is_alive": True, "role": "thing"},
    ]
    expect_winner_to_be(players, "thing")


def test_one_player_left_is_human():
    players = [
        {"id": 1, "username": "Player1", "is_alive": True, "role": "human"},
        {"id": 2, "username": "Player2", "is_alive": False, "role": "human"},
        {"id": 3, "username": "Player3", "is_alive": False, "role": "infected"},
        {"id": 4, "username": "Player4", "is_alive": False, "role": "thing"},
    ]
    expect_winner_to_be(players, "human")


def test_the_thing_declares_victory_with_humans_alive():
    players = [
        {"id": 1, "username": "Player1", "is_alive": True, "role": "human"},
        {"id": 2, "username": "Player2", "is_alive": True, "role": "human"},
        {"id": 3, "username": "Player3", "is_alive": False, "role": "infected"},
        {"id": 4, "username": "Player4", "is_alive": True, "role": "thing"},
    ]
    create_game_with_custom_players(players)

    room_id = 1
    with db_session:
        game = Game.get(id=room_id)
        response = client.request(
            "PUT", f"/game/{game.id}/declare-victory", json={"playerID": 4}
        )
        assert response.status_code == 200

    with db_session:
        game = Game.get(id=room_id)
        assert game.have_humans_won is True


def test_the_thing_declares_victory_without_humans_alive():
    players = [
        {"id": 1, "username": "Player1", "is_alive": False, "role": "human"},
        {"id": 2, "username": "Player2", "is_alive": False, "role": "human"},
        {"id": 3, "username": "Player3", "is_alive": False, "role": "infected"},
        {"id": 4, "username": "Player4", "is_alive": True, "role": "thing"},
    ]
    create_game_with_custom_players(players)

    room_id = 1
    with db_session:
        game = Game.get(id=room_id)
        response = client.request(
            "PUT", f"/game/{game.id}/declare-victory", json={"playerID": 4}
        )
        assert response.status_code == 200

    with db_session:
        game = Game.get(id=room_id)
        assert game.have_humans_won is False


def test_all_players_leave_game():
    players = [
        {"id": 1, "username": "Player1", "is_alive": True, "role": "human"},
        {"id": 2, "username": "Player2", "is_alive": True, "role": "human"},
        {"id": 3, "username": "Player3", "is_alive": True, "role": "infected"},
        {"id": 4, "username": "Player4", "is_alive": False, "role": "thing"},
    ]
    expect_winner_to_be(players, "human")

    # salir con todos los jugadores

    room_id = 1

    with db_session:
        game = Game.get(id=room_id)
        _update_game_state(game, "human")
        assert game is not None
        assert WaitingRoom.get(id=room_id) is not None

    for player in players:
        mock_leave_request = PlayerID(playerID=player["id"]).model_dump()
        response = client.request(
            "DELETE", f"/game/{room_id}/leave-game", json=mock_leave_request
        )
        assert response.status_code == 200
        with db_session:
            assert Player.get(id=player["id"]) is None

    with db_session:
        game = Game.get(id=room_id)
        assert game is None
        assert WaitingRoom.get(id=room_id) is None


# Mock _get_winner, _update_game_state, and asyncio.sleep
# async def mock_sleep(seconds):
#    pass


# def test_room_deletion(monkeypatch):
#    monkeypatch.setattr(asyncio, "sleep", mock_sleep)
#    players = [
#        {"id": 1, "username": "Player1", "is_alive": True, "role": "human"},
#        {"id": 2, "username": "Player2", "is_alive": False, "role": "thing"},
#    ]
#    game = create_game_with_custom_players(players)
#    game_id = game.id
#
#    async def run_test():
#        with db_session:
#            game = Game.get(id=game_id)
#            await end_game_if_conditions_are_met(game)
#            assert WaitingRoom.get(id=game_id) is None
#            assert Game.get(id=game_id) is None
#
#    asyncio.run(run_test())

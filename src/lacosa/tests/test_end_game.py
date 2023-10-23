from models import Game, WaitingRoom, db
from pony.orm import db_session, commit
from lacosa.game.utils.game_ender import _get_winner, _update_game_state, end_game_if_conditions_are_met
import lacosa.game.utils.game_ender as game_ender
import asyncio
import pytest


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

        game = Game(
            waiting_room=room,
            players=room.players,
            **data["game"]
        )

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


# Mock _get_winner, _update_game_state, and asyncio.sleep
async def mock_sleep(seconds):
    pass


def test_room_deletion(monkeypatch):
    monkeypatch.setattr(asyncio, "sleep", mock_sleep)
    players = [
        {"id": 1, "username": "Player1", "is_alive": True, "role": "human"},
        {"id": 2, "username": "Player2", "is_alive": False, "role": "thing"},
    ]
    game = create_game_with_custom_players(players)
    game_id = game.id

    async def run_test():
        with db_session:
            game = Game.get(id=game_id)
            await end_game_if_conditions_are_met(game)
            assert WaitingRoom.get(id=game_id) is None
            assert Game.get(id=game_id) is None

    asyncio.run(run_test())

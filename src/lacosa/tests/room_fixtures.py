from models import WaitingRoom, Game, db
from pony.orm import db_session
import pytest


@pytest.fixture()
def db_room_creation():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()

    with db_session:
        room = WaitingRoom(id=0, name="Test Room2", max_players=6, min_players=3)
        room.players.create(id=1, username="Test_player1",
                            is_host=True, position=1)


@pytest.fixture()
def db_room_creation_with_players():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()
    with db_session:
        room = WaitingRoom(id=0, name="Test_room")
        room.players.create(id=1, username="Test_player", is_host=True, position=1)
        room.players.create(id=2, username="Test_player2", is_host=False, position=2)
        room.players.create(id=3, username="Test_player3", is_host=False, position=3)


@pytest.fixture()
def create_rooms_and_return_expected():
    """
    Populates the test database with predefined data using Pony ORM.
    """
    room1_data = {
        "id": 1,
        "name": "Room 1",
        "player_amount": 2,
        "min_players": 3,
        "max_players": 6
    }
    room2_data = {
        "id": 2,
        "name": "Room 2",
        "player_amount": 1,
        "min_players": 2,
        "max_players": 4
    }
    ignore_keys_for_db = {"player_amount"}

    db.drop_all_tables(with_all_data=True)
    db.create_tables()
    with db_session:
        room1 = WaitingRoom(
            **{k: v for k, v in room1_data.items() if k not in ignore_keys_for_db})
        room1.players.create(username='player1')
        room1.players.create(username='player2')

        room2 = WaitingRoom(
            **{k: v for k, v in room2_data.items() if k not in ignore_keys_for_db})
        room2.players.create(username='player3')

    return room1_data, room2_data

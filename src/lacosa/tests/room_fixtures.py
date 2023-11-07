from models import WaitingRoom, db
from pony.orm import db_session
import pytest


@pytest.fixture()
def db_room_creation():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()

    with db_session:
        room = WaitingRoom(id=0, name="Test Room2",
                           max_players=6, min_players=3)
        room.players.create(id=1, username="Test_player1",
                            is_host=True, position=1)


@pytest.fixture()
def db_room_creation_with_players():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()
    with db_session:
        room = WaitingRoom(id=0, name="Test_room")
        room.players.create(id=1, username="Test_player",
                            is_host=True, position=1)
        room.players.create(id=2, username="Test_player2",
                            is_host=False, position=2)
        room.players.create(id=3, username="Test_player3",
                            is_host=False, position=3)


@pytest.fixture()
def create_rooms_and_return_expected():
    """
    Populates the test database with predefined data using Pony ORM.
    """
    room1_data = {
        "id": 1,
        "name": "Room 1",
        "playerAmount": 2,
        "minPlayers": 3,
        "maxPlayers": 6
    }
    room2_data = {
        "id": 2,
        "name": "Room 2",
        "playerAmount": 1,
        "minPlayers": 2,
        "maxPlayers": 4
    }

    db.drop_all_tables(with_all_data=True)
    db.create_tables()
    with db_session:
        room1 = WaitingRoom(
            name=room1_data["name"],
            id=room1_data["id"],
            min_players=room1_data["minPlayers"],
            max_players=room1_data["maxPlayers"],
        )
        room1.players.create(username='player1')
        room1.players.create(username='player2')

        room2 = WaitingRoom(
            name=room2_data["name"],
            id=room2_data["id"],
            min_players=room2_data["minPlayers"],
            max_players=room2_data["maxPlayers"],
        )
        room2.players.create(username='player3')

    return room1_data, room2_data

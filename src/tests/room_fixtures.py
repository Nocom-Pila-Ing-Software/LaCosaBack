from models import WaitingRoom, Player, db
from pony.orm import db_session
import pytest

"""
class WaitingRoom(db.Entity):
    id = PrimaryKey(int, auto=True)
    room_name = Required(str)
    game = Optional(Game)
    players = Set('Player')


class Player(db.Entity):
    id = PrimaryKey(int, auto=True)
    game = Optional(Game)
    room = Required(WaitingRoom)
    username = Required(str)
    role = Required(str, default="human")
    is_host = Required(bool, default=False)
    is_alive = Required(bool, default=True)
    cards = Set('Card')
"""

@pytest.fixture()
def db_room_creation():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()

    with db_session:
        room = WaitingRoom(id=0, room_name="Test Room2")
        room.players.create(id=1, username="Test_player1", is_host=True)

@pytest.fixture(scope="module")
def db_room_creation_with_players():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()
    with db_session:
        room = WaitingRoom(id=0, room_name="Test_room")
        room.players.create(id=1, username="Test_player", is_host=True)
        room.players.create(id=2, username="Test_player2", is_host=False)
        room.players.create(id=3, username="Test_player3", is_host=False)
    yield
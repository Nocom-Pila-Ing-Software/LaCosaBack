from models import WaitingRoom, Player, db
from pony.orm import db_session
import pytest

@pytest.fixture()
def db_room_creation():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()

    with db_session:
        room = WaitingRoom(id=0, room_name="Test Room2")
        room.players.create(id=1, username="Test_player1", is_host=True, position=1)

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

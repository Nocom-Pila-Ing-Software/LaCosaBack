from models import WaitingRoom, db
from pony.orm import db_session
import pytest


@pytest.fixture(scope="module")
def db_room_creation():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()

    with db_session:
        room = WaitingRoom(id=0, room_name="Test Room2")

@pytest.fixture()
def setup_database():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()
    with db_session:
        WaitingRoom(id=0, room_name="Test_room")
        WaitingRoom(id=1, room_name="Test_room2")
    yield
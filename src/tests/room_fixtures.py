from models import Game, WaitingRoom, Player, Card, db
from pony.orm import db_session
import pytest
from typing import List, Dict


@pytest.fixture(scope="module")
def db_room_creation():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()

    with db_session:
        room = WaitingRoom(id=0, room_name="Test Room2")

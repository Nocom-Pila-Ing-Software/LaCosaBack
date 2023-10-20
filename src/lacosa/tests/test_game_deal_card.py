from main import app
from fastapi.testclient import TestClient
from models import Game, WaitingRoom, Player, db
from pony.orm import db_session
from lacosa.schemas import PlayerID
import pytest

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_test_environment():
    global db
    db.drop_all_tables(with_all_data=True)
    db.create_tables()
    with db_session:
        room = WaitingRoom(id=0, name="Test room")
        player = Player(id=1, username="Player1", room=room)
        room.players.add(player)
        game = Game(id=0, waiting_room=room, players=room.players, current_player=1)
        game.cards.create(name="Lanzallamas")

        room = WaitingRoom(id=1, name="Test room")
        player = Player(id=2, username="Player2", room=room)
        room.players.add(player)
        game = Game(id=1, waiting_room=room, players=room.players, current_player=2)
        for i in range(40):
            if i % 2 == 0:
                game.cards.create(name="Lanzallamas")
            else:
                game.cards.create(name="Carta Mazo")
        for _ in range(5):
            player.cards.create(name="Carta Mano")

        room = WaitingRoom(id=2, name="Test room")
        player = Player(id=3, username="Player3", room=room)
        room.players.add(player)
        game = Game(id=2, waiting_room=room, players=room.players, current_player=3)

def test_draw_card_success(setup_test_environment):
    mock_draw_request = PlayerID(playerID=1).model_dump()
    response = client.put("/game/0/draw-card", json=mock_draw_request)
    assert response.status_code == 200
    assert response.json() == None

def test_draw_card_invalid_game_id(setup_test_environment):
    mock_draw_request = PlayerID(playerID=1).model_dump()
    response = client.put("/game/666/draw-card", json=mock_draw_request)
    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found"}

def test_draw_card_invalid_player_id(setup_test_environment):
    mock_draw_request = PlayerID(playerID=666).model_dump()
    response = client.put("/game/1/draw-card", json=mock_draw_request)
    assert response.status_code == 400
    assert response.json() == {"detail": "Player not found"}

def test_draw_card_player_not_in_game(setup_test_environment):
    mock_draw_request = PlayerID(playerID=2).model_dump()
    response = client.put("/game/0/draw-card", json=mock_draw_request)
    assert response.status_code == 404
    assert response.json() == {"detail": "Player not in game"}

def test_draw_card_player_already_has_cards(setup_test_environment):
    mock_draw_request = PlayerID(playerID=2).model_dump()
    response = client.put("/game/1/draw-card", json=mock_draw_request)
    assert response.status_code == 400
    assert response.json() == {"detail": "Player already has a card"}

def test_draw_card_no_cards_left(setup_test_environment):
    mock_draw_request = PlayerID(playerID=3).model_dump()
    response = client.put("/game/2/draw-card", json=mock_draw_request)
    assert response.status_code == 404
    assert response.json() == {"detail": "No cards left in deck"}

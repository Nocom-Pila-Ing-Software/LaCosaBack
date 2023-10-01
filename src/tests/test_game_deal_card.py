from main import app
from fastapi.testclient import TestClient
from models import Game, WaitingRoom, Player, db
from pony.orm import db_session
from schemas.game import PlayerID
import pytest

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_test_environment():
    global db
    db.drop_all_tables(with_all_data=True)
    db.create_tables()
    with db_session:
        #crear una waiting room con un jugador sin deck
        room = WaitingRoom(id=0, room_name="Test room")
        player = Player(id=1, username="Player1", room=room)
        room.players.add(player)
        game = Game(id=0, waiting_room=room, players=room.players)
        game.cards.create(name="Lanzallamas")

        #crear una waiting room con otro jugador con una mano de 4 cartas y un deck de 40 cartas
        room = WaitingRoom(id=1, room_name="Test room")
        player = Player(id=2, username="Player2", room=room)
        room.players.add(player)
        game = Game(id=1, waiting_room=room, players=room.players)
        for i in range(40):
            if i % 2 == 0:
                game.cards.create(name="Lanzallamas")
            else:
                game.cards.create(name="Carta Mazo")
        for _ in range(5):
            player.cards.create(name="Carta Mano")

        #crear una waiting room con otro jugador con una mano de 4 cartas y un deck de 0 cartas
        room = WaitingRoom(id=2, room_name="Test room")
        player = Player(id=3, username="Player3", room=room)
        room.players.add(player)
        game = Game(id=2, waiting_room=room, players=room.players)

def test_draw_card_success(setup_test_environment):
    mock_draw_request = PlayerID(playerID=1).model_dump()
    response = client.put("/game/0/deal-card", json=mock_draw_request)
    assert response.status_code == 200
    assert response.json() == None

def test_draw_card_invalid_game_id(setup_test_environment):
    mock_draw_request = PlayerID(playerID=1).model_dump()
    response = client.put("/game/666/deal-card", json=mock_draw_request)
    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found"}

def test_draw_card_invalid_player_id(setup_test_environment):
    mock_draw_request = PlayerID(playerID=666).model_dump()
    response = client.put("/game/1/deal-card", json=mock_draw_request)
    assert response.status_code == 404
    assert response.json() == {"detail": "Player not found"}  

def test_draw_card_player_not_in_game(setup_test_environment):
    mock_draw_request = PlayerID(playerID=2).model_dump()
    response = client.put("/game/0/deal-card", json=mock_draw_request)
    assert response.status_code == 404
    assert response.json() == {"detail": "Player not in game"}  

def test_draw_card_player_already_has_cards(setup_test_environment):
    mock_draw_request = PlayerID(playerID=2).model_dump()
    response = client.put("/game/1/deal-card", json=mock_draw_request)
    assert response.status_code == 400
    assert response.json() == {"detail": "Player already has a card"}

def test_draw_card_no_cards_left(setup_test_environment):
    mock_draw_request = PlayerID(playerID=3).model_dump()
    response = client.put("/game/2/deal-card", json=mock_draw_request)
    assert response.status_code == 404
    assert response.json() == {"detail": "No cards left in deck"}

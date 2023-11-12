from unittest.mock import MagicMock
from unittest.mock import patch
from main import app
from fastapi.testclient import TestClient
from models import Game, WaitingRoom, Player, db
from pony.orm import db_session
from lacosa.schemas import PlayerID
import pytest
from .game_fixtures import deck_with_panic_card

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
        game = Game(id=0, waiting_room=room,
                    players=room.players, current_player=1)
        game.cards.create(name="Lanzallamas")

        room = WaitingRoom(id=1, name="Test room")
        player = Player(id=2, username="Player2", room=room)
        room.players.add(player)
        game = Game(id=1, waiting_room=room,
                    players=room.players, current_player=2)
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
        game = Game(id=2, waiting_room=room,
                    players=room.players, current_player=3)


def test_draw_card_success(setup_test_environment):
    mock_draw_request = PlayerID(playerID=1).model_dump()
    response = client.put("/game/0/deal-card", json=mock_draw_request)
    assert response.status_code == 200
    assert response.json() is None


def test_draw_card_invalid_game_id(setup_test_environment):
    mock_draw_request = PlayerID(playerID=1).model_dump()
    response = client.put("/game/666/deal-card", json=mock_draw_request)
    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found"}


def test_draw_card_invalid_player_id(setup_test_environment):
    mock_draw_request = PlayerID(playerID=666).model_dump()
    response = client.put("/game/1/deal-card", json=mock_draw_request)
    assert response.status_code == 400
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


def test_draw_panic_card(deck_with_panic_card):
    data = deck_with_panic_card
    p1 = data["players"][0]
    game_id = data["game"]["id"]
    mock_card = MagicMock()
    mock_card.type = "panic"
    mock_card.name = "Revelaciones"

    # Mocking Deck.get_card_from_deck
    with patch('lacosa.game.utils.deck.Deck.get_card_from_deck') as mock_get_card:
        # Create a mock card object with "type" and "name" attributes
        mock_get_card.return_value = mock_card

        req = PlayerID(playerID=p1["id"]).model_dump()
        response = client.put(f"/game/{game_id}/deal-card", json=req)

        assert response.status_code == 200

        with db_session:
            game = Game.get(id=game_id)
            assert game.current_action == "revelations"

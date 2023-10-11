from main import app
from fastapi.testclient import TestClient
from models import Game
from pony.orm import db_session, select
from schemas.schemas import PlayerID, GameID, CardInfo
from lacosa.game.schemas import GameCreationRequest, PublicPlayerInfo, GameStatus, PlayCardRequest
import pytest
from .game_fixtures import db_game_creation, db_game_status, db_game_creation_with_cards

client = TestClient(app)


def test_create_game_success(db_game_creation):
    mock_creation_request = GameCreationRequest(
        roomID=0,
        players=[
            PlayerID(playerID=1),
            PlayerID(playerID=2),
        ]
    ).model_dump()

    creation_response = GameID(gameID=1).model_dump()

    response = client.post("/game", json=mock_creation_request)
    data = response.json()

    with db_session:
        game_record = select(g for g in Game if g.id ==
                             int(data["gameID"])).get()
        the_thing = select(p for p in game_record.players if p.role == "thing")
        current_players = list(select(
            p for p in game_record.players if p.role == "thing"
        ))

        # Game was created
        assert game_record is not None

        # Deck was created
        assert len(game_record.cards) > 0

        # Players were created
        assert len(game_record.players) > 0

        # The thing role was assigned
        assert the_thing.exists()

        # The thing has 'La Cosa' card
        assert (
            the_thing.get().cards
            .select(lambda c: c.name == "La Cosa")
            .exists()
        )

        # all players have 4 cards
        assert all(p.cards.count() == 4 for p in current_players)

    assert response.status_code == 201
    assert data == creation_response


def test_invalid_room_id(db_game_creation):
    mock_creation_request = GameCreationRequest(
        roomID=666,
        players=[
            PlayerID(playerID=1),
            PlayerID(playerID=2),
        ]
    ).model_dump()
    response = client.post("/game", json=mock_creation_request)
    assert response.status_code == 404
    assert response.json() == {"detail": "Room ID doesn't exist"}


def test_get_game_status(db_game_status):
    expected_response = db_game_status.model_dump()
    response = client.get("/game/1")
    assert response.status_code == 200
    assert response.json() == expected_response


def test_get_game_status_invalid_id():
    response = client.get("/game/666")
    assert response.status_code == 404


def test_play_card(db_game_creation_with_cards):
    mock_play_request = PlayCardRequest(
        playerID=1,
        targetPlayerID=2,
        cardID=0
    ).model_dump()

    response = client.put("/game/5/play-card", json=mock_play_request)

    assert response.status_code == 200

    response = client.get("/game/5")
    # The last played card is correct
    assert response.json()["lastPlayedCard"] == {
        "cardID": 0,
        "name": "Lanzallamas",
        "description": "Está que arde"
    }
    with db_session:
        # The card was removed from the player
        player_list = list(Game.get(id=5).players)
        assert not player_list[0].cards.filter(id=0).exists()

        # The card was added to the game
        assert Game.get(id=5).cards.filter(id=0).exists()


    # The target player is dead
    assert response.json()["players"] == [

        {
            "playerID": 1,
            "username": "Player1",
            "is_host": True,
            "is_alive": True
        },
        {
            "playerID": 3,
            "username": "Player3",
            "is_host": False,
            "is_alive": True
        }
    ]

    assert response.json()["deadPlayers"] == [
        {
            "playerID": 2,
            "username": "Player2",
            "is_host": False,
            "is_alive": False
        }
    ]


def test_play_card_invalid_player(db_game_creation_with_cards):
    mock_play_request = PlayCardRequest(
        playerID=666,
        targetPlayerID=2,
        cardID=0
    ).model_dump()

    response = client.put("/game/5/play-card", json=mock_play_request)

    assert response.status_code == 400
    assert response.json() == {"detail": "Player not found"}


def test_play_card_invalid_card(db_game_creation_with_cards):
    mock_play_request = PlayCardRequest(
        playerID=1,
        targetPlayerID=2,
        cardID=666
    ).model_dump()

    response = client.put("/game/5/play-card", json=mock_play_request)

    assert response.status_code == 400
    assert response.json() == {"detail": "Card not found"}


def test_play_card_invalid_target(db_game_creation_with_cards):
    mock_play_request = PlayCardRequest(
        playerID=1,
        targetPlayerID=666,
        cardID=0
    ).model_dump()

    response = client.put("/game/5/play-card", json=mock_play_request)

    assert response.status_code == 400
    assert response.json() == {"detail": "Player not found"}

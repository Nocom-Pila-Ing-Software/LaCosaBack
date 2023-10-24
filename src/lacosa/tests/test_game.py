from main import app
from fastapi.testclient import TestClient
from models import Game, WaitingRoom, Player, Card
from pony.orm import db_session, select
from lacosa.schemas import PlayerID, GameID, CardInfo
from lacosa.game.schemas import GameCreationRequest, PlayCardRequest, GenericCardRequest
import pytest
from .game_fixtures import db_game_creation, db_game_status, db_game_creation_with_cards, db_game_creation_with_cards_2
import pdb

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

        # The thing has 'La cosa' card
        assert (
            the_thing.get().cards
            .select(lambda c: c.name == "La cosa")
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
    assert response.json() == {"detail": "Room not found"}


def test_get_game_status(db_game_status):
    expected_response = db_game_status.model_dump()
    response = client.get("/game/1")
    assert response.status_code == 200
    assert response.json() == expected_response


def test_get_game_status_invalid_id():
    response = client.get("/game/666")
    assert response.status_code == 404


def test_play_Lanzallamas_card_no_defended(db_game_creation_with_cards):
    mock_play_request = PlayCardRequest(
        playerID=1,
        targetPlayerID=2,
        cardID=4
    ).model_dump()

    response = client.put("/game/5/play-card", json=mock_play_request)

    assert response.status_code == 200

    response = client.get("/game/5")

    # The target player is dead
    assert response.json()["players"] == [

        {
            "playerID": 1,
            "username": "Player1",
            "is_host": True,
            "is_alive": True
        },
        {
            "playerID": 2,
            "username": "Player2",
            "is_host": False,
            "is_alive": True
        },
        {
            "playerID": 3,
            "username": "Player3",
            "is_host": False,
            "is_alive": True
        }
    ]

    # Check event was created
    with db_session:
        game_record = select(g for g in Game if g.id == 5).get()
        event_record = select(e for e in game_record.events).get()
        assert event_record.player1.id == 1
        assert event_record.player2.id == 2
        assert event_record.card1.id == 4
        assert event_record.type == "action"
        assert event_record.is_completed == False
        assert event_record.is_successful == False

    # no defenderse de la carta
    mock_play_request = GenericCardRequest(
        playerID=2,
        cardID=-1
    ).model_dump()

    response = client.put("/game/5/defend-card", json=mock_play_request)
    assert response.status_code == 200

    response = client.get("/game/5")

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


def test_play_vigila_tus_espaldas_card_no_defended(db_game_creation_with_cards_2):
    mock_play_request = PlayCardRequest(
        playerID=3,
        targetPlayerID=3,
        cardID=10
    ).model_dump()

    response = client.put("/game/5/play-card", json=mock_play_request)

    assert response.status_code == 200

    response = client.get("/game/5")

    # The target player is dead
    assert response.json()["players"] == [
        {
            "playerID": 4,
            "username": "Player4",
            "is_host": False,
            "is_alive": True
        },
        {
            "playerID": 3,
            "username": "Player3",
            "is_host": False,
            "is_alive": True
        },
        {
            "playerID": 2,
            "username": "Player2",
            "is_host": False,
            "is_alive": True
        },
        {
            "playerID": 1,
            "username": "Player1",
            "is_host": True,
            "is_alive": True
        }
    ]


def test_play_cambio_de_lugar_card_no_defended(db_game_creation_with_cards):
    mock_play_request = PlayCardRequest(
        playerID=1,
        targetPlayerID=2,
        cardID=5
    ).model_dump()

    response = client.put("/game/5/play-card", json=mock_play_request)

    assert response.status_code == 200

    response = client.get("/game/5")

    # The target player is dead
    assert response.json()["players"] == [

        {
            "playerID": 1,
            "username": "Player1",
            "is_host": True,
            "is_alive": True
        },
        {
            "playerID": 2,
            "username": "Player2",
            "is_host": False,
            "is_alive": True
        },
        {
            "playerID": 3,
            "username": "Player3",
            "is_host": False,
            "is_alive": True
        }
    ]

    # Check event was created
    with db_session:
        game_record = select(g for g in Game if g.id == 5).get()
        event_record = select(e for e in game_record.events).get()
        assert event_record.player1.id == 1
        assert event_record.player2.id == 2
        assert event_record.card1.id == 5
        assert event_record.type == "action"
        assert event_record.is_completed == False
        assert event_record.is_successful == False

    # no defenderse de la carta
    mock_play_request = GenericCardRequest(
        playerID=2,
        cardID=-1
    ).model_dump()

    response = client.put("/game/5/defend-card", json=mock_play_request)
    assert response.status_code == 200

    response = client.get("/game/5")

    assert response.json()["players"] == [

        {
            "playerID": 2,
            "username": "Player2",
            "is_host": False,
            "is_alive": True
        },
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

    assert response.json()["deadPlayers"] == []


def test_play_mas_vale_que_corras_card_no_defended(db_game_creation_with_cards):
    mock_play_request = PlayCardRequest(
        playerID=1,
        targetPlayerID=2,
        cardID=6
    ).model_dump()

    response = client.put("/game/5/play-card", json=mock_play_request)

    assert response.status_code == 200

    response = client.get("/game/5")

    # The target player is dead
    assert response.json()["players"] == [

        {
            "playerID": 1,
            "username": "Player1",
            "is_host": True,
            "is_alive": True
        },
        {
            "playerID": 2,
            "username": "Player2",
            "is_host": False,
            "is_alive": True
        },
        {
            "playerID": 3,
            "username": "Player3",
            "is_host": False,
            "is_alive": True
        }
    ]

    # Check event was created
    with db_session:
        game_record = select(g for g in Game if g.id == 5).get()
        event_record = select(e for e in game_record.events).get()
        assert event_record.player1.id == 1
        assert event_record.player2.id == 2
        assert event_record.card1.id == 6
        assert event_record.type == "action"
        assert event_record.is_completed == False
        assert event_record.is_successful == False

    # no defenderse de la carta
    mock_play_request = GenericCardRequest(
        playerID=2,
        cardID=-1
    ).model_dump()

    response = client.put("/game/5/defend-card", json=mock_play_request)
    assert response.status_code == 200

    response = client.get("/game/5")

    assert response.json()["players"] == [

        {
            "playerID": 2,
            "username": "Player2",
            "is_host": False,
            "is_alive": True
        },
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

    assert response.json()["deadPlayers"] == []


def test_play_cambio_de_lugar_card_defended(db_game_creation_with_cards):
    mock_play_request = PlayCardRequest(
        playerID=1,
        targetPlayerID=2,
        cardID=5
    ).model_dump()

    response = client.put("/game/5/play-card", json=mock_play_request)

    assert response.status_code == 200

    response = client.get("/game/5")

    # The target player is dead
    assert response.json()["players"] == [

        {
            "playerID": 1,
            "username": "Player1",
            "is_host": True,
            "is_alive": True
        },
        {
            "playerID": 2,
            "username": "Player2",
            "is_host": False,
            "is_alive": True
        },
        {
            "playerID": 3,
            "username": "Player3",
            "is_host": False,
            "is_alive": True
        }
    ]

    # Check event was created
    with db_session:
        game_record = select(g for g in Game if g.id == 5).get()
        event_record = select(e for e in game_record.events).get()
        assert event_record.player1.id == 1
        assert event_record.player2.id == 2
        assert event_record.card1.id == 5
        assert event_record.type == "action"
        assert event_record.is_completed == False
        assert event_record.is_successful == False

    # defenderse de la carta con aqui estoy bien
    mock_play_request = GenericCardRequest(
        playerID=2,
        cardID=7
    ).model_dump()

    response = client.put("/game/5/defend-card", json=mock_play_request)
    assert response.status_code == 200

    response = client.get("/game/5")

    assert response.json()["players"] == [

        {
            "playerID": 1,
            "username": "Player1",
            "is_host": True,
            "is_alive": True
        },
        {
            "playerID": 2,
            "username": "Player2",
            "is_host": False,
            "is_alive": True
        },
        {
            "playerID": 3,
            "username": "Player3",
            "is_host": False,
            "is_alive": True
        }
    ]

    # Check event was completed correctly
    with db_session:
        game_record = select(g for g in Game if g.id == 5).get()
        event_record = select(
            e for e in game_record.events if e.type == "action" and e.is_completed == True
        ).order_by(lambda e: e.id).first()
        assert event_record.player1.id == 1
        assert event_record.player2.id == 2
        assert event_record.card1.id == 5
        assert event_record.card2.id == 7
        assert event_record.type == "action"
        assert event_record.is_completed == True
        assert event_record.is_successful == False


def test_play_seduccion(db_game_creation_with_cards_2):
    mock_play_request = PlayCardRequest(
        playerID=2,
        targetPlayerID=1,
        cardID=9
    ).model_dump()

    with db_session:
        game_record = select(g for g in Game if g.id == 5).get()
        game_record.current_player = 2
        game_record.current_action = "action"

    response = client.put("/game/5/play-card", json=mock_play_request)

    assert response.status_code == 200

    # Check event was created
    with db_session:
        game_record = select(g for g in Game if g.id == 5).get()
        event_record = select(
            e for e in game_record.events if e.type == "action").get()
        assert event_record.player1.id == 2
        assert event_record.player2.id == 1
        assert event_record.card1.id == 9
        assert event_record.type == "action"
        assert event_record.is_completed == True
        assert event_record.is_successful == True

        event_trade = select(
            e for e in game_record.events if e.type == "trade").get()

        assert event_trade.player1.id == 2
        assert event_trade.player2.id == 1
        assert event_trade.type == "trade"
        assert event_trade.is_completed == False
        assert event_trade.is_successful == False

        assert game_record.last_played_card.id == 9
        assert game_record.current_player == 2
        assert game_record.current_action == "trade"

    mock_trade_request = GenericCardRequest(
        playerID=2,
        cardID=8
    ).model_dump()

    response = client.put("/game/5/trade-card", json=mock_trade_request)

    assert response.status_code == 200

    mock_trade_request = GenericCardRequest(
        playerID=1,
        cardID=5
    ).model_dump()

    response = client.put("/game/5/trade-card", json=mock_trade_request)

    assert response.status_code == 200

    with db_session:
        game_record = select(g for g in Game if g.id == 5).get()
        event_trade = select(
            e for e in game_record.events if e.type == "trade").get()

        assert event_trade.player1.id == 2
        assert event_trade.player2.id == 1
        assert event_trade.card1.id == 8
        assert event_trade.card2.id == 5
        assert event_trade.type == "trade"
        assert event_trade.is_completed == True
        assert event_trade.is_successful == True

        assert game_record.current_player == 3
        assert game_record.current_action == "draw"


def test_play_mas_vale_que_corras_card_defended(db_game_creation_with_cards):
    mock_play_request = PlayCardRequest(
        playerID=1,
        targetPlayerID=2,
        cardID=6
    ).model_dump()

    response = client.put("/game/5/play-card", json=mock_play_request)

    assert response.status_code == 200

    response = client.get("/game/5")

    # The target player is dead
    assert response.json()["players"] == [

        {
            "playerID": 1,
            "username": "Player1",
            "is_host": True,
            "is_alive": True
        },
        {
            "playerID": 2,
            "username": "Player2",
            "is_host": False,
            "is_alive": True
        },
        {
            "playerID": 3,
            "username": "Player3",
            "is_host": False,
            "is_alive": True
        }
    ]

    # Check event was created
    with db_session:
        game_record = select(g for g in Game if g.id == 5).get()
        event_record = select(e for e in game_record.events).get()
        assert event_record.player1.id == 1
        assert event_record.player2.id == 2
        assert event_record.card1.id == 6
        assert event_record.type == "action"
        assert event_record.is_completed == False
        assert event_record.is_successful == False

    # defenderse de la carta con aqui estoy bien
    mock_play_request = GenericCardRequest(
        playerID=2,
        cardID=7
    ).model_dump()

    response = client.put("/game/5/defend-card", json=mock_play_request)
    assert response.status_code == 200

    response = client.get("/game/5")

    assert response.json()["players"] == [

        {
            "playerID": 1,
            "username": "Player1",
            "is_host": True,
            "is_alive": True
        },
        {
            "playerID": 2,
            "username": "Player2",
            "is_host": False,
            "is_alive": True
        },
        {
            "playerID": 3,
            "username": "Player3",
            "is_host": False,
            "is_alive": True
        }
    ]

    # Check event was completed correctly
    with db_session:
        game_record = select(g for g in Game if g.id == 5).get()
        event_record = select(
            e for e in game_record.events if e.type == "action" and e.is_completed == True
        ).order_by(lambda e: e.id).first()
        assert event_record.player1.id == 1
        assert event_record.player2.id == 2
        assert event_record.card1.id == 6
        assert event_record.card2.id == 7
        assert event_record.type == "action"
        assert event_record.is_completed == True
        assert event_record.is_successful == False


def test_play_Lanzallamas_card_defended(db_game_creation_with_cards):
    mock_play_request = PlayCardRequest(
        playerID=1,
        targetPlayerID=2,
        cardID=4
    ).model_dump()

    response = client.put("/game/5/play-card", json=mock_play_request)

    assert response.status_code == 200

    response = client.get("/game/5")

    # The target player is dead
    assert response.json()["players"] == [

        {
            "playerID": 1,
            "username": "Player1",
            "is_host": True,
            "is_alive": True
        },
        {
            "playerID": 2,
            "username": "Player2",
            "is_host": False,
            "is_alive": True
        },
        {
            "playerID": 3,
            "username": "Player3",
            "is_host": False,
            "is_alive": True
        }
    ]

    # Check event was created
    with db_session:
        game_record = select(g for g in Game if g.id == 5).get()
        event_record = select(e for e in game_record.events).get()
        assert event_record.player1.id == 1
        assert event_record.player2.id == 2
        assert event_record.card1.id == 4
        assert event_record.type == "action"
        assert event_record.is_completed == False
        assert event_record.is_successful == False

    # defenderse de la carta con aqui estoy bien
    mock_play_request = GenericCardRequest(
        playerID=2,
        cardID=8
    ).model_dump()

    response = client.put("/game/5/defend-card", json=mock_play_request)
    assert response.status_code == 200

    response = client.get("/game/5")

    assert response.json()["players"] == [

        {
            "playerID": 1,
            "username": "Player1",
            "is_host": True,
            "is_alive": True
        },
        {
            "playerID": 2,
            "username": "Player2",
            "is_host": False,
            "is_alive": True
        },
        {
            "playerID": 3,
            "username": "Player3",
            "is_host": False,
            "is_alive": True
        }
    ]

    # Check event was completed correctly
    with db_session:
        game_record = select(g for g in Game if g.id == 5).get()
        event_record = select(
            e for e in game_record.events if e.type == "action" and e.is_completed == True
        ).order_by(lambda e: e.id).first()
        assert event_record.player1.id == 1
        assert event_record.player2.id == 2
        assert event_record.card1.id == 4
        assert event_record.card2.id == 8
        assert event_record.type == "action"
        assert event_record.is_completed == True
        assert event_record.is_successful == False
        assert event_record.game.last_played_card.id == 8


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


def test_defense_card_invalid_phase(db_game_creation_with_cards):
    mock_play_request = GenericCardRequest(
        playerID=1,
        cardID=5
    ).model_dump()

    with db_session:
        # create event to defend
        game_record = select(g for g in Game if g.id == 5).get()
        game_record.events.create(
            player1=game_record.players.select(lambda p: p.id == 2).get(),
            player2=game_record.players.select(lambda p: p.id == 1).get(),
            card1=game_record.cards.select(lambda c: c.id == 5).get(),
            type="action",
            is_completed=False,
            is_successful=False
        )

    response = client.put("/game/5/defend-card", json=mock_play_request)

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Player not has permission to execute this action"}

# no se actualiza la base de datos por cada modulo


def test_game_is_over(db_game_creation_with_cards):
    mock_play_request = PlayCardRequest(
        playerID=1,
        targetPlayerID=2,
        cardID=4
    ).model_dump()
    response = client.put("/game/5/play-card", json=mock_play_request)

    assert response.status_code == 200
    response = client.get("/game/5")

    assert response.json()["result"]["isGameOver"] == True

    mock_play_request = PlayCardRequest(
        playerID=3,
        targetPlayerID=1,
        cardID=60
    ).model_dump()

    response = client.put("/game/5/play-card", json=mock_play_request)

    assert response.status_code == 200

    response = client.get("/game/5")
    # FIXME: this doesn't work, is harcoded
    """
    assert response.json()["result"]["isGameOver"] == False

    with db_session:
        assert not Game.exists(id=5)
        #verificar si se borro room
        assert not WaitingRoom.exists(id=0)
        assert not Player.exists(id=1)
        assert not Player.exists(id=2)
        assert not Player.exists(id=3)
        assert not Card.exists(id=4)
        assert not Card.exists(id=60)
    """

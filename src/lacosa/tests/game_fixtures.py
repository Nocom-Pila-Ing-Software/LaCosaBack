import random
from models import Event, Game, WaitingRoom, Player, Card, db
from pony.orm import db_session, select
from lacosa.game.schemas import PublicPlayerInfo, GameStatus
from lacosa.schemas import PlayerID, CardInfo
import pytest
from typing import List, Dict


@pytest.fixture(scope="module")
def db_game_creation():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()

    with db_session:
        # Create a waiting room with players for testing
        room = WaitingRoom(id=0, name="Test room")
        room.players.create(username="Player1", is_host=True, position=1)
        room.players.create(username="Player2", is_host=False, position=2)


def get_player_data() -> List[Dict]:
    player_data = [
        {"username": "pepito", "is_host": True, "is_alive": True},
        {"username": "fulanito", "is_host": False, "is_alive": True}
    ]
    return player_data


@db_session
def setup_db_game_status(game_data: Dict) -> None:
    room1 = WaitingRoom(name="test room")

    db_players = [
        Player(id=index, room=room1, **player_data)
        for index, player_data in enumerate(game_data["players"], start=1)
    ]
    card = Card(id=1, **game_data["card"])
    # Create a Game instance
    Game(
        id=game_data["game_id"], waiting_room=room1, players=db_players,
        last_played_card=card, current_player=1
    )


def get_game_status_response(game_data: Dict) -> GameStatus:
    schema_players = [
        PublicPlayerInfo(playerID=index, **player_data)
        for index, player_data in enumerate(game_data["players"], start=1)
    ]
    card = CardInfo(cardID=1, **game_data["card"])
    # Create a Game instance
    response = GameStatus(
        gameID=game_data["game_id"],
        players=schema_players,
        deadPlayers=[],
        lastPlayedCard=card,
        playerPlayingTurn=PlayerID(playerID=1),
        currentAction="draw",
        result={
            "isGameOver": False,
            "humansWin": False,
            "winners": []
        },
        events=[]
    )
    return response


@pytest.fixture(scope="module")
def db_game_status():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()

    game_data = {
        "players": get_player_data(),
        "card": {"name": "Lanzallamas", "description": "está que arde"},
        "game_id": 1
    }

    setup_db_game_status(game_data)
    response = get_game_status_response(game_data)
    return response


@pytest.fixture(scope="function")
def db_game_creation_with_cards():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()

    with db_session:
        # Create a waiting room
        room = WaitingRoom(id=0, name="Test room")
        player1 = room.players.create(
            id=1, username="Player1", is_host=True, position=1)
        player2 = room.players.create(
            id=2, username="Player2", is_host=False, position=2)
        player3 = room.players.create(
            id=3, username="Player3", is_host=False, position=3)

        # Create a game with players
        game = Game(id=5, waiting_room=room, current_player=1, current_action="draw",
                    last_played_card=None, players=room.players, events={})

        # añadir player a game
        game.players.add(player1)
        game.players.add(player2)
        game.players.add(player3)

        # crear cartas para el juego
        game.cards.create()
        game.cards.create()
        game.cards.create()

        # Add cards to players
        player1.cards.create(id=4, name="Lanzallamas",
                             description="Está que arde")
        player1.cards.create(id=5, name="Cambio de lugar",
                                description="Cambio de lugar")
        player1.cards.create(id=6, name="Más vale que corras",
                                description="Más vale que corras")

        player2.cards.create(id=7, name="Aquí estoy bien",
                                description="Aquí estoy bien")
        player2.cards.create(id=8, name="Nada de barbacoas",
                                description="Nada de barbacoas")
        player2.cards.create()
        player2.cards.create()

        player3.cards.create(id=60, name="Lanzallamas",
                             description="Está que arde")


@pytest.fixture(scope="module")
def db_game_creation_with_cards_player_data():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()

    with db_session:
        room = WaitingRoom(id=0, name="Test room")
        player = Player(id=1, username="Player", room=room)
        room.players.add(player)
        game = Game(id=0, waiting_room=room,
                    players=room.players, current_player=1)
        for _ in range(5):
            player.cards.create(name="Carta_test", description="Carta test")


discard_card_game_data = {
    "room": {"id": 1, "name": "Test room"},
    "players": [
        {"id": 1, "username": "Player1", "is_host": True, "position": 1},
        {"id": 2, "username": "Player2", "is_host": False, "position": 2}
    ],
    "game": {"id": 1, "current_player": 1},
    "cards": [
        [
            {"id": 1, "name": "card1"},
            {"id": 2, "name": "card2"},
            {"id": 3, "name": "card3"},
            {"id": 4, "name": "card4"},
        ],
        [
            {"id": 5, "name": "card5"},
            {"id": 6, "name": "card6"},
            {"id": 7, "name": "card7"},
            {"id": 8, "name": "card8"},
        ]
    ]
}


@pytest.fixture(scope="module")
def discard_card_game_creation():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()
    # second half
    with db_session:
        room = WaitingRoom(**discard_card_game_data["room"])
        for player_data in discard_card_game_data["players"]:
            room.players.create(**player_data)

        game = Game(
            waiting_room=room,
            players=room.players,
            **discard_card_game_data["game"]
        )
        for player, cards in zip(game.players, discard_card_game_data["cards"]):
            for card in cards:
                player.cards.create(**card)

    return discard_card_game_data


@ pytest.fixture(scope="module")
def db_game_creation_without_cards():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()

    with db_session:
        room = WaitingRoom(id=0, name="Test room")
        player = Player(id=1, username="Player", room=room,
                        is_host=True, position=1)
        room.players.add(player)
        Game(id=0, waiting_room=room, players=room.players, current_player=1)


@pytest.fixture()
def db_game_creation_with_trade_event():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()

    with db_session:
        room = WaitingRoom(id=1, name="Test room")
        for i in range(8):
            player = Player(id=i, username="Player"+str(i),
                            room=room, is_host=i == 1, position=i)
            room.players.add(player)
        game = Game(id=1, waiting_room=room, players=room.players,
                    current_player=random.randint(0, 5), last_played_card=None, current_action="trade", events=[])

        players_in_game = select(p for p in game.players)[:]

        event = Event(id=1, game=game, type="trade", player1=game.current_player,
                      player2=players_in_game[3] if players_in_game[3].id != game.current_player else players_in_game[4])

        Game.get(id=1).events.add(event)

        events_in_game = select(e for e in game.events)[:]

        for i in range(8):
            for j in range(4):
                card = None
                if players_in_game[i] == events_in_game[0].player2:
                    card = players_in_game[i].cards.create(
                        name="No, gracias", description="Carta test defensa")
                else:
                    card = players_in_game[i].cards.create(
                        name="Carta"+str(i*5+j), description="Carta test")
                game.cards.add(card)


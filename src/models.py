from pony.orm import Database, PrimaryKey, Required, Optional, Set
from enum import Enum

db = Database()


class EventType(str, Enum):
    action = "action"
    trade = "trade"


class CardType(str, Enum):
    action = "action"
    defense = "defense"
    special = "special"


class Event(db.Entity):
    id = PrimaryKey(int, auto=True)
    game = Required('Game')
    type = Required(EventType)
    player1 = Required('Player')
    player2 = Required('Player')
    card1 = Optional('Card')
    card2 = Optional('Card')
    is_completed = Required(bool, default=False)
    is_successful = Required(bool, default=False)


class Game(db.Entity):
    id = PrimaryKey(int, auto=True)
    waiting_room = Required('WaitingRoom')
    players = Set('Player')
    cards = Set('Card')
    last_played_card = Optional('Card', reverse="played_on_game")
    current_player = Required(int)
    current_action = Required(str, default="draw")
    is_game_over = Required(bool, default=False)
    have_humans_won = Required(bool, default=False)
    events = Set(Event)


class WaitingRoom(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    game = Optional(Game, cascade_delete=True)
    players = Set('Player')
    min_players = Required(int, default=2)
    max_players = Required(int, default=8)


class Player(db.Entity):
    id = PrimaryKey(int, auto=True)
    game = Optional(Game)
    room = Required(WaitingRoom)
    username = Required(str)
    role = Required(str, default="human")
    is_host = Required(bool, default=False)
    is_alive = Required(bool, default=True)
    cards = Set('Card')
    position = Optional(int)  # becomes 0 when dead

    # I dont know if this is the best way to do this
    events = Set(Event)
    events2 = Set(Event, reverse="player2")


class Card(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, default="Generic card name")
    description = Required(str, default="Generic card description")
    # The following attributes are optional because a card can belong to a Game
    # and not a player and viceversa
    player = Optional(Player)
    deck = Optional(Game)
    is_cancelled_by = Set('Card', reverse="cancels")
    cancels = Set('Card', reverse="is_cancelled_by")

    # This attribute is the counterpart of Game.last_played_card
    played_on_game = Optional(Game, reverse="last_played_card")
    type = Required(CardType, default="action")

    # I dont know if this is the best way to do this
    events = Set(Event)
    events2 = Set(Event, reverse="card2")

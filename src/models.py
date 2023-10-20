from pony.orm import Database, PrimaryKey, Required, Optional, Set


db = Database()


class Game(db.Entity):
    id = PrimaryKey(int, auto=True)
    waiting_room = Required('WaitingRoom')
    players = Set('Player')
    cards = Set('Card')
    last_played_card = Optional('Card', reverse="played_on_game")
    current_player = Required(int)


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
    position = Optional(int)


class Card(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, default="Generic card name")
    type = Required(str, default="Generic card type")
    description = Required(str, default="Generic card description")
    # The following attributes are optional because a card can belong to a Game
    # and not a player and viceversa
    player = Optional(Player)
    deck = Optional(Game)

    # This attribute is the counterpart of Game.last_played_card
    played_on_game = Optional(Game, reverse="last_played_card")

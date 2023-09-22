from pony.orm import Database, PrimaryKey, Required, Optional, Set


db = Database()


class Game(db.Entity):
    id = PrimaryKey(int, auto=True)
    waiting_room = Required('WaitingRoom')
    current_turn = Required(int, default=0)
    players = Set('Player')
    cards = Set('Card')


class WaitingRoom(db.Entity):
    id = PrimaryKey(int, auto=True)
    room_name = Required(str)
    game = Optional(Game)
    players = Set('Player')


class Player(db.Entity):
    id = PrimaryKey(int, auto=True)
    game = Optional(Game)
    room = Required(WaitingRoom)
    username = Required(str)
    role = Required(str, default="human")
    is_host = Required(bool, default=False)
    cards = Set('Card')


class Card(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, default="Generic card name")
    description = Required(str, default="Generic card description")
    # The following attributes are optional because a card can belong to a Game
    # and not a player and viceversa
    player = Optional(Player)
    game = Optional(Game)

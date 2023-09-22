from pony.orm import Database, PrimaryKey, Required, Optional, Set


db = Database()


class Game(db.Entity):
    id = PrimaryKey(int, auto=True)
    waiting_room = Required('WaitingRoom')
    currentTurn = Required(int, default=0)
    players = Set('Player')
    cards = Set('Card')


class WaitingRoom(db.Entity):
    id = PrimaryKey(int, auto=True)
    roomName = Required(str)
    game = Optional(Game)
    players = Set('Player')


class Player(db.Entity):
    id = PrimaryKey(int, auto=True)
    game = Optional(Game)
    room = Required(WaitingRoom)
    username = Required(str)
    role = Required(str, default="human")
    isHost = Required(str, default="F")
    cards = Set('Card')


class Card(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, default="Generic card name")
    description = Required(str, default="Generic card description")
    # The following attributes are optional because a card can belong to a Game
    # and not a player and viceversa
    player = Optional(Player)
    game = Optional(Game)

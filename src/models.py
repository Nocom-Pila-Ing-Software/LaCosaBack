from datetime import time
from pony.orm import *


db = Database()


class Game(db.Entity):
    id = PrimaryKey(int, auto=True)
    waiting_room = Required('WaitingRoom')
    isDirectionLeft = Optional(str)
    currentTurn = Optional(int)
    players = Set('Player')
    cards = Set('Card')
    messages = Set('Message')


class Player(db.Entity):
    id = PrimaryKey(int, auto=True)
    game = Required(Game)
    username = Optional(str)
    isQuarantined = Optional(str)
    role = Optional(str)
    isHost = Optional(str)
    cards = Set('Card')


class Message(db.Entity):
    id = PrimaryKey(int, auto=True)
    content = Optional(str)
    timestamp = Optional(time)
    game = Required(Game)


class WaitingRoom(db.Entity):
    id = PrimaryKey(int, auto=True)
    roomName = Optional(str)
    maxPlayers = Optional(int)
    password = Optional(str)
    game = Optional(Game)


class Card(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    type = Optional(str)
    minPlayerNum = Optional(int)
    isExchangeable = Optional(str)
    description = Optional(str)
    player = Required(Player)
    game = Required(Game)


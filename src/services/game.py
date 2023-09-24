from fastapi import HTTPException
from pony.orm import select
import random
from models import WaitingRoom, Game, Player
from schemas.game import GameCreationRequest


def create_deck(game):
    # create game deck
    for i in range(40):
        if i % 2 == 0:
            game.cards.create(name="Lanzallamas")
        else:
            game.cards.create(name="Carta Mazo")


def assign_thing_role(game):
    # Assign roles
    players_in_game = list(select(p for p in game.players))

    the_thing = random.choice(players_in_game)
    the_thing.role = "thing"
    return the_thing


def deal_cards_to_thing(the_thing):
    # Deal cards
    the_thing.cards.create(name="La Cosa")
    for _ in range(3):
        the_thing.cards.create(name="Carta Mano")


def deal_cards_to_players(game):
    human_players = list(
        select(p for p in game.players if p.role == "human")
    )

    for player in human_players:
        for _ in range(4):
            player.cards.create(name="Carta Mano")


def create_game_on_db(creation_request: GameCreationRequest):
    room = WaitingRoom[creation_request.roomID]
    game = Game(
        waiting_room=room,
        players=room.players
    )
    return game


def is_room_valid(creation_request):
    return WaitingRoom.get(id=creation_request.roomID) is not None


def are_players_valid(creation_request):
    for player in creation_request.players:
        if Player.get(id=player.playerID) is None:
            return False

    return True


def handle_errors(creation_request: GameCreationRequest):
    if not is_room_valid(creation_request):
        raise HTTPException(
            status_code=404, detail="Room ID doesn't exist"
        )
    elif not are_players_valid(creation_request):
        raise HTTPException(status_code=400, detail="Invalid player ID")

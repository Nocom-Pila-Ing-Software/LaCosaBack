from fastapi import HTTPException
from pony.orm import select
import random
from models import WaitingRoom, Game, Player
from schemas.game import GameCreationRequest


def create_deck(game: Game) -> None:
    """
    Create a deck of cards for the given game

    Args:
    game (Game): The game object to add the deck to
    """
    for i in range(40):
        if i % 2 == 0:
            game.cards.create(name="Lanzallamas")
        else:
            game.cards.create(name="Carta Mazo")


def assign_thing_role(game: Game) -> Player:
    """
    Assign "thing" role to a random player within a game

    Args:
    game (Game): The game object to assign roles in

    Returns:
    Player: The player that was assigned the "thing" role
    """
    players_in_game = list(select(p for p in game.players))

    the_thing = random.choice(players_in_game)
    the_thing.role = "thing"
    return the_thing


def deal_cards_to_thing(the_thing: Player) -> None:
    """
    Deal cards to the "thing" player

    Args:
    the_thing (Player): The player to deal cards to
    """
    the_thing.cards.create(name="La Cosa")
    for _ in range(3):
        the_thing.cards.create(name="Carta Mano")


def deal_cards_to_players(game: Game) -> None:
    """
    Deal cards to all "human" players within a game

    Args:
    game (Game): The game object to deal cards in
    """
    human_players = list(
        select(p for p in game.players if p.role == "human")
    )

    for player in human_players:
        for _ in range(4):
            player.cards.create(name="Carta Mano")


def create_game_on_db(creation_request: GameCreationRequest) -> Game:
    """
    Creates a new Game instance in the database

    Args:
    creation_request (GameCreationRequest): Input data to create the game

    Returns:
    Game: The newly created game object
    """
    room = WaitingRoom[creation_request.roomID]
    game = Game(
        waiting_room=room,
        players=room.players
    )
    return game


def is_room_valid(creation_request: GameCreationRequest) -> bool:
    """
    Checks if the room id in creation_request exists in database

    Args:
    creation_request (GameCreationRequest): Input data to validate

    Returns:
    bool: True if room exists, False otherwise
    """
    return WaitingRoom.get(id=creation_request.roomID) is not None


def are_players_valid(creation_request: GameCreationRequest) -> bool:
    """
    Checks if every player in the creation_request exists in database

    Args:
    creation_request (GameCreationRequest): Input data to validate

    Returns:
    bool: True if all players exist, False otherwise
    """
    for player in creation_request.players:
        if Player.get(id=player.playerID) is None:
            return False

    return True


def handle_errors(creation_request: GameCreationRequest) -> None:
    """
    Checks for errors in creation_request and raises HTTPException if needed

    Args:
    creation_request (GameCreationRequest): Input data to validate

    Raises:
    HTTPException(status_code=404): If the room ID doesn't exist in database
    HTTPException(status_code=400): If a player ID doesn't exist in database
    """
    if not is_room_valid(creation_request):
        raise HTTPException(
            status_code=404, detail="Room ID doesn't exist"
        )
    elif not are_players_valid(creation_request):
        raise HTTPException(status_code=400, detail="Invalid player ID")

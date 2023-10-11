from fastapi import HTTPException
import random
from pony.orm import select
from ..schemas import GameCreationRequest
from schemas.schemas import PlayerID, GameID
from .game_draw_card import draw_card
from models import WaitingRoom, Game


class GameCreator:
    def __init__(self, creation_request):
        self.creation_request = creation_request
        self.deck_strategy = Deck()
        self._handle_errors(creation_request)

    def create(self):
        self.game = self._create_game_on_db(self.creation_request)
        self.deck_strategy.create_deck(self.game)
        self._assign_roles()
        self.deck_strategy.deal_cards(self.game)

    def get_response(self):
        response = GameID(gameID=self.game.id)
        return response

    def _handle_errors(self, creation_request: GameCreationRequest) -> None:
        """
        Checks for errors in creation_request and raises HTTPException if needed

        Args:
        creation_request (GameCreationRequest): Input data to validate

        Raises:
        HTTPException(status_code=404): If the room ID doesn't exist in the database
        HTTPException(status_code=400): If a player ID doesn't exist in the database
        """
        if not self._is_room_valid(creation_request):
            raise HTTPException(
                status_code=404, detail="Room ID doesn't exist"
            )

    def _is_room_valid(self, creation_request: GameCreationRequest) -> bool:
        """
        Checks if the room id in creation_request exists in the database

        Args:
        creation_request (GameCreationRequest): Input data to validate

        Returns:
        bool: True if room exists, False otherwise
        """
        return WaitingRoom.get(id=creation_request.roomID) is not None

    def _create_game_on_db(self, creation_request: GameCreationRequest) -> Game:
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
            players=room.players,
            current_player=room.players.select(
                lambda p: p.position == 1).first().id
        )
        return game

    def _assign_roles(self) -> None:
        """
        Assign "thing" role to a random player within a game and assigns "human" role to the rest

        Args:
        game (Game): The game object to assign roles in
        """
        players_in_game = list(select(p for p in self.game.players))

        the_thing = random.choice(players_in_game)
        the_thing.role = "thing"

        for player in players_in_game:
            if player != the_thing:
                player.role = "human"


class Deck:
    def create_deck(self, game: Game) -> None:
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

    def deal_cards(self, game: Game) -> None:
        """
        Deal "The Thing" and 3 random cards to the "thing" player and
        4 cards to the rest of the players

        Args:
            game (Game): The game object to deal cards in
        """
        players_in_game = list(game.players)

        for player in players_in_game:
            if player.role == "thing":
                player.cards.create(name="La Cosa")
                for _ in range(3):
                    draw_card(int(game.id), PlayerID(playerID=player.id))
            else:
                for _ in range(4):
                    draw_card(int(game.id), PlayerID(playerID=player.id))

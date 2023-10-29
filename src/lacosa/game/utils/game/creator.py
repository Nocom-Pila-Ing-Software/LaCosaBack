import random
from pony.orm import select
from ...schemas import GameCreationRequest
from lacosa.schemas import GameID
from models import Game
from ..deck import Deck
import lacosa.utils as utils
from lacosa.interfaces import ResponseInterface, CreatorInterface


class GameCreator(ResponseInterface, CreatorInterface):
    def __init__(self, creation_request):
        self.creation_request = creation_request
        self.deck_strategy = Deck()

    def create(self):
        self._randomize_players_positions(self.creation_request)
        self.game = self._create_game_on_db(self.creation_request)
        self.deck_strategy.create_deck(self.game)
        self._assign_roles()
        self.deck_strategy.deal_cards(self.game)

    def get_response(self):
        response = GameID(gameID=self.game.id)
        return response

    def _randomize_players_positions(self, creation_request: GameCreationRequest) -> None:
        """
        Randomizes the positions of the players in the game (1 to n)

        Args:
        game (Game): The game object to randomize the positions in
        """
        room = utils.find_room(creation_request.roomID)
        players_in_room = list(select(p for p in room.players))
        random.shuffle(players_in_room)
        for i, player in enumerate(players_in_room):
            player.position = i + 1

    def _create_game_on_db(self, creation_request: GameCreationRequest) -> Game:
        """
        Creates a new Game instance in the database

        Args:
        creation_request (GameCreationRequest): Input data to create the game

        Returns:
        Game: The newly created game object
        """
        room = utils.find_room(creation_request.roomID)
        game = Game(
            waiting_room=room,
            players=room.players,
            current_player=room.players.select().order_by(
                lambda p: random.random())[:][0].id
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

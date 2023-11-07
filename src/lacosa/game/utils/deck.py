from models import Game, Player, Card
import random
import lacosa.utils as utils
import lacosa.game.utils.exceptions as exceptions
import json
from settings import settings


class Deck:
    @classmethod
    def create_deck(cls, game: Game) -> None:
        """
        Create a deck of cards for the given game

        Args:
            game (Game): The game object to add the deck to
        """
        player_count = max(4, min(12, game.players.count()))

        with open(settings.DECK_CONFIG_PATH) as config_file:
            config = json.load(config_file)

        for card_name, card_data in config["cards"].items():
            card_amount = card_data["amount_per_player"].get(str(player_count))
            card_description = card_data["description"]
            card_type = card_data["type"]

            for _ in range(int(card_amount)):
                game.cards.create(
                    name=card_name, description=card_description, type=card_type)

    @classmethod
    def deal_cards(cls, game: Game) -> None:
        """
        Deal "The Thing" and 3 random cards to the "thing" player and
        4 cards to the rest of the players

        Args:
            game (Game): The game object to deal cards in
        """
        players_in_game = list(game.players)

        for player in players_in_game:
            if player.role == "thing":
                player.cards.create(
                    name="La cosa", description="Eres La Cosa, infecta o destruye a los Humanos, no puedes descartarla.")
                for _ in range(3):
                    cls.draw_card(int(game.id), player.id)
            else:
                for _ in range(4):
                    cls.draw_card(int(game.id), player.id)

    @classmethod
    def draw_card(cls, game_id: int, player_id: int) -> None:
        """
        Draw a card from the game deck and assign it to a player

        Args:
        game_id (int): The ID of the game to draw a card from
        player_id (PlayerID): The ID of the player to assign the card to
        """

        game = utils.find_game(game_id)
        player = utils.find_player(player_id)

        cls._handle_draw_card_errors(game, player)

        card = random.choice(list(game.cards))

        card.player = player
        game.cards.remove(card)
        player.cards.add(card)

    @classmethod
    def discard_card(cls, card: Card, player: Player, game: Game):
        player.cards.remove(card)
        game.cards.add(card)

    @classmethod
    def _handle_draw_card_errors(cls, game: Game, player: Player) -> None:
        """
        Check if the pre-conditions for drawing a card are met

        Args:
        game_id (int): The ID of the game to draw a card from
        player_id (PlayerID): The ID of the player to assign the card to
        """
        exceptions.validate_player_in_game(game, player)
        exceptions.validate_ammount_of_cards(player)
        exceptions.validate_deck_not_empty(game)

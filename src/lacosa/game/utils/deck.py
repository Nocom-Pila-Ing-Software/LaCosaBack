from models import Game, Player
from fastapi import HTTPException, status
import random
import lacosa.game.utils.utils as utils


class Deck:
    @classmethod
    def create_deck(cls, game: Game) -> None:
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
                player.cards.create(name="La Cosa")
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
    def _handle_draw_card_errors(cls, game: Game, player: Player) -> None:
        """
        Check if the pre-conditions for drawing a card are met

        Args:
        game_id (int): The ID of the game to draw a card from
        player_id (PlayerID): The ID of the player to assign the card to
        """
        if player not in game.players:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Player not in game")

        # FIXME: player can have 5 cards
        if player.cards.count() > 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Player already has a card")

        if not game.cards:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No cards left in deck")

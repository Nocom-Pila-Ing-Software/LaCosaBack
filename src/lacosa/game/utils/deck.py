from models import Game, Player
import random
import lacosa.utils as utils
import lacosa.game.utils.exceptions as exceptions


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
        exceptions.validate_player_in_game(game, player)
        exceptions.validate_ammount_of_cards(player)
        exceptions.validate_deck_not_empty(game)

    @classmethod
    def hand_info(cls, player_id: int) -> list:
        """
        Return a list of dictionaries with the information of the cards in the player's hand

        Args:
            player (Player): The player to get the hand info from

        Returns:
            list: A list of dictionaries with the information of the cards in the player's hand
        """
        hand_info = []

        player = utils.find_player(player_id)

        for card in player.cards:
            hand_info.append({
                "cardName": card.name,
                "cardID": card.id,
                "isPlayable": cls._is_card_playable(card),
                "isDiscardable": cls._is_card_discardable(card)
            })

        return hand_info

    @classmethod
    def _is_card_playable(cls, card) -> bool:
        """
        Check if a card is playable

        Args:
            card (Card): The card to check

        Returns:
            bool: True if the card is playable, False otherwise
        """
        return card.name == "Lanzallamas"  # FIXME: Add logic to check if the card is playable (Seguramente sea un IF gigante)

    @classmethod
    def _is_card_discardable(cls, card) -> bool:
        """
        Check if a card is discardable

        Args:
            card (Card): The card to check

        Returns:
            bool: True if the card is discardable, False otherwise
        """
        return card.name != "La Cosa"  # FIXME: Add logic to check if the card is discardable (Creo que solo la cosa no es descartable)

    @classmethod
    def possible_targets(cls, card_id: int, player_id: int) -> list:
        """
        Return a list of dictionaries with the information of the possible targets for the given card

        Args:
            card_id (int): The ID of the card to check
            player_id (int): The ID of the player that is playing the card

        Returns:
            list: A list of dictionaries with the information of the possible targets for the given card
        """
        player = utils.find_player(player_id)
        game = utils.find_game(player.game.id)

        exceptions.validate_player_in_game(game, player)
        exceptions.validate_player_has_card(player, card_id)

        possible_targets = []

        # FIXME: Add logic to check which players are possible targets (Seguramente sea un IF gigante)
        for player in game.players:
            if player.id != player_id:
                possible_targets.append(
                    {"playerID": player.id, "playerName": player.username}
                )

        return possible_targets
    
    @classmethod
    def discard_card(cls, card_id: int, player_id: int) -> None:
        """
        Discard a card from the player's hand

        Args:
            card_id (int): The ID of the card to discard
            player_id (int): The ID of the player that is discarding the card
        """
        player = utils.find_player(player_id)
        game = utils.find_game(player.game.id)
        card = utils.find_card(card_id)

        exceptions.validate_player_in_game(game, player)
        exceptions.validate_player_has_card(player, card_id)
        exceptions.validate_player_alive(player)
        #exceptions.validate_card_discardable(card)

        player.cards.remove(card)
        game.cards.add(card)

    @classmethod
    def possible_defense_cards(cls, card_id: int, target_id: int) -> list:
        """
        Return a list of dictionaries with the information of the possible defense cards for the given card and target

        Args:
            card_id (int): The ID of the card to check
            target_id (int): The ID of the target

        Returns:
            list: A list of dictionaries with the information of the possible defense cards for the given card and target
        """
        card = utils.find_card(card_id)
        target = utils.find_player(target_id)
        game = utils.find_game(target.game.id)

        exceptions.validate_player_in_game(game, target)
        exceptions.validate_player_has_card(target, card)

        possible_defense_cards = []

        # FIXME: Add logic to check which cards are possible defense cards

        return possible_defense_cards

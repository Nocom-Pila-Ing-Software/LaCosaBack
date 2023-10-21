from lacosa.game.utils.deck import Deck
from models import Event
from ..schemas import GenericCardRequest, PlayCardRequest
from .card_effects import get_card_effect_function, CardEffectFunc
import lacosa.utils as utils
import lacosa.game.utils.exceptions as exceptions
from lacosa.interfaces import ActionInterface
from pony.orm import db_session, commit


class CardPlayer(ActionInterface):
    def __init__(self, play_request: PlayCardRequest, game_id: int):
        self.game = utils.find_game(game_id)
        self.player = utils.find_player(play_request.playerID)
        self.target_player = utils.find_player(play_request.targetPlayerID)
        self.card = utils.find_card(play_request.cardID)
        self.handle_errors()

    def execute_action(self) -> None:
        """
        Plays a card on the game

        Args:
        play_request (PlayCardRequest): Input data to validate
        game_id (int): The id of the game to validate
        """

        effect_func: CardEffectFunc = get_card_effect_function(self.card.name)
        effect_func(self.target_player, self.game)

        self.player.cards.remove(self.card)
        self.game.cards.add(self.card)
        self.game.last_played_card = self.card

        self.game.current_player = self.get_next_player_id()

    def get_next_player_id(self):
        next_player = self.game.players.select(
            lambda p: p.position == self.player.position + 1).first()
        if next_player is None:
            next_player = self.game.players.select(
                lambda p: p.position == 1).first()
        return next_player.id

    def handle_errors(self) -> None:
        """
        Checks for errors in play_request and raises HTTPException if needed

        Args:
        play_request (PlayCardRequest): Input data to validate
        game_id (int): The id of the game to validate

        Raises:
        HTTPException(status_code=400): If the player is not found or not is allowed to play
        HTTPException(status_code=404): If the game is not found
        """

        exceptions.validate_player_in_game(self.game, self.player)
        exceptions.validate_player_in_game(self.game, self.target_player)
        exceptions.validate_player_has_card(self.player, self.card.id)
        exceptions.validate_player_alive(self.target_player)


class CardTrader(ActionInterface):
    def __init__(self, trade_request: GenericCardRequest, game_id: int):
        self.game = utils.find_game(game_id)
        self.event = utils.find_partial_event(trade_request.playerID)
        self.player = utils.find_player(trade_request.playerID)
        self.card = utils.find_card(trade_request.cardID)
        self.handle_errors()

    def execute_action(self) -> None:
        """
        If both players have selected a card, trade them
        If only one player has selected a card, save it in the event

        Args:
        trade_request (PlayCardRequest): Input data to validate
        game_id (int): The id of the game to validate
        """

        if self.event.card1 is None:
            self.event.card1 = self.card
            self.game.current_player = self.event.player2.id
        else:
            self.event.card2 = self.card
            self.event.is_completed = True
            self.event.is_successful = True
            self.game.current_player = self.get_next_player_id()
            self.game.current_action = "draw"

            self.event.player1.cards.remove(self.event.card1)
            self.event.player1.cards.add(self.event.card2)

            self.event.player2.cards.remove(self.event.card2)
            self.event.player2.cards.add(self.event.card1)

    def get_next_player_id(self):
        next_player = self.game.players.select(
            lambda p: p.position == self.event.player1.position + 1).first()
        if next_player is None:
            next_player = self.game.players.select(
                lambda p: p.position == 1).first()
        return next_player.id

    def handle_errors(self) -> None:
        """
        Checks for errors in trade_request and raises HTTPException if needed

        Args:
        trade_request (PlayCardRequest): Input data to validate
        game_id (int): The id of the game to validate

        Raises:
        HTTPException(status_code=400): If the player is not found or the card is not in the player's hand
        HTTPException(status_code=403): If the player is not allowed to trade
        HTTPException(status_code=404): If the game is not found
        """

        exceptions.validate_player_in_game(self.game, self.player)
        exceptions.validate_current_action(self.game, "trade")
        exceptions.validate_current_player(self.game, self.player)
        exceptions.validate_player_alive(self.player)
        exceptions.validate_player_has_card(self.player, self.card.id)
        # TODO: Validate player is allowed to trade the card with the other player (La cosa y eso)


class CardDefender(ActionInterface):
    def __init__(self, defend_request: GenericCardRequest, game_id: int):
        self.game = utils.find_game(game_id)
        self.event = utils.find_event_to_defend(defend_request.playerID)
        self.player = utils.find_player(defend_request.playerID)
        self.card = utils.find_card(defend_request.cardID) if defend_request.cardID != -1 else None
        self.handle_errors()

    def execute_action(self) -> None:
        """
        If the player has selected a card, save it in the event

        Args:
        defend_request (PlayCardRequest): Input data to validate
        game_id (int): The id of the game to validate
        """

        if self.card is not None:
            self.event.card2 = self.card
            self.event.is_completed = True
            self.event.is_successful = False
            self.game.current_player = self.get_next_player_id()
            self.game.current_action = "draw"

            self.event.player2.cards.remove(self.event.card2)
            Deck.draw_card(self.game.id, self.event.player2.id)

    def get_next_player_id(self):
        next_player = self.game.players.select(
            lambda p: p.position == self.event.player1.position + 1).first()
        if next_player is None:
            next_player = self.game.players.select(
                lambda p: p.position == 1).first()
        return next_player.id

    def handle_errors(self) -> None:
        """
        Checks for errors in defend_request and raises HTTPException if needed

        Args:
        defend_request (PlayCardRequest): Input data to validate
        game_id (int): The id of the game to validate

        Raises:
        HTTPException(status_code=400): If the player is not found or the card is not in the player's hand
        HTTPException(status_code=403): If the player is not allowed to defend
        HTTPException(status_code=404): If the game is not found
        """

        exceptions.validate_player_in_game(self.game, self.player)
        exceptions.validate_current_action(self.game, "defend", "trade")
        exceptions.validate_current_player(self.game, self.player)
        exceptions.validate_player_alive(self.player)
        exceptions.validate_player_has_card(self.player, self.card.id)
        # exceptions.validate_card_type(self.card, "defense") #FIXME: implement this
        exceptions.validate_correct_defense_card(self.card, self.event)

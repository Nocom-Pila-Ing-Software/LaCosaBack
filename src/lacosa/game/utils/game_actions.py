from ..schemas import PlayCardRequest, EventTypes, GenericCardRequest, EventCreationRequest
from lacosa.game.utils.deck import Deck
from lacosa.game.utils.event_creator import EventCreator
from .card_effects import execute_card_effect
import lacosa.utils as utils
import lacosa.game.utils.exceptions as exceptions
from .deck import Deck
from lacosa.interfaces import ActionInterface
import lacosa.game.utils.turn_handler as turn_handler
from pathlib import Path
import json


class CardPlayer(ActionInterface):
    def __init__(self, play_request: PlayCardRequest, game_id: int):
        self.game = utils.find_game(game_id)
        self.player = utils.find_player(play_request.playerID)
        self.target_player = utils.find_player(play_request.targetPlayerID)
        self.next_player_trade = utils.find_player(self.get_next_player_id())
        self.card = utils.find_card(play_request.cardID)
        self.handle_errors()

    def execute_action(self) -> None:
        # Creo un evento de tipo acción
        self.game.current_action = "action"

        # Creo el evento de acción
        event_request = EventCreationRequest(
            gameID=self.game.id,
            playerID=self.player.id,
            targetPlayerID=self.target_player.id,
            cardID=self.card.id,
            targetCardID=-1,
            type=EventTypes.action,
            isCompleted=False,
            isSuccessful=False
        )
        event_create = EventCreator(event_request)
        event_create.create()

        check_card_is_defensible = self.check_card_is_defensible(self.card)
        if not check_card_is_defensible:
            execute_card_effect(self.card, self.player,
                                self.target_player, self.game)

            event_create.is_completed = True
            event_create.is_successful = True

            self.game.current_action = "trade"

            event_request = EventCreationRequest(
                gameID=self.game.id,
                playerID=self.player.id,
                targetPlayerID=self.next_player_trade.id,
                cardID=-1,  # probar
                targetCardID=-1,
                type=EventTypes.trade,
                isCompleted=False,
                isSuccessful=False
            )
            event_create = EventCreator(event_request)
            event_create.create()
        else:
            self.game.current_action = "defense"
            self.game.current_player = self.target_player.position

    def get_next_player_id(self):
        next_player = turn_handler.get_next_player(
            self.game,
            self.player.position
        )
        return next_player.id

    def check_card_is_defensible(self, card) -> bool:
        config_path = Path(__file__).resolve().parent.parent / \
            'utils' / 'config_deck.json'

        with open(config_path) as config_file:
            config = json.load(config_file)

        if card.name in config['cards']:
            if 'defensible_by' in config['cards'][card.name]:
                return True
            else:
                return False

    def handle_errors(self) -> None:
        """
        Checks for errors in play_request and raises HTTPException if needed
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
        next_player = turn_handler.get_next_player(
            self.game,
            self.event.player1.position
        )
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
        self.card = utils.find_card(
            defend_request.cardID) if defend_request.cardID != -1 else None
        self.handle_errors()

    def execute_action(self) -> None:
        """
        If the player has selected a card, save it in the event

        Args:
        defend_request (PlayCardRequest): Input data to validate
        game_id (int): The id of the game to validate
        """
        if self.event.type == "trade":
            if self.card is not None:
                self.event.card2 = self.card

                self.event.is_completed = True
                self.event.is_successful = False
                self.game.current_player = self.get_next_player_id()
                self.game.current_action = "draw"

                self.event.player2.cards.remove(self.event.card2)
                Deck.draw_card(self.game.id, self.event.player2.id)

        elif self.event.type == "action":
            if self.card is not None:
                self.event.card2 = self.card
                execute_card_effect(
                    self.event.card2, self.event.player2, self.event.player1, self.game)
                self.event.is_successful = False
            else:
                execute_card_effect(
                    self.event.card1, self.event.player1, self.event.player2, self.game)
                self.event.is_successful = True

            self.event.is_completed = True

            self.game.current_action = "trade"

            event_request = EventCreationRequest(
                gameID=self.game.id,
                playerID=self.event.player1.id,
                targetPlayerID=self.get_next_player_id(),
                cardID=-1,
                targetCardID=-1,
                type=EventTypes.trade,
                isCompleted=False,
                isSuccessful=False
            )
            event_create = EventCreator(event_request)
            event_create.create()

    def get_next_player_id(self):
        next_player = turn_handler.get_next_player(
            self.game,
            self.event.player1.position
        )
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
        exceptions.validate_current_action(self.game, "defense", "trade")
        exceptions.validate_current_player(self.game, self.player)
        exceptions.validate_player_alive(self.player)
        if self.card is not None:
            exceptions.validate_player_has_card(self.player, self.card.id)
            exceptions.validate_correct_defense_card(self.card, self.event)
        # exceptions.validate_card_type(self.card, "defense") #FIXME: implement this

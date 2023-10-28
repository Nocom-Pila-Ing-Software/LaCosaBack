from models import Event
from ...schemas import PlayCardRequest, EventTypes, GenericCardRequest, EventCreationRequest
from lacosa.game.utils.deck import Deck
from lacosa.game.utils.event_creator import EventCreator
from .effects import execute_card_effect
import lacosa.utils as utils
import lacosa.game.utils.exceptions as exceptions
from ..deck import Deck
from lacosa.interfaces import ActionInterface
import lacosa.game.utils.turn_handler as turn_handler
from pathlib import Path
import json
from pony.orm import commit, select


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
            events_completed = select(
                e for e in self.game.events if e.is_completed == True)[:]
            last_event = None
            if len(events_completed) > 0:
                last_event = sorted(events_completed, key=lambda e: e.id)[-1]
            self.event.card2 = self.card
            self.event.is_completed = True
            self.event.is_successful = True
            if (
                last_event is not None
                and last_event.type == "action"
                and last_event.is_successful
                and last_event.card1.name in ("Cambio de lugar", "Mas vale que corras")
                and last_event.player1.id == self.event.player1.id
            ):
                self.game.current_player = last_event.player2.id
            else:
                self.game.current_player = self.get_next_player_id()
            self.game.current_action = "draw"

            self.event.player1.cards.remove(self.event.card1)
            self.event.player1.cards.add(self.event.card2)

            self.event.player2.cards.remove(self.event.card2)
            self.event.player2.cards.add(self.event.card1)

            if (self.event.player1.role == "thing" and self.event.card1.name == "Infeccion"):
                self.event.player2.role = "infected"
            elif (self.event.player2.role == "thing" and self.event.card2.name == "Infeccion"):
                self.event.player1.role = "infected"

            commit()

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
        exceptions.validate_card_allowed_to_trade(
            self.card, self.event, self.player)

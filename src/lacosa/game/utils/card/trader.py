from ...schemas import GenericCardRequest
from lacosa.interfaces import ActionInterface
from lacosa.utils import find_game, find_partial_event, find_player, find_card
from lacosa.game.utils import exceptions, turn_handler
from pony.orm import select


class CardTrader(ActionInterface):
    POSITION_SWITCHING_CARDS = {"Cambio de lugar", "Mas vale que corras"}

    def __init__(self, trade_request: GenericCardRequest, game_id: int):
        self.game = find_game(game_id)
        self.event = find_partial_event(trade_request.playerID)
        self.player = find_player(trade_request.playerID)
        self.card = find_card(trade_request.cardID)
        self.handle_errors()

    def execute_action(self) -> None:
        """
        Depending on whether both players have selected a card either trades them or saves the card in the event.

        Args:
        trade_request (PlayCardRequest): Input data to validate.
        game_id (int): The id of the game to validate.
        """
        if self.event.card1 is None:
            self.event.card1 = self.card
            self.game.current_player = self.event.player2.id
        else:
            self.trade_cards()

    def trade_cards(self):
        completed_events = select(
            e for e in self.game.events if e.is_completed is True
        ).sort_by(lambda e: e.id)[:]
        last_event = completed_events[-1] if completed_events else None

        self.event.card2 = self.card
        self.event.is_completed = True
        self.event.is_successful = True
        self.game.current_player = self.get_next_player_id(last_event)
        self.game.current_action = "draw"

        self.swap_cards()
        self.update_infection_status()

    def get_next_player_id(self, last_event):
        if self.should_continue_with_last_event_player(last_event):
            return last_event.player2.id
        else:
            next_player = turn_handler.get_next_player(
                self.game, self.event.player1.position
            )
            return next_player.id

    def should_continue_with_last_event_player(self, last_event):
        should_continue = (
            last_event
            and last_event.type == "action"
            and last_event.is_successful
            and last_event.card1.name in self.POSITION_SWITCHING_CARDS
            and last_event.player1.id == self.event.player1.id
        )
        return should_continue

    def swap_cards(self):
        self.event.player1.cards.remove(self.event.card1)
        self.event.player1.cards.add(self.event.card2)

        self.event.player2.cards.remove(self.event.card2)
        self.event.player2.cards.add(self.event.card1)

    def update_infection_status(self):
        if self.is_infected(self.event.player1, self.event.card1):
            self.assign_infection(self.event.player2)
        elif self.is_infected(self.event.player2, self.event.card2):
            self.assign_infection(self.event.player1)

    def is_infected(self, player, card):
        return player.role == "thing" and card.name == "Infeccion"

    def assign_infection(self, player):
        player.role = "infected"

    def handle_errors(self) -> None:
        """
        Checks for errors in trade_request and raises exception if needed.

        Args:
        trade_request (PlayCardRequest): Input data to validate.
        game_id (int): The id of the game to validate.

        Raises:
        HTTPException(status_code=400): If the player is not found or the card is not in the player's hand.
        HTTPException(status_code=403): If the player is not allowed to trade.
        HTTPException(status_code=404): If the game is not found.
        """
        exceptions.validate_player_in_game(self.game, self.player)
        exceptions.validate_current_action(self.game, "trade")
        exceptions.validate_current_player(self.game, self.player)
        exceptions.validate_player_alive(self.player)
        exceptions.validate_player_has_card(self.player, self.card.id)
        exceptions.validate_card_allowed_to_trade(self.card, self.event, self.player)

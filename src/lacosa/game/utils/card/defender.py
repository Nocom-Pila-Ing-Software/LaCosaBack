from ...schemas import EventTypes, GenericCardRequest, EventCreationRequest
from lacosa.game.utils import event_creator, exceptions, turn_handler
from .effects import execute_card_effect
from ..deck import Deck
from lacosa.interfaces import ActionInterface
import lacosa.utils as utils
from lacosa.game.utils.card_shower import clear_shown_cards


class CardDefender(ActionInterface):
    def __init__(self, defend_request: GenericCardRequest, game_id: int):
        self.game = utils.find_game(game_id)
        self.event = utils.find_event_to_defend(defend_request.playerID)
        self.player = utils.find_player(defend_request.playerID)
        self.card = None
        if defend_request.cardID != -1:
            self.card = utils.find_card(defend_request.cardID)
        self.handle_errors()

    def execute_action(self) -> None:
        self.event.card2 = self.card if self.card else None
        self.event.is_completed = True

        if self.event.type == "trade":
            self.handle_trade_event()
        elif self.event.type == "action":
            self.handle_action_event()

    def get_next_player_id(self):
        next_player = turn_handler.get_next_player(
            self.game, self.event.player1.position
        )
        return next_player.id

    def handle_errors(self) -> None:
        exceptions.validate_player_in_game(self.game, self.player)
        exceptions.validate_current_action(self.game, "defense", "trade")
        exceptions.validate_current_player(self.game, self.player)
        exceptions.validate_player_alive(self.player)
        if self.card is not None:
            exceptions.validate_player_has_card(self.player, self.card.id)
            exceptions.validate_correct_defense_card(self.card, self.event)

    def handle_trade_event(self):
        self.game.current_player = self.get_next_player_id()
        self.game.current_action = "draw"
        self.game.last_played_card = self.card
        Deck.draw_card(self.game.id, self.event.player2.id)
        Deck.discard_card(self.card, self.event.player2, self.game)

        clear_shown_cards(self.game.players)

    def handle_action_event(self):
        card = self.event.card2 if self.card else self.event.card1
        execute_card_effect(card, self.event.player1, self.event.player2, self.game)
        if self.card:
            self.event.is_successful = False
            Deck.draw_card(self.game.id, self.event.player2.id)
        else:
            self.event.is_successful = True

        self.game.current_action = "trade"
        self.game.current_player = self.event.player1.id
        self.create_new_event()

    def create_new_event(self):
        event_request = EventCreationRequest(
            gameID=self.game.id,
            playerID=self.event.player1.id,
            targetPlayerID=self.get_next_player_id(),
            cardID=-1,
            targetCardID=-1,
            type=EventTypes.trade,
            isCompleted=False,
            isSuccessful=False,
        )
        event_create = event_creator.EventCreator(event_request)
        event_create.create()

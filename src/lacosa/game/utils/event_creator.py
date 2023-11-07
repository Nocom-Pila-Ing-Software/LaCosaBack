from models import Event
from lacosa.game.schemas import GameEvent, EventTypes, Action
import lacosa.utils as utils
from lacosa.interfaces import CreatorInterface


class EventCreator(CreatorInterface):
    def __init__(self, event_request: GameEvent):
        self.event_request = event_request
        self.game = utils.find_game(event_request.gameID)
        self.player1 = utils.find_player(event_request.playerID)
        self.player2 = utils.find_player(event_request.targetPlayerID)
        self.card1 = utils.find_card(event_request.cardID)
        self.card2 = utils.find_card(event_request.targetCardID)

    def create(self):
        self.event = self._create_event_on_db()
        self._update_game_status()

    def _create_event_on_db(self) -> Event:
        event = Event(
            game=self.game,
            type=self.event_request.type,
            player1=self.player1,
            player2=self.player2,
            card1=self.card1,
            card2=self.card2,
            is_completed=self.event_request.isCompleted,
            is_successful=self.event_request.isSuccessful
        )
        return event

    def _update_game_status(self) -> None:
        if self.event_request.type == EventTypes.action:
            self.game.current_action = Action.action
        elif self.event_request.type == EventTypes.trade:
            self.game.current_action = Action.trade

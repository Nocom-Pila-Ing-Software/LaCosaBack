from models import Event
from ...schemas import PlayCardRequest, EventTypes, EventCreationRequest
from lacosa.game.utils.deck import Deck
from lacosa.game.utils.event_creator import EventCreator
from .effects import execute_card_effect
import lacosa.utils as utils
import lacosa.game.utils.exceptions as exceptions
from lacosa.interfaces import ActionInterface
import lacosa.game.utils.turn_handler as turn_handler
import json
from pony.orm import select
from settings import settings


class CardPlayer(ActionInterface):
    def __init__(self, play_request: PlayCardRequest, game_id: int):
        self.game = utils.find_game(game_id)
        self.player = utils.find_player(play_request.playerID)
        self.target_player = utils.find_player(play_request.targetPlayerID)
        self.card = utils.find_card(play_request.cardID)
        self.handle_errors()

    def execute_action(self) -> None:
        # Creo un evento de tipo acción
        self.game.last_played_card = self.card

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
        event = utils.find_partial_event(self.player.id)

        Deck.discard_card(self.card, self.player, self.game)

        check_card_is_defensible = self.check_card_is_defensible(self.card)
        if not check_card_is_defensible:
            execute_card_effect(self.card, self.player,
                                self.target_player, self.game)

            event.is_completed = True
            event.is_successful = True

            self.game.current_action = "trade"
            if select(e for e in Event if (e.player1.id == self.player.id or e.player2.id == self.target_player.id) and e.is_completed is False).get() is None:
                event_request = EventCreationRequest(
                    gameID=self.game.id,
                    playerID=self.player.id,
                    targetPlayerID=self.get_next_player_id(),
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
            self.game.current_player = self.target_player.id

    def get_next_player_id(self):
        next_player = turn_handler.get_next_player(
            self.game,
            self.player.position
        )
        return next_player.id

    def check_card_is_defensible(self, card) -> bool:
        with open(settings.DECK_CONFIG_PATH) as config_file:
            config = json.load(config_file)

        if card.name in config['cards']:
            if 'defensible_by' in config['cards'][card.name]:
                return True
        return False

    def handle_errors(self) -> None:
        """
        Checks for errors in play_request and raises HTTPException if needed
        """

        exceptions.validate_player_in_game(self.game, self.player)
        exceptions.validate_player_in_game(self.game, self.target_player)
        exceptions.validate_player_has_card(self.player, self.card.id)
        exceptions.validate_player_alive(self.target_player)

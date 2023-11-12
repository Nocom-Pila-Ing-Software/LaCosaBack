from lacosa import utils
from lacosa.interfaces import ActionInterface
from lacosa.game.schemas import ShowCardsRequest
from lacosa.game.utils import card_shower
from lacosa.game.utils import turn_handler
from pony.orm import commit


class RevelationsHandler(ActionInterface):
    def __init__(self, show_request: ShowCardsRequest, game_id: int):
        self.game = utils.find_game(game_id)
        self.player = utils.find_player(show_request.playerID)
        self.cards = [utils.find_card(card.cardID)
                      for card in show_request.cards]

    def create_info_event(self, type_):
        self.game.events.create(
            player1=self.player,
            type=type_,
            is_completed=True
        )

    def show_cards(self, ):
        card_shower.show_cards_to_players(self.cards, list(self.game.players))

    def is_infection_shown(self, ):
        return len(self.cards) == 1 and self.cards[0].name == "Infeccion"

    def execute_action(self) -> None:
        if self.is_infection_shown():
            self.show_cards()
            self.create_info_event("revelations-end")
            turn_handler.next_turn(self.game, self.player)
            self.game.current_action = "draw"
            return

        if not self.cards:
            # player didn't show
            self.create_info_event("no-show")
        else:
            self.show_cards()

        turn_handler.next_turn(self.game, self.player)
        commit()

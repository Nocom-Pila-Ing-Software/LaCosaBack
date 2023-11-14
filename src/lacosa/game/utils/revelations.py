from lacosa import utils
from lacosa.interfaces import ActionInterface
from lacosa.game.schemas import ShowCardsRequest
from lacosa.game.utils import card_shower
from lacosa.game.utils import turn_handler
from lacosa.game.utils import exceptions
from lacosa.game.schemas import EventTypes


class RevelationsHandler(ActionInterface):
    def __init__(self, show_request: ShowCardsRequest, game_id: int):
        self.game = utils.find_game(game_id)
        self.player = utils.find_player(show_request.playerID)
        self.cards_to_show = show_request.cardsToShow
        self.handle_errors()

    def create_info_event(self, type_):
        self.game.events.create(
            player1=self.player,
            type=type_,
            is_completed=True
        )

    def get_cards_to_show(self, ):
        cards = []
        if self.cards_to_show == "infection":
            exceptions.validate_infection_in_hand(self.player)
            cards = [
                self.player.cards.filter(
                    lambda c: c.name == "Infeccion").first()
            ]
        elif self.cards_to_show == "all":
            cards = list(self.player.cards)

        return cards

    def show_cards(self):
        cards = self.get_cards_to_show()
        card_shower.show_cards_to_players(cards, list(self.game.players))

    def handle_revelations_end(self, ):
        self.create_info_event(EventTypes.revelations_end)
        turn_handler.next_turn(self.game, self.player)
        self.game.current_action = "draw"

    def execute_action(self) -> None:
        if self.cards_to_show == "infection":
            self.show_cards()
            self.handle_revelations_end()
            return

        if self.cards_to_show == "all":
            self.show_cards()
        else:
            # player didn't show
            self.create_info_event(EventTypes.no_show)

        turn_handler.next_turn(self.game, self.player)

    def handle_errors(self) -> None:
        exceptions.validate_player_in_game(self.game, self.player)
        exceptions.validate_player_alive(self.player)
        exceptions.validate_player_is_in_turn(self.player, self.game)

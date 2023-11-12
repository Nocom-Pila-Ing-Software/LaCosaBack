import json
from lacosa import utils
import lacosa.game.utils.exceptions as exceptions
from lacosa.interfaces import ResponseInterface
from lacosa.player.schemas import (
    UsabilityResponse,
    UsabilityInfoCard,
)
from fastapi import status
from models import Event
from pony.orm import select
from settings import settings


class CardDefenseInformer(ResponseInterface):
    def __init__(self, player_id: int, card_id: int):
        self.player = utils.find_player(player_id, status.HTTP_404_NOT_FOUND)
        self.card = None
        if card_id != -1:
            utils.find_card(card_id, status.HTTP_404_NOT_FOUND)
        self.handle_errors()

    def get_response(self) -> UsabilityResponse:
        card_info = self.get_defense_cards_info()
        return UsabilityResponse(cards=card_info)

    def get_defense_cards_info(self) -> list:
        if self.card is None:
            return self.get_trade_event_defense_cards()
        else:
            return self.get_action_defense_cards()

    def get_trade_event_defense_cards(self):
        cards_info = []
        event = self.get_trade_event()
        if event is not None and event.player2 == self.player:
            cards_info = self.get_cards_by_name("No gracias")
            cards_info += self.get_cards_by_name("Aterrador")
            cards_info += self.get_cards_by_name("Fallaste")
        return sorted(cards_info, key=lambda card: card.cardID)

    def get_trade_event(self):
        incomplete_trades = select(
            e for e in Event if e.type == "trade" and e.is_completed is False
        )

        trades_involving_player = incomplete_trades.filter(
            lambda e: e.player1 == self.player or e.player2 == self.player
        )
        return trades_involving_player.first()

    def get_action_defense_cards(self):
        # FIXME: cards can only be defended by a single card only
        # this will probably break if we add more cards to the defensible_by attribute
        defense_card = self.get_defense_cards(self.card.name)
        return sorted(
            self.get_cards_by_name(defense_card), key=lambda card: card.cardID
        )

    def get_cards_by_name(self, card_name):
        return [
            UsabilityInfoCard(
                cardID=card.id,
                name=card.name,
                description=card.description,
                usable=True,
            )
            for card in self.player.cards
            if card.name == card_name
        ]

    def get_defense_cards(self, card_name: str) -> str:
        with open(settings.DECK_CONFIG_PATH) as config_file:
            config = json.load(config_file)
        return config["cards"][card_name]["defensible_by"]

    def handle_errors(self) -> None:
        exceptions.validate_player_has_game(self.player, status.HTTP_400_BAD_REQUEST)
        exceptions.validate_player_alive(self.player)
        if self.card is not None:
            exceptions.validate_correct_type(self.card, "action")

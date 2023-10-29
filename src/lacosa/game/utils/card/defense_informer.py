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
        self.card = utils.find_card(card_id, status.HTTP_404_NOT_FOUND)
        self.handle_errors()

    def get_response(self) -> UsabilityResponse:
        """
        Returns the information of which cards can be used to defend against the card played by the attacker

        Returns:
        UsabilityResponse: The cards information
        """

        return UsabilityResponse(cards=self.get_cards_info())

    def get_cards_info(self) -> list:
        """
        Returns the information of which cards can be used to defend against the card played by the attacker

        Returns:
        list: The cards information
        """

        cards_info = []
        # Get the cards that only are usable if the player is the target of the trade event (and only in a trade event)
        if self.card is None:
            event = select(e for e in Event if e.type == "trade" and (
                e.player1 == self.player or e.player2 == self.player) and e.is_completed is False).first()
            # Verify if the player is the target of the trade event and not the trader generating the event
            if event is not None and event.player2 == self.player:
                for card in self.player.cards:
                    if card.name == "No, gracias":
                        cards_info.append(UsabilityInfoCard(
                            cardID=card.id,
                            name=card.name,
                            description=card.description,
                            usable=True
                        ))
        else:
            # Cards that can be used to defend against the card (actions card) played by the attacker
            for card in self.player.cards:
                if card.name in self.get_cards_that_defend(self.card.name):
                    cards_info.append(UsabilityInfoCard(
                        cardID=card.id,
                        name=card.name,
                        description=card.description,
                        usable=True
                    ))

        return sorted(cards_info, key=lambda card: card.cardID)

    def get_cards_that_defend(self, card_name: str) -> str:
        """
        Returns the type of the card
        """
        with open(settings.DECK_CONFIG_PATH) as config_file:
            config = json.load(config_file)

        return config["cards"][card_name]["defensible_by"]

    def handle_errors(self) -> None:
        """
        Checks for errors and raises HTTPException if needed
        """

        exceptions.validate_player_in_game(
            None, self.player, status.HTTP_400_BAD_REQUEST)
        exceptions.validate_player_alive(self.player)
        if self.card is not None:
            exceptions.validate_correct_type(
                self.card, "action")


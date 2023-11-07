from lacosa import utils
import lacosa.game.utils.exceptions as exceptions
from lacosa.interfaces import ResponseInterface
from lacosa.player.schemas import (
    UsabilityActionResponse,
    UsabilityActionInfoCard,
)
from fastapi import status


class CardUsabilityInformer(ResponseInterface):
    UNPLAYABLE_CARDS = {"La cosa", "Infeccion"}
    UNPLAYABLE_TYPES = {"defense"}
    UNDISCARDABLE_CARDS = {"La cosa"}

    def __init__(self, player_id: int):
        self.player = utils.find_player(player_id, status.HTTP_404_NOT_FOUND)
        self.handle_errors()

    def get_response(self) -> UsabilityActionResponse:
        """
        Returns the information of which cards can be played or discarded by the player

        Returns:
        UsabilityInfoResponse: The cards information
        """

        card_info = self.get_cards_info()
        return UsabilityActionResponse(cards=card_info)

    def is_card_playable(self, card):
        return (
            card.name not in self.UNPLAYABLE_CARDS
            and card.type not in self.UNPLAYABLE_TYPES
            )

    def is_last_infection_card(self, card):
        infection_cards_in_hand = self.get_infection_cards_num()
        return (
            self.player.role == "infected"
            and card.name == "Infeccion"
            and infection_cards_in_hand == 1
        )

    def is_card_discardable(self, card):
        is_card_discardable = card.name not in self.UNDISCARDABLE_CARDS

        # applies only to infected
        is_last_infection_card = self.is_last_infection_card(card)

        return (
            is_card_discardable
            and not is_last_infection_card
        )

    def get_usability_schema(self, card):
        playable = self.is_card_playable(card)
        discardable = self.is_card_discardable(card)

        return UsabilityActionInfoCard(
            cardID=card.id,
            name=card.name,
            description=card.description,
            playable=playable,
            discardable=discardable
        )

    def get_infection_cards_num(self):
        return sum(
            1 for card in self.player.cards
            if card.name == "Infeccion"
        )

    def get_cards_info(self) -> list:
        """
        Returns the information of which cards can be played or discarded by the player

        Returns:
        list: The cards information
        """

        cards_info = [
            self.get_usability_schema(card) for card in self.player.cards
        ]
        return cards_info

    def handle_errors(self) -> None:
        """
        Checks for errors and raises HTTPException if needed
        """

        exceptions.validate_player_has_game(
            self.player,
            status.HTTP_400_BAD_REQUEST
        )
        exceptions.validate_player_alive(self.player)

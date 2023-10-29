import json
from lacosa import utils
import lacosa.game.utils.exceptions as exceptions
from lacosa.interfaces import ResponseInterface
from lacosa.player.schemas import (
    UsabilityActionResponse,
    UsabilityActionInfoCard,
)
from fastapi import status
from settings import settings


class CardUsabilityInformer(ResponseInterface):
    def __init__(self, player_id: int):
        self.player = utils.find_player(player_id, status.HTTP_404_NOT_FOUND)
        self.handle_errors()

    def get_response(self) -> UsabilityActionResponse:
        """
        Returns the information of which cards can be played or discarded by the player

        Returns:
        UsabilityInfoResponse: The cards information
        """

        return UsabilityActionResponse(cards=self.get_cards_info())

    def get_cards_info(self) -> list:
        """
        Returns the information of which cards can be played or discarded by the player

        Returns:
        list: The cards information
        """

        cards_info = []
        amount_Infeccion_cards_in_hand = 0
        for cardi in self.player.cards:
            if cardi.name == "Infeccion":
                amount_Infeccion_cards_in_hand += 1

        for card in self.player.cards:
            playable = True
            discardable = True
            if card.name == "Infeccion" or card.name == "La cosa" or self.get_card_type(card.name) == "defense":
                playable = False

            if card.name == "La cosa" or (card.name == "Infeccion" and amount_Infeccion_cards_in_hand == 1 and self.player.role == "infected"):
                discardable = False

            cards_info.append(UsabilityActionInfoCard(
                cardID=card.id,
                name=card.name,
                description=card.description,
                playable=playable,
                discardable=discardable
            ))
        return cards_info

    def get_card_type(self, card_name: str) -> str:
        """
        Returns the type of the card
        """
        with open(settings.DECK_CONFIG_PATH) as config_file:
            config = json.load(config_file)

        return config["cards"][card_name]["type"]

    def handle_errors(self) -> None:
        """
        Checks for errors and raises HTTPException if needed
        """

        exceptions.validate_player_in_game(
            None, self.player, status.HTTP_400_BAD_REQUEST)
        exceptions.validate_player_alive(self.player)


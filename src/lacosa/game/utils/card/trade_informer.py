from fastapi import status
from lacosa import utils
import lacosa.game.utils.exceptions as exceptions
from lacosa.interfaces import ResponseInterface
from lacosa.player.schemas import UsabilityResponse, UsabilityInfoCard


class CardTradeInformer(ResponseInterface):
    def __init__(self, player_id: int):
        self.player = utils.find_player(player_id, status.HTTP_404_NOT_FOUND)
        self.target = utils.find_target_in_trade_event(player_id)
        self.handle_errors()

    def get_response(self) -> UsabilityResponse:
        """
        Returns the information of which cards can be selected to trade with the player

        Returns:
        UsabilityResponse: The cards information
        """

        return UsabilityResponse(cards=self.get_cards_info())

    def get_cards_info(self) -> list:
        """
        Returns the information of which cards can be selected to trade with the player

        Returns:
        list: The cards information
        """

        amount_Infeccion_cards_in_hand = 0
        for cardi in self.player.cards:
            if cardi.name == "Infeccion":
                amount_Infeccion_cards_in_hand += 1

        cards_info = []
        for card in self.player.cards:
            usable = True
            if card.name == "La cosa":
                usable = False
            if card.name == "Infeccion" and amount_Infeccion_cards_in_hand == 1 and self.player.role == "infected":
                usable = False
            if card.name == "Infeccion" and self.target.role == "infected":
                usable = False
            if card.name == "Infeccion" and self.target.role != "human" and self.player.role == "thing":
                usable = False
            if card.name == "Infeccion" and self.player.role == "human":
                usable = False

            cards_info.append(UsabilityInfoCard(
                cardID=card.id,
                name=card.name,
                description=card.description,
                usable=usable
            ))

        return cards_info

    def handle_errors(self) -> None:
        """
        Checks for errors and raises HTTPException if needed
        """

        exceptions.validate_player_in_game(
            None, self.player, status.HTTP_400_BAD_REQUEST)
        exceptions.validate_player_in_game(
            None, self.target, status.HTTP_400_BAD_REQUEST)
        exceptions.validate_player_alive(self.player)
        exceptions.validate_player_alive(self.target)

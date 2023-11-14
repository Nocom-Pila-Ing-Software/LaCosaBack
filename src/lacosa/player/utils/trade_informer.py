from fastapi import status
from lacosa import utils
import lacosa.game.utils.exceptions as exceptions
from lacosa.interfaces import ResponseInterface
from lacosa.player.schemas import UsabilityResponse, UsabilityInfoCard


class CardTradeInformer(ResponseInterface):
    def __init__(self, player_id: int):
        self.player = utils.find_player(player_id, status.HTTP_404_NOT_FOUND)
        self.target = utils.find_target_in_trade_event(player_id)
        self.event = utils.find_partial_event(player_id)
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

        if self.event.card1 is None:
            player = self.event.player1
            target = self.event.player2
        else:
            player = self.event.player2
            target = self.event.player1

        amount_Infeccion_cards_in_hand = 0
        for cardi in player.cards:
            if cardi.name == "Infeccion":
                amount_Infeccion_cards_in_hand += 1

        cards_info = []
        for card in player.cards:
            usable = True

            if card.name == "La cosa":
                usable = False
            if (
                card.name == "Infeccion"
                and amount_Infeccion_cards_in_hand == 1
                and player.role == "infected"
            ):
                usable = False
            if card.name == "Infeccion" and target.role == "infected":
                usable = False
            if (
                card.name == "Infeccion"
                and target.role != "human"
                and player.role == "thing"
            ):
                usable = False
            if (
                card.name == "Infeccion"
                and target.role != "thing"
                and player.role == "infected"
            ):
                usable = False
            if card.name == "Infeccion" and player.role == "human":
                usable = False

            cards_info.append(
                UsabilityInfoCard(
                    cardID=card.id,
                    name=card.name,
                    description=card.description,
                    usable=usable,
                )
            )

        return cards_info

    def handle_errors(self) -> None:
        """
        Checks for errors and raises HTTPException if needed
        """

        exceptions.validate_player_has_game(self.player, status.HTTP_400_BAD_REQUEST)
        exceptions.validate_player_has_game(self.target, status.HTTP_400_BAD_REQUEST)
        exceptions.validate_player_alive(self.player)
        exceptions.validate_player_alive(self.target)

from fastapi import status
from lacosa.player.schemas import PlayerResponse
from lacosa.schemas import PlayerID, CardInfo
from typing import List
import lacosa.utils as utils


def get_player_info(player_id: PlayerID) -> PlayerResponse:
    """
    Get the info of a player

    Args:
    player_id (PlayerID): Input data to validate

    Returns:
    PlayerResponse: The info of the player
    """

    player = utils.find_player(
        player_id, failure_status=status.HTTP_404_NOT_FOUND
    )

    return PlayerResponse(
        hand=get_schemas_from_cards(player.cards),
        role=player.role,
        is_alive=player.is_alive,
        shownCards=get_schemas_from_cards(player.shown_cards),
        playerID=player.id
    )


def get_schemas_from_cards(cards) -> List[CardInfo]:
    """
    Get the list of cards of a player

    Args:
    player_id (PlayerID): Input data to validate

    Returns:
    list[CardInfo]: The list of cards of the player
    """

    card_schemas = [
        get_card_schema(card) for card in cards
    ]

    card_schemas.sort(key=lambda x: x.cardID)

    return card_schemas


def get_card_schema(card) -> CardInfo:
    """
    Get the data of a card

    Args:
    card (Card): The card to get the data from

    Returns:
    CardInfo: The data of the card
    """

    return CardInfo(
        cardID=card.id,
        name=card.name,
        description=card.description
    )
